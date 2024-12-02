from odoo import api, fields, models, _
import qrcode
import base64
from io import BytesIO


class ContractLineEdit(models.Model):
    _inherit = "contract.line"

    qr_code = fields.Binary(
        string='QR Code',
        store=True,
        attachment=True,
        compute='qr_code_generate',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Model',
    )
    department = fields.Char(
        string='Department'
    )
    barcode = fields.Char(
        string='Barcode'
    )
    categ_id = fields.Many2one(
        'product.category',
        string='Model Type'
    )
    default_code = fields.Char(
        string='Asset Number'
    )
    name = fields.Text(
        required=False
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Location',
    )
    state_tree = fields.Selection([
        ('active', 'Activate'),
        ('expire', 'Expired'),
        ('terminate', 'Terminate')
    ], string='Status')

    comment = fields.Text(
        string='Terminate Reason',
        readonly=True,
    )

    @api.onchange('categ_id')
    def categ_id_onchange(self):
        return {'domain': {'product_id': [('categ_id', '=', self.categ_id.id)]}}

    @api.onchange('partner_shipping_id')
    def onchange_partner_shipping_id(self):
        if self.contract_id.partner_shipping_id:
            self.partner_shipping_id = self.contract_id.partner_shipping_id.id

    @api.onchange('product_id')
    def product_onchange(self):
        if self.product_id:
            if self.product_id.barcode:
                self.barcode = self.product_id.barcode
            if self.product_id.default_code:
                self.default_code = self.product_id.default_code

    @api.depends('product_id', 'default_code')
    def qr_code_generate(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if rec.default_code:
                qr = qrcode.QRCode(version=3, box_size=10, border=4,
                                   error_correction=qrcode.constants.ERROR_CORRECT_L)
                if rec.contract_id.state != 'active':
                    return False
                else:
                    msg = "%s/new/ticket?ProductNumber=%s" % (base_url, rec.default_code)
                    qr.add_data(msg)
                    qr.make(fit=True)
                    img = qr.make_image()
                    temp = BytesIO()
                    img.save(temp, format="PNG")
                    qr_image = base64.b64encode(temp.getvalue())
                    rec.qr_code = qr_image

    def action_terminates(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract Terminate',
            'res_model': 'contract.terminate.entry.wizard',
            'view_mode': 'form',
            'target': 'new',
        }