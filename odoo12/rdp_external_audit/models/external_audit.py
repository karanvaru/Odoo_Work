# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import string
from unicodedata import category, name
from odoo import api, fields, models, _
from datetime import date, datetime
import time
from odoo.http import request



class ExternalAudit(models.Model):

    _name = "external.audit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "External Audit"


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'DRAFT'), 
        ('wip','WIP'),
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),

    ], string='Status', readonly=True, default='draft',track_visibility='always')
    open_days = fields.Char(string="Opendays",compute="compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    cancelled_date = fields.Datetime('Cancelled Date')
    description = fields.Text('Description',track_visibility='always')
    # employee_name = fields.Char('Assigned By',readonly="True")
    internal_notes = fields.Html(string='Internal Notes',track_visibility='always')
    related_month_ids = fields.Many2many('externalaudit.related',string="Related Month")
    transaction_type_ids = fields.Many2many('externalaudit.transactiontype',string="Transaction Type")
    subject = fields.Char('Subject',track_visibility='always')
    
  
    


    @api.model
    def create(self, vals):
            vals.update({
                'name' : self.env['ir.sequence'].next_by_code('external.audit.sequence'),
               
            })
           
            return super(ExternalAudit, self).create(vals)
    
    
    @api.multi
    def action_to_wip(self):
        self.state = 'wip'


    def action_to_closed(self):
        self.closed_date = datetime.today() 
        self.state = 'closed'
        
         
       
    @api.multi
    def action_to_cancel(self):
        self.cancelled_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})
    

    @api.depends('cancelled_date')
    def compute_open_days(self):
        for record in self:
            if record['closed_date']:
                record['open_days'] = str((record['closed_date'] - record['create_date']).days) + " Days"
            else:
                record['open_days'] = str((datetime.today() - record['create_date']).days) + " Days"

            record['open_days'] = record['open_days'].split(',')[0]
            if record['open_days'] == '0:00:00':
                record['open_days'] = '0 Days'

    


class ExternalAuditRelatedMonth(models.Model):

    _name = "externalaudit.related"
    _description = "External Audit Related Month"   


    name = fields.Char('Name')   

class ExternalAuditTransactionType(models.Model):

    _name = "externalaudit.transactiontype"
    _description = "External Audit Transaction Type"   


    name = fields.Char('Name') 

   
   


   
                                   

   














