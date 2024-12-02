from odoo import models, fields, api
from datetime import datetime


class SalePolicyConfirmWizard(models.TransientModel):
    _name = "sale.policy.confirm.wizard"

    policy_sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Policies",
    )
    policy_sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Policy",
        required=True
    )
    od_amount = fields.Float(
        string="OD Amount",
    )

    addon_amount = fields.Float(
        string="Addon Amount",
    )

    third_party = fields.Float(
        string="Third Party",
    )

    discount = fields.Float(
        string="Discount (%)"
    )
    gross_premium = fields.Float(
        string="Pre Tax Premium",
    )
    policy_type = fields.Selection(
        selection=[
            ('vehicle', 'Vehicle'),
            ('health', 'Health'),
            ('corporate', 'SME')
        ],
        string="Policy Type",
        copy=False,
    )

    health_policy_type = fields.Selection(
        selection=[
            ('floater', 'Floater'),
            ('individual', 'Individual'),
        ],
        default='floater',
        string="Policy Type",
        copy=False,
    )

    @api.onchange('policy_sale_order_line_id')
    def onchange_policy_sale_order(self):
        gross_premium = 0.0
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        order = self.env[active_model].browse(active_id)
        policy = order.order_line.filtered(
            lambda policy: policy.id == self.policy_sale_order_line_id.id)
        if policy:
            if self.health_policy_type == 'floater':
                gross_premium = policy.floater_price_unit
            if self.health_policy_type == 'individual':
                gross_premium = policy.individual_price_unit

        self.update({
            'od_amount': policy.od_amount,
            'addon_amount': policy.addon_amount,
            'discount': policy.discount,
            'third_party': policy.third_party,
            'policy_type': order.policy_type,
            'gross_premium': gross_premium
        })

    @api.onchange('health_policy_type')
    def onchange_health_policy_type(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        policy_price = self.env[active_model].browse(active_id)
        lines = policy_price.order_line.filtered(
            lambda policy: policy.id == self.policy_sale_order_line_id.id)
        if lines:
            if self.health_policy_type == 'floater':
                self.gross_premium = lines.floater_price_unit
            if self.health_policy_type == 'individual':
                self.gross_premium = lines.individual_price_unit

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        partner_relative = []
        gross_premimum = 0.0
        if active_id and active_model:
            order = self.env[active_model].browse(active_id)
            price = self.gross_premium
            if self.policy_type == 'vehicle':
                # discount = self.discount + order.ncb_bonus
                price = self.od_amount + self.addon_amount
                # if discount > 0:
                #     price = price * (1.0 - discount / 100.0)
                gross_premimum += price + self.third_party
            else:
                gross_premimum += price
            policy_sale_order_line_id = self.policy_sale_order_line_id
            tax = 0.0
            for rec in policy_sale_order_line_id.tax_id:
                tax += rec.amount
            amount = gross_premimum * tax / 100
            net_amount = gross_premimum + amount
            for rec in order.policy_details_holder:
                partner_relative.append(rec.id)

            order.update({
                'policy_sale_order_line_id': policy_sale_order_line_id
            })
            other_lines = order.order_line.filtered(lambda i: i != policy_sale_order_line_id).update(
                {'product_uom_qty': 0})

            order.action_confirm()
            vals = {
                'partner_id': order.partner_id.id,
                'agent_id': order.agent_id.id,
                'insurance_company_id': policy_sale_order_line_id.product_id.insurance_company_id.id,
                'policy_product_id': policy_sale_order_line_id.product_id.id,
                'net_amount': net_amount,
                'gross_premimum': gross_premimum,
                'tax_ids': policy_sale_order_line_id.tax_id.ids,
                'tax_amount': policy_sale_order_line_id.price_tax,
                'vehicle_number': order.vehicle_number,
                'vehicle_manufacturing_year': order.vehicle_manufacturing_year,
                'vehicle_make': order.vehicle_make,
                'vehicle_model': order.vehicle_model,
                'order_ref_id': order.id,
                'policy_type': order.policy_type,
                'idv_value': policy_sale_order_line_id.idv_value,
                'notes': policy_sale_order_line_id.name,
                'od_amount': self.od_amount,
                'addon_amount': self.addon_amount,
                'third_party': self.third_party,
                'discount': self.discount,
                'policy_holders_ids': partner_relative,
                'policy_category_id': order.policy_category_id.id,
                'ncb_amount': order.ncb_bonus,

                'cng_lpg_value': order.cng_lpg_value,
                'engine_chassis_no': order.engine_chassis_no,
                'fuel_type': order.fuel_type,
                'company_id': order.company_id.id,

                'electronic_accessories_idv': order.electronic_accessories_idv,
                'non_electrical_accessories_idv_electrical': order.non_electrical_accessories_idv_electrical,
                'health_policy_type': self.health_policy_type,
            }
            policy_id = self.env['insurance.policy'].create(vals)
            order.update({'policy_id': policy_id.id})
        return True
