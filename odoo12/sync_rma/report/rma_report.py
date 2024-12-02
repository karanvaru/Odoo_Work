# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools


AVAILABLE_PRIORITIES = [
   ('0', 'All'),
   ('1', 'Low Priority'),
   ('2', 'High Priority'),
   ('3', 'Urgent')
]


class RmaReport(models.Model):
    """ RMA Report """
    _name = "rma.report"
    _auto = False
    _description = "RMA Report"

    name = fields.Char(string='Name')
    issue_date = fields.Datetime(string='Date')
    location_id = fields.Many2one('stock.location', string="Source Location")
    location_dest_id = fields.Many2one('stock.location', string="Destination Location")
    partner_id = fields.Many2one('res.partner', string='Customer')
    subject = fields.Char(string="Subject")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority')
    associated_so = fields.Many2one('sale.order', string='Sale Order')
    user_id = fields.Many2one('res.users', string='Responsible')
    state = fields.Selection([('draft', 'Draft'),
                            ('confirm', 'Confirmed'),
                            ('approve', 'Approved'),
                            ('cancel', 'Cancelled'),
                            ('reject', 'Reject'),
                            ('done', 'Done')], string='Status')
    order_id = fields.Many2one('rma.issue', string='Issue Reference')
    product_id = fields.Many2one('product.product', string='Product')
    qty_delivered = fields.Float(string='Delivered Qty')
    to_return = fields.Float(string='Return Qty')
    return_type_id = fields.Many2one('return.type', string="Return Type")
    repair_id = fields.Many2one('repair.order', string="Repair")
    sale_id = fields.Many2one('sale.order', string="Replace Sale")
    invoice_id = fields.Many2one('account.invoice', string="Credit Memo")

    def _select(self):
        select_str = """
            SELECT
                    min(l.id) as id,
                    l.order_id as order_id,
                    l.product_id as product_id,
                    l.qty_delivered,
                    l.to_return,
                    l.return_type_id as return_type_id,
                    l.repair_id as repair_id,
                    l.sale_id as sale_id,
                    l.invoice_id as invoice_id,
                    s.name,
                    s.subject as subject,
                    s.location_id as location_id,
                    s.location_dest_id as location_dest_id,
                    s.partner_id as partner_id,
                    s.issue_date as issue_date,
                    s.priority as priority,
                    s.user_id as user_id,
                    s.associated_so as associated_so,
                    s.state as state
        """
        return select_str

    def _from(self):
        from_str = """
            FROM
                rma_issue_line l
                    join rma_issue s on (l.order_id = s.id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY s.name,s.subject,s.location_id,s.location_dest_id,s.priority,s.user_id,
                s.partner_id,s.issue_date,s.associated_so,s.state,l.order_id,
                    l.product_id,l.qty_delivered,l.to_return,l.return_type_id,l.repair_id,l.sale_id,l.invoice_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                %s %s %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
