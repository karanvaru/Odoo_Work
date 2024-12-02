import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time


class GlobalFeedbackInherit(models.Model):
    _inherit = "global.feedback"

    global_feedback_ticket_count = fields.Integer(string="HPI Count", compute="compute_hpi_global_feedback_count")

    @api.multi
    def compute_hpi_global_feedback_count(self):
        for rec in self:
            count_values = self.env['helpdesk.process.improvement'].search_count([('global_feedback_ticket_id', '=', rec.id)])
            rec.global_feedback_ticket_count = count_values

    def action_to_hpi_ticket(self, vals):
        global_feedback_id = self.env['helpdesk.process.improvement']

        vals = {
            'global_feedback_ticket_id': self.id,
        }
        new_val = global_feedback_id.create(vals)
        # self.button_true = True

        return new_val

    def open_hpi_global_feedback_tickets(self):
        self.ensure_one()
        return {

            'name': 'Helpdesk Process Improvement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.process.improvement',
            'domain': [('global_feedback_ticket_id', '=', self.id)],
        }