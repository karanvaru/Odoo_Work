import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time


class AspAppInherit(models.Model):
    _inherit = "asp.partner"

    hpi_asp_ticket_count = fields.Integer(string="HPI Count", compute="compute_hpi_asp_count")

    @api.multi
    def compute_hpi_asp_count(self):
        for rec in self:
            count_values = self.env['helpdesk.process.improvement'].search_count([('asp_ticket_id', '=', rec.id)])
            rec.hpi_asp_ticket_count = count_values

    def action_to_hpi_ticket(self, vals):
        hpi_asp_id = self.env['helpdesk.process.improvement']

        vals = {
            'asp_ticket_id': self.id,
        }
        new_val = hpi_asp_id.create(vals)
        # self.button_true = True

        return new_val

    def open_hpi_asp_tickets(self):
        self.ensure_one()
        return {

            'name': 'Helpdesk Process Improvement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.process.improvement',
            'domain': [('asp_ticket_id', '=', self.id)],
        }