# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    policy_type = fields.Selection(
        selection=[
            ('vehicle', 'Vehicle'),
            ('health', 'Health'),
            ('corporate', 'SME')
        ],
        string="Policy Type",
        copy=False,
        related='policy_category_id.policy_type'
    )
    is_policy_quotation = fields.Boolean(
        string="Policy Quotation",
        copy=False
    )
    policy_sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Policy Line",
        copy=False,
        readonly=True
    )
    policy_id = fields.Many2one(
        'insurance.policy',
        string="Policy",
        copy=False,
        readonly=True
    )
    vehicle_number = fields.Char(
        string="Vehicle Number",
        copy=False
    )
    vehicle_manufacturing_year = fields.Char(
        string="MFG Year",
        copy=False
    )
    vehicle_make = fields.Char(
        string="Make",
        copy=False
    )
    vehicle_model = fields.Char(
        string="Model",
        copy=False
    )
    agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
    )
    idv_value = fields.Float(
        string="IDV Value",
    )
    od_amount = fields.Float(
        string="OD Amount",
    )
    addon_amount = fields.Float(
        string="Addon Amount",
    )
    policy_category_id = fields.Many2one(
        'product.category',
        string="Policy Category",
        domain="[('is_policy_category', '=', True)]",
    )

    ncb_bonus = fields.Float(
        string="NCB (%)",
    )

    third_party = fields.Float(
        string="Third Party",
    )

    policy_details_holder = fields.One2many(
        string="Partner Relatives",
        comodel_name="policy.details.holder",
        inverse_name="order_id",
    )
    cng_lpg_value = fields.Char(
        string="CNG/LPG Value",
        copy=False
    )
    engine_chassis_no = fields.Char(
        string="Engine Chassis No",
    )

    fuel_type = fields.Selection(
        selection=[
            ('petrol', 'Petrol'),
            ('diesel', 'Diesel'),
            ('cng', 'CNG'),
            ('electric', 'Electric'),
        ],
        copy=False,
        string="Fuel Type",
    )

    non_electrical_accessories_idv_electrical = fields.Float(
        string="Non Electrical Accessories IDV Electrical",
    )
    electronic_accessories_idv = fields.Float(
        string="Electronic Accessories IDV",
    )

    is_floater = fields.Boolean(
        string="Is Floater",
        copy=False,
        default=True
    )
    is_individual = fields.Boolean(
        string="Is Individual",
        copy=False,
        default=True
    )

    def get_line_data(self):
        data_dct = {}
        sum_insured_list = self.order_line.mapped("sum_insured")
        for rec in self.order_line:
            if rec.insurance_company_id not in data_dct:
                data_dct[rec.insurance_company_id] = {}
                for sum_insured in sum_insured_list:
                    data_dct[rec.insurance_company_id].update({sum_insured: {
                        'Floater': '-',
                        'Individual': '-',
                    }})
            data_dct[rec.insurance_company_id][rec.sum_insured] = {
                'Floater': rec.floater_price_unit,
                'Individual': rec.individual_price_unit,
            }
        return data_dct

    @api.onchange('agent_id')
    def onchange_agent(self):
        if self.agent_id:
            self.user_id = self.env['res.users'].sudo().search([
                ('partner_id', '=', self.agent_id.id)
            ]).id

    def action_convert_policy(self):
        act_read = self.env.ref(
            'qno_insurance_management.action_sale_policy_detail_wizard'
        ).sudo().read([])[0]
        return act_read

    def action_commission_rate(self):
        return

    def action_confirm_policy(self):
        if not self.agent_id:
            raise ValidationError(
                _('Please add valid agent')
            )
        act_read = self.env.ref(
            'qno_insurance_management.action_sale_policy_confirm_wizard'
        ).sudo().read([])[0]
        act_read['context'] = {
            'default_policy_sale_order_line_ids': [(6, 0, self.order_line.ids)]
        }
        return act_read

    @api.onchange('idv_value')
    def onchange_idv_value(self):
        self.order_line.update({
            'idv_value': self.idv_value,
        })
        self.order_line.onchange_price_unit_value()

    @api.onchange('od_amount')
    def onchange_od_amount(self):
        self.order_line.update({
            'od_amount': self.od_amount,
        })
        self.order_line.onchange_price_unit_value()

    @api.onchange('addon_amount')
    def onchange_addon_amount(self):
        self.order_line.update({
            'addon_amount': self.addon_amount,
        })
        self.order_line.onchange_price_unit_value()

    @api.onchange('third_party')
    def onchange_third_party(self):
        self.order_line.update({
            'third_party': self.third_party
        })
        self.order_line.onchange_price_unit_value()

    @api.onchange('ncb_bonus')
    def onchange_ncb_bonus(self):
        self.order_line.update({
            'ncb_bonus': self.ncb_bonus,
        })
        self.order_line.onchange_price_unit_value()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.policy_type == 'health':
            self.policy_details_holder = [(5, 0, 0)]
            for rec in self.partner_id.child_ids:
                vals = {
                    'relation_id': rec.partner_relation_id.id,
                    'date_of_birth': rec.date_of_birth,
                    'name': rec.name,
                    'gender': rec.gender,
                }
                self.policy_details_holder = [(0, 0, vals)]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    idv_value = fields.Float(
        string="IDV Value",
    )
    od_amount = fields.Float(
        string="OD Amount",
    )
    addon_amount = fields.Float(
        string="Addon Amount",
    )
    ncb_bonus = fields.Float(
        string="NCB (%)",
    )

    third_party = fields.Float(
        string="Third Party",
    )
    price_unit = fields.Float(
        string="Pre Tax Premium",
    )
    price_total = fields.Monetary(
        string="Net Premium",
    )

    floater_price_unit = fields.Float(
        string="Floater Price Unit",
    )
    individual_price_unit = fields.Float(
        string="Individual Price Unit",
    )
    sum_insured = fields.Float(
        string="Sum Insured",
    )
    # insurance_company_id = fields.Many2one(
    #     'res.company',
    #     string='Company',
    #     copy=True,
    # )

    insurance_company_id = fields.Many2one(
        'res.partner',
        string='Company',
        copy=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        self.insurance_company_id = self.product_id.insurance_company_id
        return super(SaleOrderLine, self)._onchange_product_id_warning()

    @api.onchange('od_amount', 'addon_amount', 'third_party', 'discount', 'ncb_bonus')
    def onchange_price_unit_value(self):
        for rec in self:
            # discount = rec.discount + rec.ncb_bonus
            price = rec.od_amount + rec.addon_amount
            # if discount > 0:
            #     price = price * (1.0 - discount / 100.0)
            price = price + rec.third_party
            rec.price_unit = price

    #             if discount > 0:
    #                 price = (rec.od_amount + rec.addon_amount) - (
    #                         ((rec.od_amount + rec.addon_amount) * rec.discount) / 100) + rec.third_party
    #                 rec.price_unit = price
    #             else:
    #                 rec.price_unit = (rec.od_amount + rec.addon_amount) - (
    #                         ((rec.od_amount + rec.addon_amount) * 0) / 100) + rec.third_party

    def name_get(self):
        res = []
        for line in self:
            name = line.product_id.name
            if line.insurance_company_id:
                name = "Company : " + line.insurance_company_id.name
            if line.sum_insured > 0:
                name = name + " Sum Insured: " + str(line.sum_insured)
            res.append((line.id, name))
        return res

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            #             discount=self.discount,
            discount=0,
            price_subtotal=self.price_subtotal,
        )


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    policy_type = fields.Selection(
        selection=[
            ('vehicle', 'Vehicle'),
            ('health', 'Health'),
            ('corporate', 'SME')
        ],
        string="Policy Type",
        copy=False
    )

    policy_categ_id = fields.Many2one(
        'product.category',
        string="Policy Category",
        domain="[('is_policy_category', '=', True)]",
    )


class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'

    def _prepare_order_line_values(self):
        values = super(SaleOrderTemplateLine, self)._prepare_order_line_values()
        values.update({
            'insurance_company_id': self.product_id.insurance_company_id.id,
        })
        return values
