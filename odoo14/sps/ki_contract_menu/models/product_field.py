from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import qrcode
import base64
from io import BytesIO


class ProductStatus(models.Model):
    _inherit = 'product.product'

    product_status = fields.Selection([
        ('active', 'Activate'),
        ('deactive', 'Deactivate')
    ],
        default='deactive',
        string='Status'
    )

    is_active = fields.Boolean(
        string='Active',
    )

    deactive_reasion = fields.Selection([
        ('onSite', 'On Site'),
        ('onOurOffice', 'On Our Office'),
        ('dead', 'Dead'),
        ('other', 'Other')
    ], string='Deactivate Reason')
    current_contract_id = fields.Many2one(
        'contract.contract',
        string='Current Assigned Contract'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=False,

    )
    department_pro = fields.Char(
        string='Department',
        required=False,

    )
    partner_shipping_pro_id = fields.Many2one(
        'res.partner',
        string='Location',
        required=False,

    )
    is_cartridge = fields.Boolean(
        string='Cartridge'
    )
    purchase_id = fields.Many2one(
        'purchase.order'
    )

    category_name = fields.Char(
        string='Category Name',
        related='categ_id.name',
        store=True
    )
    category_type = fields.Selection(
        string='Category type',
        related='categ_id.type',
        store=True
    )

    qr_code = fields.Binary(
        string='QR Code',
        store=True,
        attachment=True,
        compute='qr_code_generate',
    )

    # part_product_line_ids = fields.One2many(
    #     'cartridge.part.line',
    #     'product_id',
    #     string='All Parts'
    # )

    def type_product(self):
        for rec in self:
            rec.type = 'product'

    @api.depends('default_code')
    def qr_code_generate(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            # if rec.default_code:
            qr = qrcode.QRCode(version=3, box_size=10, border=4,
                               error_correction=qrcode.constants.ERROR_CORRECT_L)
            msg = "%s/product/details?ProductNumber=%s" % (base_url, rec.default_code)
            qr.add_data(msg)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            rec.qr_code = qr_image

    @api.model
    def default_get(self, fields):
        res = super(ProductStatus, self).default_get(fields)
        if self._context.get('menu_printer'):
            cate_name = self.env['product.category'].search([('type', '=', 'printer')], limit=1)
            res.update({
                'categ_id': cate_name.id,
            })
        elif self._context.get('menu_cartridge'):
            cate_name = self.env['product.category'].search([('type', '=', 'cartridge')])
            res.update({
                'categ_id': cate_name.id,
                'is_cartridge': True,
            })
        elif self._context.get('menu_parts'):
            cate_name = self.env['product.category'].search([('type', '=', 'parts')])
            res.update({
                'categ_id': cate_name.id,
            })
        elif self._context.get('menu_printer_parts'):
            cate_name = self.env['product.category'].search([('type', '=', 'printer_parts')])
            res.update({
                'categ_id': cate_name.id,
            })

        return res

    @api.constrains('default_code')
    def unique_internal_reference(self):
        for record in self:
            if record.default_code:
                exist_code = self.search([
                    ('default_code', '=', record.default_code),
                    ('id', '!=', record.id),
                ])
                if exist_code:
                    raise ValidationError(_("Internal Reference must be unique !"))

    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '%s' % (name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id')) or []
            if not sellers and partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                # Filter out sellers based on the company. This is done afterwards for a better
                # code readability. At this point, only a few sellers should remain, so it should
                # not be a performance issue.
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result

    def action_open_all_contract(self):
        act = self.env.ref('ki_contract_menu.action_contract').read([])[0]
        act['domain'] = [('contract_line_fixed_ids.product_id', '=', self.id)]
        act['context'] = {'default_product_id': self.id}
        return act

    def action_open_all_tickets(self):
        act = self.env.ref('helpdesk_mgmt.helpdesk_ticket_action').read([])[0]
        act['domain'] = [('product_id', '=', self.id)]
        act['context'] = {'default_product_id': self.id}
        return act

    def action_open_all_purchase(self):
        act = self.env.ref('purchase.purchase_rfq').read([])[0]
        act['domain'] = [('product_id', '=', self.id)]
        act['context'] = {'default_product_id': self.id}
        return act

    def action_in_out_register(self):
        act = self.env.ref('ki_contract_menu.product_register_line_action').read([])[0]
        act['domain'] = [('product_id', '=', self.id)]
        act['context'] = {'default_product_id': self.id}
        return act

    def action_refill_request(self):
        act = self.env.ref('ki_contract_menu.refill_request_actions').read([])[0]
        act['domain'] = [('product_id', '=', self.id)]
        act['context'] = {'default_product_id': self.id}
        return act

    def action_parts_historys(self):
        act = self.env.ref('ki_contract_menu.action_product_parts_history_lines_on_catridge').read([])[0]
        act['domain'] = [('refill_part_id.product_id', '=', self.id)]
        return act

    def action_transactions(self):
        act = self.env.ref('ki_contract_menu.action_product_parts_history_lines').read([])[0]
        act['domain'] = [('product_part_id', '=', self.id)]
        return act

    def action_count_parts(self):
        refill_part_id = self.env['refill.request.line'].search(
            [('product_part_id', '=', self.id), ('refill_part_id.state', '=', 'done')])
        r_list = []
        for rec in refill_part_id:
            r_list.append(rec.refill_part_id.product_id.id)
        act = self.env.ref('ki_contract_menu.cartridge_normal_action').read([])[0]
        act['domain'] = [('id', 'in', r_list)]
        return act


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    active_product = fields.Integer(
        string='Active Pinter',
        compute='_compute_product_count',
        readonly=True,
    )
    deactivate_product = fields.Integer(
        string='Deactivate Pinter',
        compute='_compute_product_count',
        readonly=True,
    )
    product_variant_ids = fields.One2many(
        'product.product',
        'product_tmpl_id',
        string='Products Variants'
    )
    department_pro = fields.Char(
        string='Department',
        required=False,
    )
    partner_shipping_pro_id = fields.Many2one(
        'res.partner',
        string='Location',
        required=False,
    )
    is_cartridge = fields.Boolean(
        string='Cartridge'
    )
    part_product_line_ids = fields.One2many(
        'cartridge.part.line',
        'product_template_id',
        string='All Parts'

    )

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        if self._context.get('menu_printer'):
            cate_name = self.env['product.category'].search([('type', '=', 'printer')], limit=1)
            res.update({
                'categ_id': cate_name.id,
            })
        elif self._context.get('menu_cartridge'):
            cate_name = self.env['product.category'].search([('type', '=', 'cartridge')])
            res.update({
                'categ_id': cate_name.id,
            })
        elif self._context.get('menu_parts'):
            cate_name = self.env['product.category'].search([('type', '=', 'parts')])
            res.update({
                'categ_id': cate_name.id,
            })
        elif self._context.get('menu_printer_parts'):
            cate_name = self.env['product.category'].search([('type', '=', 'printer_parts')])
            res.update({
                'categ_id': cate_name.id,
            })

        return res

    def _compute_product_count(self):
        for i in self:
            act_product = self.env['product.product'].search_count([('product_status', '=', 'active'),
                                                                    ('product_tmpl_id', '=', i.id)])

            i.active_product = act_product

            deact_product = self.env['product.product'].search_count([('product_status', '=', 'deactive'),
                                                                      ('product_tmpl_id', '=', i.id)])
            i.deactivate_product = deact_product

    def get_attachment(self):
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'product.template'), ('res_id', '=', self.id)]
        res['context'] = {'default_res_model': 'product.template', 'default_res_id': self.id}
        return res

    @api.model
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        if vals_list.get('categ_id'):
            res.categ_id = vals_list.get('categ_id')
        return res


class ProductCategory(models.Model):
    _inherit = 'product.category'

    type = fields.Selection(
        [
            ('printer', 'Printer'),
            ('cartridge', 'Cartridge'),
            ('parts', 'Parts'),
            ('printer_parts', 'Printer Parts')
        ],
        string='Type',
    )
