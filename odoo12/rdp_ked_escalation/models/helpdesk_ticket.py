
import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time



class HelpdeskTicketKED(models.Model):
    _inherit ="helpdesk.ticket"

    ked_ticket_count = fields.Integer(string="KED Ticket Count",compute="compute_ked_count")
    ked_ticket_id = fields.Many2one('ked.escalation','KED Ticket', compute="compute_ked_ticket")
    ked_status = fields.Selection(string='KED status', related="ked_ticket_id.state",store=True)
    kam_delay_days = fields.Char(string="KED Delay Days",related="ked_ticket_id.delay_days")
    source = fields.Selection([
        ('website', 'Website'), 
        ('email', 'Email'),
        ('chatbot', 'Chatbot'),
        ('ivrs', 'IVRS'),
        ('other', 'Other'),


    ], string='Source Document',track_visibility='always')

  
        
    @api.multi
    def compute_ked_count(self):
        for rec in self:
            count_values = self.env['ked.escalation'].search_count([('helpdesk_ticket_fed_id','=',rec.id)])
            rec.ked_ticket_count = count_values


    def action_to_ked_ticket(self, vals):
        ked_helpdesk_id = self.env['ked.escalation']
        vals = {
            'helpdesk_ticket_fed_id': self.id,
        }
        new_val = ked_helpdesk_id.create(vals)
        return new_val


    def open_ked_tickets(self):

            self.ensure_one()
            return {
                'name': 'KED Escalation',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'ked.escalation',
                'domain': [('helpdesk_ticket_fed_id','=',self.id)],
            }


    @api.multi
    def compute_ked_ticket(self):
        for rec in self:
            ked_id = self.env['ked.escalation'].search([('helpdesk_ticket_fed_id','=',rec.id)])
            for k_id in ked_id:
                rec.ked_ticket_id = k_id.id
    @api.multi
    def compute_ked_status(self):
        for rec in self:
            rec.ked_status = rec.ked_ticket_id.state            