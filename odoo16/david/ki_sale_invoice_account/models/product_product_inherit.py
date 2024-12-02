# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import timedelta, time
from odoo.tools.float_utils import float_round


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    def _compute_sales_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        date_from = fields.Datetime.to_string(
            fields.datetime.combine(
                fields.datetime.now() - timedelta(days=365),time.min
            )
        )
        domain = [
            ('state', '=', 'posted'),
            ('product_id', 'in', self.ids),
            ('invoice_date', '>=', date_from),
        ]
        for group in self.env['account.invoice.report']._read_group(
            domain,
            ['product_id', 'quantity'], ['product_id']
        ):
            r[group['product_id'][0]] = group['quantity']
        
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            product.sales_count = float_round(
                r.get(product.id, 0),
                precision_rounding=product.uom_id.rounding
            )
        return r

    def action_view_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "ki_sale_invoice_account.action_product_account_invoice_report_all"
        )
        action['domain'] = [('product_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['quantity'],
            'active_id': self._context.get('active_id'),
            'search_default_current': 1,
            'active_model': 'account.invoice.report',
            'search_default_customer': 1,
        }
        return action


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_view_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "ki_sale_invoice_account.action_product_account_invoice_report_all"
        )
        action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['quantity'],
            'active_id': self._context.get('active_id'),
            'search_default_current': 1,
            'active_model': 'account.invoice.report',
            'search_default_customer': 1,
        }
        return action
