import qrcode
import base64
from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContractExtention(models.Model):
    _inherit = "contract.contract"

    sales_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    qr_code = fields.Binary(
        string='QR Code',
        store=True,
        attachment=True,
        compute='qr_code_generate',
    )

    @api.depends('date_start', 'partner_id', 'contract_line_fixed_ids.product_id')
    def qr_code_generate(self):
        qr = qrcode.QRCode(version=3, box_size=10, border=4,
                           error_correction=qrcode.constants.ERROR_CORRECT_L)
        date_start = self.date_start.strftime("%d/%m/%Y")

        msg = """  Customer Name: %s 
Stat Date: %s 
Product Name: %s""" % (self.partner_id.name, date_start,
                                          self.contract_line_fixed_ids[0].product_id.name if self.contract_line_fixed_ids else False)
        qr.add_data(msg)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image

    @api.model
    def create(self, vals):
        res = super(ContractExtention, self).create(vals)

        if len(res.contract_line_fixed_ids.ids) > 1:
            raise ValidationError(_("You cannot add more than one Product for Contract"))

        return res

    def write(self, vals):
        res = super(ContractExtention, self).write(vals)
        if len(self.contract_line_fixed_ids.ids) > 1:
            raise ValidationError(_("You cannot add more than one Product for Contract"))

        return res


