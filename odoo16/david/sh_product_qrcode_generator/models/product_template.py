# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv import expression

from io import BytesIO
import base64

try:
    import qrcode
except ImportError:
    qrcode = None


class ShProductTemplate(models.Model):
    _inherit = "product.template"

    sh_qr_code = fields.Char(
        string="QR Code", related='product_variant_ids.sh_qr_code', readonly=False)
    sh_qr_code_img = fields.Binary(
        string="QR Code Image", readonly=False, compute='_compute_sh_qr_code_1')

    def sh_action_open_label_layout_with_qr(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sh_product_qrcode_generator.sh_action_open_label_layout_with_qr')
        action['context'] = {'default_product_tmpl_ids': self.ids}
        return action

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super(ShProductTemplate, self)._name_search(
            name, args, operator, limit, name_get_uid)
        if not result:
            if not args:
                args = []
            domain = [('sh_qr_code', '=', name)]
            domain = expression.AND([args, domain])
            result = list(self._search(
                domain, limit=limit, access_rights_uid=name_get_uid))
        return result

    @ api.constrains('sh_qr_code')
    def _validate_qrcode(self):
        for template in self:
            if template.sh_qr_code:
                products = self.env['product.template'].search(
                    [('id', '!=', template.id), ('sh_qr_code', '=', template.sh_qr_code)])
                if products:
                    raise ValidationError("QR code must be unique !")

    @ api.model_create_multi
    def create(self, vals_list):
        res = super(ShProductTemplate, self).create(vals_list)
        is_create_qr_code = self.env['ir.config_parameter'].sudo().get_param(
            'sh_product_qrcode_generator.is_sh_product_qrcode_generator_when_create')
        if is_create_qr_code:
            for template in res:
                qr_sequence = self.env['ir.sequence'].next_by_code(
                    'seq.sh_product_qrcode_generator')
                if qr_sequence:
                    qr_code = qr_sequence
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_code)
                    qr.make(fit=True)

                    img = qr.make_image()
                    temp = BytesIO()
                    img.save(temp, format="PNG")
                    qr_code_image = base64.b64encode(temp.getvalue())

                    template.sh_qr_code = qr_code
                    template.sh_qr_code_img = qr_code_image

        # Necessary if enter qr code in product template and only 1 variant than should work vice versa
        for vals in vals_list:
            if vals.get("sh_qr_code", False):
                sh_qr_code = vals.get("sh_qr_code")
                if res and res.product_variant_id:
                    res.product_variant_id.sh_qr_code = sh_qr_code
        return res

    @api.depends('sh_qr_code')
    def _compute_sh_qr_code_1(self):
        if self:
            for rec in self:
                rec.sh_qr_code_img = False
                if rec.sh_qr_code:
                    qr_code = rec.sh_qr_code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_code)
                    qr.make(fit=True)
                    img = qr.make_image()
                    temp = BytesIO()
                    img.save(temp, format="PNG")
                    qr_code_image = base64.b64encode(temp.getvalue())
                    rec.sh_qr_code_img = qr_code_image
