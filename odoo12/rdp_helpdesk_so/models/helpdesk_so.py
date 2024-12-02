# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class HelpdeskSOReference(models.Model):
    _inherit = 'helpdesk.ticket'

    so_reference = fields.Many2one('sale.order', string="SO Reference", compute='compute_so_in_helpdesk')
    ################studio_to_code#################
    # serial_no = fields.Char(string="Serial No.")
    bill_date = fields.Date(string="Bill Date")
    scope = fields.Selection(
        [("In-scope", "In-Scope"),
         ("AMS Scope", "AMS Scope"),
         ("Out-of-scope", "Out-of-Scope"),
         ("Other", "Other")
         ], string="Scope")
    helpdesk_partner_id = fields.Many2one('res.partner', string="Partner")
    sales_channel = fields.Selection([("GeM (P1)", "GeM (P1)"),
                                      ("Corporate (P2)", "Corporate (P2)"),
                                      ("eCommerce (P3)", "eCommerce (P3)"),
                                      ("RDP", "RDP"),
                                      ("Other", "Other")
                                      ], string="Sales Channel")
    attached_os = fields.Selection(
        [("Linux", "Linux"),
         ("Windows11 Home", "Windows11 Home"),
         ("Windows11 Pro", "Windows11 Pro"),
         ("Windows10 Home", "Windows10 Home"),
         ("Windows10 Pro", "Windows10 Pro"),
         ("Windows10 IOT", "Windows10 IOT"),
         ("Windows8 Embedded", "Windows8 Embedded"),
         ("Windows7 Embedded", "Windows7 Embedded"),
         ("Windows7", "Windows7"),
         ("Others", "Others"),
         ("NA", "NA")
         ], string="Attached OS")

    @api.multi
    def compute_so_in_helpdesk(self):
        for rec in self:
            # helpdesk_serial_no = rec.x_studio_serial_no
            # if helpdesk_serial_no:
            #     lot_ref = self.env['stock.move.line'].search([('lot_id', '=', rec.x_studio_serial_no)])
                lot_ref = self.env['stock.move.line'].search([])
                for lr in lot_ref:
                    stock_ref = lr.reference

                    stock_picking_ref = self.env['stock.picking'].search([('name', '=', stock_ref)])
                    for sr in stock_picking_ref:
                        source_doc_ref = sr.origin
                        if source_doc_ref:
                            if 'SO' in source_doc_ref:
                                sale_order = self.env['sale.order'].search([('name', '=', source_doc_ref)])

                                for so in sale_order:
                                    rec.so_reference = so.id

# class HelpdeskSaleOrder(models.Model):

#     _inherit = 'stock.production.lot'

#     stock_pick = fields.Many2one('sale.order', 'Stock pick')
