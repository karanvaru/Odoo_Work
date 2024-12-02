import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time


class SalesChallengeInherit(models.Model):
    _inherit = "sale.challenge"

    hpi_sales_challenge_ticket_count = fields.Integer(string="HPI Count", compute="compute_hpi_sales_challenge_count")
    hdpi_button_yes = fields.Char(string="HDPI", compute="compute_hdpi_button_action")

    @api.multi
    def compute_hpi_sales_challenge_count(self):
        for rec in self:
            count_values = rec.env['helpdesk.process.improvement'].search_count([('sales_challenge_ticket_id', '=', rec.id)])
            rec.hpi_sales_challenge_ticket_count = count_values

    def action_to_hpi_ticket(self, vals):
        hpi_sales_challenge_id = self.env['helpdesk.process.improvement']

        vals = {
            'sales_challenge_ticket_id': self.id,
        }
        new_val = hpi_sales_challenge_id.create(vals)
        # self.button_true = True

        return new_val

    def open_hpi_sales_challenge_tickets(self):
        self.ensure_one()
        return {

            'name': 'Helpdesk Process Improvement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.process.improvement',
            'domain': [('sales_challenge_ticket_id', '=', self.id)],
        }

    @api.depends('hpi_sales_challenge_ticket_count')
    def compute_hdpi_button_action(self):
        for rec in self:
            if rec.hpi_sales_challenge_ticket_count != 0:
                rec.hdpi_button_yes = "Yes"