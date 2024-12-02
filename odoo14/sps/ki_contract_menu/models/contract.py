from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContractEdit(models.Model):
    _inherit = "contract.contract"
    _order = 'create_date desc'

    qr_code = fields.Binary(
        string='QR Code',
        store=True,
        attachment=True,
        compute='qr_code_generate',
    )
    name = fields.Char(required=False)

    state = fields.Selection([
        ('active', 'Activate'),
        ('expire', 'Expired'),
        ('terminate', 'Terminate')
    ], string='Status')

    renew_from_contract = fields.Many2one(
        'contract.contract',
        string='Renew From Contract'
    )

    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Location',
    )

    date_end = fields.Date(required=True)

    contract_line_fixed_ids = fields.One2many(
        "contract.line",
        "contract_id",
        context={'active_test': False}
    )

    def action_terminate(self):
        # self.state = 'terminate'
        # print('terminate')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract Terminate',
            'res_model': 'contract.terminate.entry.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_renew(self):
        new_id = self.copy()
        action_id = self.env.ref('ki_contract_menu.action_contract').read([])[0]
        action_id['domain'] = [('id', '=', new_id.id)]
        new_id.renew_from_contract = self.id
        new_id.date_start = datetime.today()
        return action_id

    @api.model
    def _contract_expire_status(self):
        res = self.env['contract.contract'].search([('date_end', '<', fields.Date.today())])
        for re in res:
            re.state = 'expire'

    # @api.depends('date_start', 'partner_id', 'contract_line_fixed_ids')
    # def qr_code_generate(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     qr = qrcode.QRCode(version=3, box_size=10, border=4,
    #                        error_correction=qrcode.constants.ERROR_CORRECT_L)
    #
    #     for a in self.contract_line_fixed_ids:
    #         print('aaaaaaaaaaaaaa', a)
    #         QrcodeOBJ = a.product_id
    #
    #         msg = "%s/new/ticket?ProductNumber=%s" % (base_url, QrcodeOBJ.default_code)
    #         qr.add_data(msg)
    #         qr.make(fit=True)
    #         img = qr.make_image()
    #         temp = BytesIO()
    #         img.save(temp, format="PNG")
    #         qr_image = base64.b64encode(temp.getvalue())
    #         self.qr_code = qr_image

    @api.model
    def create(self, vals):

        res = super(ContractEdit, self).create(vals)
        res.state = 'active'
        date_start = res.date_start.strftime("%d/%m/%Y")
        date_end = res.date_end.strftime("%d/%m/%Y")
        sequence = self.env['ir.sequence'].next_by_code('contract.contract', sequence_date=res.date_start)
        res.update({'name': sequence})

        if res.state == 'active':
            for i in res.contract_line_fixed_ids:
                productObj = i.product_id
                if productObj.product_status == 'active':
                    raise ValidationError(_("Product is already in other contract"))
                else:
                    productObj.product_status = 'active'
                productObj.current_contract_id = res.id
                productObj.customer_id = res.partner_id
                productObj.partner_shipping_pro_id = res.partner_shipping_id
            for j in res.contract_line_fixed_ids:
                DepartmentObj = j.product_id
                DepartmentObj.department_pro = j.department

        return res

    def write(self, vals):
        res = super(ContractEdit, self).write(vals)
        for rec in self:
            # print("date________",self.date_start)
            # sequence = self.env['ir.sequence'].next_by_code('contract.contract', sequence_date=self.date_start)
            # print("sequence",sequence)
            if rec.state == 'expire' or rec.state == 'terminate':
                for s in rec.contract_line_fixed_ids:
                    productObj = s.product_id
                    productObj.product_status = 'deactive'
                    productObj.current_contract_id = False
                    productObj.customer_id = False
                    productObj.partner_shipping_pro_id = False
                for j in rec.contract_line_fixed_ids:
                    DepartmentObj = j.product_id
                    DepartmentObj.department_pro = False
        return res

    def unlink(self):
        if self.state == 'active':
            raise ValidationError(_("Please Terminate the Contract"))
        else:
            result = super(ContractEdit, self).unlink()
            # print('rrrrrrrrrrrrrrrrrrrrrr', result)
            return result

