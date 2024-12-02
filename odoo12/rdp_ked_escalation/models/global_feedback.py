
import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time



class GlobalFeedback(models.Model):
    _inherit ="global.feedback"

    gf_ked_ticket_count = fields.Integer(string="GF KED Ticket Count",compute="compute_gf_ked_count")
    # ked_ticket_id = fields.Many2one('ked.escalation','KED Ticket', compute="compute_gf_ked_ticket")
    # ked_status = fields.Selection(string='KED status', related="ked_ticket_id.state",store=True)
    # kam_delay_days = fields.Char(string="KED Delay Days",related="ked_ticket_id.delay_days")
    # source = fields.Selection([
    #     ('website', 'Website'), 
    #     ('email', 'Email'),
    #     ('chatbot', 'Chatbot'),
    #     ('ivrs', 'IVRS'),
    #     ('other', 'Other'),


    # ], string='Source Document',track_visibility='always')

  
        
    @api.multi
    def compute_gf_ked_count(self):
        for rec in self:
            count_values = self.env['ked.escalation'].search_count([('global_feedback_id','=',rec.id)])
            rec.gf_ked_ticket_count = count_values


    def action_to_gf_ked_ticket(self, vals):
        ked_gf_id = self.env['ked.escalation']
        vals = {
            'global_feedback_id': self.id,
        }
        new_val = ked_gf_id.create(vals)
        return new_val


    def open_gf_ked_tickets(self):

            self.ensure_one()
            return {
                'name': 'KED Escalation',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'ked.escalation',
                'domain': [('global_feedback_id','=',self.id)],
            }


    # @api.multi
    # def compute_ked_ticket(self):
    #     for rec in self:
    #         ked_id = self.env['ked.escalation'].search([('helpdesk_ticket_fed_id','=',rec.id)])
    #         for k_id in ked_id:
    #             rec.ked_ticket_id = k_id.id
    # @api.multi
    # def compute_ked_status(self):
    #     for rec in self:
    #         rec.ked_status = rec.ked_ticket_id.state  