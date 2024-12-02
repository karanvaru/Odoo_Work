from odoo import models, fields, api


class RaiseQueryWizard(models.TransientModel):
    _name = "raise.query.wizard"

    description = fields.Text(
        string="Description"
    )

    def action_apply(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        query = self.env[active_model].browse(active_id)
        query.message_post(body=self.description)
        query.update({
            'state': 'query',
            'qry_sub_date': fields.Date.context_today(self),
        })
