from odoo import models, fields, api
import base64


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def update_closing_control_state_session(self, notes):
        template = self.env.ref('al_pos_close_email.email_tmpl_close_sessions')
        generated_report = self.env['ir.actions.report']._render_qweb_pdf('point_of_sale.sale_details_report',
                                                                          res_ids=[self.id])
        data_record = base64.b64encode(generated_report[0])
        ir_values = {
            'name': 'Pos Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'pos_report.pdf',
            'mimetype': 'application/pdf',
            'res_model': 'pos.session',
        }
        report_attachment = self.env['ir.attachment'].create(ir_values)
        template.attachment_ids = [(4, report_attachment.id)]

        for rec in self.company_id.email_employee_ids:
            template.send_mail(rec.id)
        template.attachment_ids = [(5, 0, 0)]

        data = super(PosSessionInherit, self).update_closing_control_state_session(notes)
        return data
