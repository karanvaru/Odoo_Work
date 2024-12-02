# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class WarrantyHistory(models.Model):
    _name = 'warranty.history'
    _description = "Warranty Renewal"
    _order = 'create_date desc, id desc'


    """ @api.one
    def _compute_invoice(self):
        orderObj = self.warranty_id.order_id
        self.write({
            'invoice_id' : orderObj.invoice_ids and orderObj.invoice_ids[0].id or False,
            'state' : self.warranty_id.state
        }) """

    name = fields.Char(
        string='Reference', readonly=True)
    is_fresh = fields.Boolean(
        string="Fresh Records", default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled')], string="State")
    invoice_id = fields.Many2one(
        'account.invoice', string="Invoice", readonly=True)#, compute='_compute_invoice'
    warranty_id = fields.Many2one(
        'warranty.registration', string="Warranty", readonly=True)
    old_start_date = fields.Date(string="Start Date", readonly=True)
    old_end_date = fields.Date(string="End Date", readonly=True)
    datas = fields.Binary(string='File Content')


    @api.multi
    def donwload_pdf(self):
        self.ensure_one()
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/wnty_dwnld?name={}&field=datas&id={}'.format(self.name, self.id),
            'target': 'self',
        }