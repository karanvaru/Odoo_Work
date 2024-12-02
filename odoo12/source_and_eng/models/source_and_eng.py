# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SourcingEngineering(models.Model):
    _name = "source.eng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sourcing & Engineering'


    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
    # state = fields.Selection([
    #     ('new', 'NEW'),
    #     ('wip', 'WIP'),
    #     ('hold', 'Hold'),
    #     ('closed', 'CLOSED'),
    #     ('cancel', 'Cancelled'),
    #
    # ], string='Status', default='new')

    se_name = fields.Char('SE Name',store=True,track_visibility='onchange')
    se_desc = fields.Text('SE Description',store=True,track_visibility='onchange')
    lead_opp = fields.Many2one('crm.lead', 'Lead/Opportunity', store=True)
    saleorder = fields.Many2one('sale.order','Sales Order', store='true')
    assigned_to = fields.Many2one('res.users', 'Assigned To', store=True, domain="[('is_int_user','=',True)]",track_visibility='onchange')
    se_type = fields.Selection([
        ('proactive', 'Proactive'),
        ('reactive', 'Reactive'),
        ('other', 'Other'),
    ], string='SE Type')
    se_catagory = fields.Selection([
        ('engineering', 'Engineering'),
        ('sourcing', 'Sourcing'),
        ('business', 'Business'),
        ('Other', 'Other'),
    ], string='PLM Benz')

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('source.eng.sequence'),
		})
        return super(SourcingEngineering, self).create(vals)
