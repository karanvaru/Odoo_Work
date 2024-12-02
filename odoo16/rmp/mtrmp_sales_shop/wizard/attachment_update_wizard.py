from odoo import models, fields, api


class AttachmentUpdateWizard(models.TransientModel):
    _name = "attachment.update.wizard"
    _description = "Attachment Update or Create Wizard"

    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string="File name", readonly=False)

    def create_update_attachment(self):
        active_id = self._context.get('active_id', False)
        vals = {
            'name': self.file_name,
            'datas': self.file,
            'res_model': 'attachment.sample.file',
            'res_id': active_id,
        }
        attachment_id = self.env["ir.attachment"].create(vals)
        lines_id = self.env['attachment.sample.file'].browse(active_id)
        if lines_id.attachment_id:
            lines_id.attachment_id = False
            lines_id.attachment_id = attachment_id.id
        else:
            lines_id.attachment_id = attachment_id.id
