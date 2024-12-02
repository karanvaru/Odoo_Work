# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from lxml import etree

class QuotationTemplateLines(models.Model):
    _inherit = 'sale.order.template.line'

    sequence_float = fields.Char(string='Sequence', default=1)
    cost_template_id = fields.Many2one('cost.estimation.template', string="Cost Estimation Template")


class Quotation(models.Model):
    _inherit = 'sale.order'

    cost_estimation_ref = fields.Many2one('cost.estimation',string='Cost Estimation Ref')
    total_cost = fields.Float('Total Cost')
    total_margin = fields.Float('Total Margin')
    margin_percent = fields.Float('Margin Percent')

    # @api.model
    # def create(self,vals):
    #     print("!!!!!!!!!!   vals",vals)
    #     res = super(Quotation, self).create(vals)
    #     print("!!!!!!!!!!   self", self)
    #     print("!!!!!!!!!!   res", res)
    #     return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(Quotation, self).fields_view_get(view_id, view_type, toolbar=toolbar,submenu=submenu)
        eview = etree.fromstring(res['arch'])
        quotation = self.env['ir.config_parameter'].sudo().get_param('quotation_restriction') or False
        if quotation and view_type:
            for node in eview.xpath("//tree"):
                node.set('create', "false")
            for node in eview.xpath("//form"):
                node.set('create', "false")
        else:
            for node in eview.xpath("//form"):
                node.set('create', "true")
            for node in eview.xpath("//tree"):
                node.set('create', "true")
        res['arch'] = etree.tostring(eview)
        return res

    def action_confirm(self):
        res = super(Quotation, self).action_confirm()
        if self.cost_estimation_ref:
            sale_order = self.env['sale.order'].search([('cost_estimation_ref','=',self.cost_estimation_ref.id),('state','=','sale')])
            if len(sale_order)>1:
                raise ValidationError(_("There is a sale order for this cost estimation"))
            else:
                self.cost_estimation_ref.sale_order = self.id

        return res

    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        res = super(Quotation, self)._compute_margin()
        for order in self:
            if order.cost_estimation_ref:
                amount_untaxed = sum(i.manual_purchase_price * i.product_uom_qty for i in order.order_line)
                amount_untaxed = round(amount_untaxed)
                if not amount_untaxed:
                    amount_untaxed= order.amount_untaxed
                order.margin_percent = amount_untaxed and round(order.margin/amount_untaxed, 2)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cost_line_id = fields.Many2one('cost.estimation.line')
    manual_purchase_price = fields.Float(string="Manual Purchase Price",copy=False, digits='Product Price',)

    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price')
    def _compute_margin(self):
        res = super(SaleOrderLine, self)._compute_margin()
        for line in self:
            if line.manual_purchase_price:
                line.margin_percent = line.margin/(line.manual_purchase_price * line.product_uom_qty)
        return res


    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom', 'manual_purchase_price')
    def _compute_purchase_price(self):
        res = super(SaleOrderLine, self)._compute_purchase_price()
        for line in self:
            if line.manual_purchase_price:
                line.purchase_price = line.manual_purchase_price
        return res
#         for line in self:
#             if not line.product_id:
#                 line.purchase_price = 0.0
#                 continue
#             line = line.with_company(line.company_id)
#             product_cost = line.product_id.standard_price
#             line.purchase_price = line._convert_price(product_cost, line.product_id.uom_id)

    def _timesheet_create_project_prepare_values(self):
        res = super(SaleOrderLine, self)._timesheet_create_project_prepare_values()
        # res.write({
        #     'cost_items_ids': self.order_id.cost_estimation_ref.ids,
        # })
        res.update({'cost_estimation_ids': self.order_id.cost_estimation_ref.id})
        return res
