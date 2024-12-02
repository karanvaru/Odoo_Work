# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class HelpdeskInwardExtend(models.Model):

    _inherit = 'helpdesk.ticket'
    # _description = 'Helpdesk Inward Extend'

    helpdesk_inward_date = fields.Datetime('Inward Opendays',compute="compute_inward_date",store="True")
    helpdesk_outward_date = fields.Datetime('Out Opendays',compute="compute_delivery_date",store="True")
    helpdesk_inward_days = fields.Char('Inward Opendays', compute="compute_inward_opendays")
    
    @api.depends('stage_id')
    @api.multi
    def compute_inward_date(self):
        for cio in self:
            h_ticket = cio.id
            if h_ticket:
                rma_lines = self.env['rma.issue'].search([('ticket_id.id','=',h_ticket)])
                if rma_lines:
                    for rl in rma_lines:
                        rid= rl.id
                        if rid:
                            rma_issue_pickup =self.env['stock.picking'].search([('rma_issue_id','=',rid),('picking_type_code','=','incoming')])
                            if rma_issue_pickup:
                                for rma_stock in rma_issue_pickup:
                                    if rma_stock.date_done:

                                        cio.helpdesk_inward_date = rma_stock.date_done

    @api.depends('stage_id')
    @api.multi
    def compute_delivery_date(self):
        for cio in self:
            h_ticket = cio.id
            if h_ticket:
                rma_lines = self.env['rma.issue'].search([('ticket_id.id','=',h_ticket)])
                if rma_lines:
                    for rl in rma_lines:
                        rid= rl.id
                        if rid:
                            rma_issue_delivery =self.env['stock.picking'].search([('rma_issue_id','=',rid),('picking_type_code','=','outgoing')])
                            if rma_issue_delivery:
                                for rma_stock in rma_issue_delivery:
                                    if rma_stock.date_done:

                                        cio.helpdesk_outward_date = rma_stock.date_done  
    @api.multi
    @api.depends('helpdesk_inward_date','helpdesk_outward_date')
    def compute_inward_opendays(self):
        for rec in self:
            if not rec.helpdesk_inward_date:
                rec.helpdesk_inward_days == "0"
            if rec.helpdesk_inward_date and rec.helpdesk_outward_date:
                rec.helpdesk_inward_days = str((rec.helpdesk_outward_date - rec.helpdesk_inward_date).days) 
            if rec.helpdesk_inward_date and not rec.helpdesk_outward_date:
                rec.helpdesk_inward_days = str((datetime.today() - rec.helpdesk_inward_date).days)      


            
        




                                    







 
  
