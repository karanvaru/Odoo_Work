from odoo import models, fields, api, _
import base64
import requests
import xlrd
from odoo.tools import mute_logger, pycompat
import io
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ImportProduct(models.Model):
    _name = "import.product.wizard"
    _description = "Import product"
    _rec_name = 'shop_id'

    file_name = fields.Binary(
        string="File Name"
    )
    filename = fields.Char(
        string="File name",
        readonly=False,
    )
    # samples_file = fields.Binary(
    #     string="Samples Import Format",
    #     readonly=False,
    # )
    # samples_file_name = fields.Char(
    #     string="Samples Import name",
    #     readonly=True,
    # )

    failed_count = fields.Integer(
        string="Fail Count"
    )
    success_count = fields.Integer(
        string="Success Count"
    )
    failed_order = fields.Text(
        string="Fail Order"
    )
    user_id = fields.Many2one(
        'res.users',
        string="Upload By User"
    )
    upload_date = fields.Datetime(
        string="Upload Date"
    )
    shop_id = fields.Many2one(
        'sale.shop',
        string="Shop"
    )

    # @api.model
    # def default_get(self, default_fields):
    #     values = super().default_get(default_fields)
    #     active_id = self._context.get('active_id', False)
    #     sample_file = self.env['attachment.sample.file'].search([
    #         ('shop_id', '=', active_id),
    #         ('file_type', '=', 'product')
    #     ], limit=1)
    #     if sample_file:
    #         values.update({
    #             'samples_file':sample_file.file,
    #             'samples_file_name':sample_file.file_name
    #         })
    #     return values

    def download_sample(self):
        self.ensure_one()
        lines_id = self.env['attachment.sample.file'].search([
            ('shop_id', '=', self.shop_id.id),
            ('file_type', '=', 'product')
        ], limit=1)
        if lines_id.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=ir.attachment&id=" + str(
                    lines_id.attachment_id.id)+ "&filename_field=name&field=datas&download=true&name=" + lines_id.attachment_id.name
            }

    def import_product(self):
        active_id = self._context.get('active_id', False)
        if self.filename:
            if not self.filename.endswith('.csv'):
                raise ValidationError(_('File must be in .csv format!'))

        csv_data = False
        try:
            csv_data = base64.decodebytes(self.file_name)
            _logger.info("Upload File____________")
        except:
            pass
        if not csv_data:
            _logger.info("Not Upload File____________")
            template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
            if template_id:
                template = self.env['mail.template'].browse(template_id).id
                email_values = {
                    'message': 'Csv Reading Issue'
                }
                template.with_context(email_values).send_mail(self.id, force_send=True, email_values=email_values)

        reader = False
        try:
            reader = pycompat.csv_reader(io.BytesIO(csv_data), delimiter=',', quotechar='"')
            _logger.info("Read File____________")
        except:
            pass
        if not reader:
            _logger.info("Not Read File____________")
            template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
            if template_id:
                template = self.env['mail.template'].browse(template_id).id
                email_values = {
                    'message': 'Csv Reading Issue'
                }
                template.with_context(email_values).send_mail(self.id, force_send=True, email_values=email_values)
        headers = []
        try:
            for r in reader:
                headers = r
                break
        except:
            template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
            if template_id:
                template = self.env['mail.template'].browse(template_id).id
                email_values = {
                    'message': 'headers Reading Issue'
                }
                template.with_context(email_values).send_mail(self.id, force_send=True, email_values=None)
            return
        lines = []
        data = []
        for i in reader:
            data.append(i)
        for i in headers:
            res = self.env['ir.model.fields'].search(
                [('model_id.model', '=', 'sale.shop.product'), ('field_description', '=', i)])
            vals = {'excel_head': i}
            if res:
                vals.update({'field_id': res.id})
            lines.append((0, 0, vals))
        wizard_id = self.env['excel.header.mapping.wizard'].create(
            {'lines_ids': lines, 'shop_id': self.shop_id.id})
        # print("self_id",self.id)
        return {
            'name': 'Upload Product',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'excel.header.mapping.wizard',
            'res_id': wizard_id.id,
            'target': 'new',
            'context': {'data': data, 'product_wizard_id': self.id}
        }

