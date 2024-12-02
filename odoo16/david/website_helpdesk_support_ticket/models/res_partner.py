# -*- coding: utf-8 -*

from odoo import models, fields, api

class CustomerPrice(models.Model):
    _inherit = 'res.partner'

    product_id_helpdesk = fields.Many2one(
        'product.product',
        string='Product',
    )
    
#    @api.multi odoo13
    @api.depends('ticket_ids')
    def _ticket_count(self):
        #for rec in self:
        #    rec.ticket_count = len(rec.ticket_ids)
        helpdesk_support = self.env['helpdesk.support']
#        for record in self:
#            record.ticket_count = helpdesk_support.search_count([('partner_id', 'child_of', record.id)])
        try:
            for record in self:
                try:
                    record.ticket_count = helpdesk_support.search_count([('partner_id', 'child_of', record.id)])
                except:
                    pass
        except:
            pass
        
        
    price_rate = fields.Float(
        string='Price / Rate (Company Currency)',
        default=0.0,
        copy=False,
    )
    ticket_count = fields.Integer(
        compute = '_ticket_count',
        store=True,
    )
    ticket_ids = fields.One2many(
        'helpdesk.support',
        'partner_id',
        string='Helpdesk Ticket',
        readonly=True,
    )
     
#    @api.multi odoo13
    def show_ticket(self):
#        for rec in self:
        self.ensure_one()
        # res = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        # res['domain'] = str([('partner_id','child_of',self.id)])
        res['domain'] = str([('partner_id','=',self.id)])
        return res
