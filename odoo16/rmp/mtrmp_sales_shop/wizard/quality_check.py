from odoo import models, fields, api


class QualityCheck(models.TransientModel):
    _name = "quality.check.wizard"
    _description = "Quality Check Wizard"

    quality_type = fields.Selection([('ok', 'OK'), ('not_ok', 'NotOk')], string="Quality Type",required=True)
    comment = fields.Text(string="Description", required=True)

    def record_submit(self):
        active_ids = self.env.context.get('active_ids', [])
        ticket_record = self.env['shop.order.ticket'].browse(active_ids)
        ticket_record.update({
            'quality_type': self.quality_type,
            'comment': self.comment,
            'state': 'qa'
        })
