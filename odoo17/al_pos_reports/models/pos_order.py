# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.order'

    total_qty = fields.Float(
        string="Total Qty",
        compute="_compute_total_qty",
        store=True
    )
    source_order_id = fields.Many2one(
        'pos.order',
        string="Source Order",
        compute="_compute_relation",
        store=True
    )
    source_name = fields.Char(
        string='Order Ref Sold',
        related="source_order_id.name",
        store=True
    )
    source_account_move = fields.Many2one(
        string='Invoice Sold',
        related="source_order_id.account_move",
        store=True
    )
    source_pos_reference = fields.Char(
        string='Receipt Number Sold',
        related="source_order_id.pos_reference",
        store=True
    )
    source_user_id = fields.Many2one(
         string='Responsible Sold',
        related="source_order_id.user_id",
        store=True
    )
    source_date_order = fields.Datetime(
        string='Date Sold',
        related="source_order_id.date_order",
        store=True
    )
    source_partner_id = fields.Many2one(
        string='Customer Sold',
        related="source_order_id.partner_id",
        store=True
    )
    source_total_qty = fields.Float(
        string="Total Qty Sold",
        related="source_order_id.total_qty",
        store=True
    )
    source_amount_paid = fields.Float(
        string='Paid Sold',
        related="source_order_id.amount_paid",
        store=True
    )
    source_config_id = fields.Many2one(
        related='source_order_id.config_id',
        string="Point of Sale Sold",
        store=True
    )
    total_diff = fields.Float(
        string="Total Diff",
        compute="_compute_total_diff",
        store=True
    )

    @api.depends(
        'source_order_id',
        'source_order_id.amount_paid',
        'amount_paid'
    )
    def _compute_total_diff(self):
        for order in self:
            order.total_diff = 0
            if order.source_order_id:
                order.total_diff = order.source_order_id.amount_paid - abs(order.amount_paid)

    @api.depends('lines', 'lines.qty')
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(l.qty for l in order.lines)
    
    @api.depends(
        'amount_total',
        'lines.refunded_orderline_id',
        'lines.refund_orderline_ids'
    )
    def _compute_relation(self):
        for order in self:
            order.source_order_id = False
            if order.amount_total < 0:
                refunded_order_ids = order.mapped('lines.refunded_orderline_id.order_id')
                if refunded_order_ids:
                    order.source_order_id = refunded_order_ids[0].id
