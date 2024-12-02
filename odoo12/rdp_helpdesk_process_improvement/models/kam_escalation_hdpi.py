import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time


class HdpiKamEscalationInherit(models.Model):
    _inherit = "ked.escalation"

    hpi_kam_escalation_ticket_count = fields.Integer(string="HPI Count", compute="compute_hpi_count")

    @api.multi
    def compute_hpi_count(self):
        for rec in self:
            count_values = self.env['helpdesk.process.improvement'].search_count([('kam_escalation_ticket_id', '=', rec.id)])
            rec.hpi_kam_escalation_ticket_count = count_values

    def action_to_hpi_ticket(self, vals):
        hpi_kam_escalation_id = self.env['helpdesk.process.improvement']

        vals = {
            'kam_escalation_ticket_id': self.id,
        }
        new_val = hpi_kam_escalation_id.create(vals)
        # self.button_true = True

        return new_val

    def open_hpi_kam_escalation_tickets(self):
        # self.ensure_one()
        return {

            'name': 'Helpdesk Process Improvement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.process.improvement',
            'domain': [('kam_escalation_ticket_id', '=', self.id)],
        }