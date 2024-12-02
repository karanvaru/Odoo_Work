from odoo import models, fields, api


class RaiseIssue(models.TransientModel):
    _name = "raise.issue.wizard"
    _description = "Raise Issue Wizard"

    raise_comment = fields.Text(string="Description", required=True)

    def record_raise_submit(self):
        active_ids = self.env.context.get('active_ids', [])
        ticket_record = self.env['shop.order.ticket'].browse(active_ids)
        ticket_record.update({
            'raise_comment': self.raise_comment,
            'state': 'issue'
        })
