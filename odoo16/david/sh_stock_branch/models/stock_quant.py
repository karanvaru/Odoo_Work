# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

import logging

from psycopg2 import Error

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class StockQuantBranch(models.Model):
    _inherit = 'stock.quant'

    branch_id = fields.Many2one(
        'res.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    @api.model
    def _merge_quants(self):
        """ In a situation where one transaction is updating a quant via
        `_update_available_quantity` and another concurrent one calls this function with the same
        argument, we’ll create a new quant in order for these transactions to not rollback. This
        method will find and deduplicate these quants.
        """
        query = """WITH
                        dupes AS (
                            SELECT min(id) as to_update_quant_id,
                                (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)] as to_delete_quant_ids,
                                SUM(reserved_quantity) as reserved_quantity,
                                SUM(inventory_quantity) as inventory_quantity,
                                SUM(quantity) as quantity,
                                MIN(in_date) as in_date
                            FROM stock_quant
                            GROUP BY product_id, company_id, location_id, lot_id, package_id, owner_id, branch_id
                            HAVING count(id) > 1
                        ),
                        _up AS (
                            UPDATE stock_quant q
                                SET quantity = d.quantity,
                                    reserved_quantity = d.reserved_quantity,
                                    inventory_quantity = d.inventory_quantity,
                                    in_date = d.in_date
                            FROM dupes d
                            WHERE d.to_update_quant_id = q.id
                        )
                   DELETE FROM stock_quant WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
        """
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(query)
                self.env.invalidate_all()
        except Error as e:
            _logger.info('an error occurred while merging quants: %s', e.pgerror)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)

        domain = [('product_id', '=', product_id.id)]
        domain = expression.AND(
            [[('branch_id', '=', self.env.user.branch_id.id)], domain])
        if not strict:
            if lot_id:
                domain = expression.AND([['|', ('lot_id', '=', lot_id.id), ('lot_id', '=', False)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            domain = expression.AND([[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([['|', ('lot_id', '=', lot_id.id), ('lot_id', '=', False)] if lot_id else [('lot_id', '=', False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])

        return self.search(domain, order=removal_strategy_order).sorted(lambda q: not q.lot_id)

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_create()
        res += ['branch_id']
        return res
