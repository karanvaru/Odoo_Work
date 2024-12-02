# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import is_html_empty


class cost_estimation_crm(models.Model):
    _inherit = 'crm.lead'

    product_line = fields.One2many('cost.product.line', 'idx')
    estimation_count = fields.Integer(compute='_compute_estimation_data', string="Number of Estimation")

    sale_order_template_id = fields.Many2one(
        'sale.order.template',
        'Quotation Template',
        check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    def _prepare_opportunity_quotation_context(self):
        res = super(cost_estimation_crm,self)._prepare_opportunity_quotation_context()
        if self.sale_order_template_id:
            res.update({
                'default_sale_order_template_id': self.sale_order_template_id.id
            })
        return res

    def _compute_line_data_for_template_change(self, line):
        return {
            'sequence': line.sequence,
            'display_type': line.display_type,
            'name': line.name,
            'description': line.name
        }

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)
        # --- first, process the list of products from the template
        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)

            if line.product_id:
                price = line.product_id.lst_price
                data.update({
                    'price_unit': price,
                    'quantity': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'unit_of_measure': line.product_uom_id.id,
                    'sequence_float': line.sequence_float,
                    'cost_template_id': line.cost_template_id.id
                })

            order_lines.append((0, 0, data))

        self.product_line = order_lines

        if not is_html_empty(template.note):
            self.description = template.note

    def _compute_estimation_data(self):
        est_cnt = self.env['cost.estimation'].search([('opportunity.id', '=', self.id)])
        self.estimation_count = len(est_cnt)

    def action_estimation(self):
        approved_cost_estimation = self.env['cost.estimation'].search([('opportunity.id', '=', self.id), ('state', '=', 'approved')])
        multiple_cost_estimate = self.env['ir.config_parameter'].sudo().get_param('multiple_cost_estimate') or False

        if approved_cost_estimation and not multiple_cost_estimate:
            raise ValidationError(_("You can't create multiple cost estimation for this opportunity due to your setting restrictions"))
        else:
            if not self.product_line:
                raise ValidationError(_(
                    "You can't create cost estimation without product lines"))
            else:
                result = []
                for rec in self.product_line:
                    if (not rec.product_id.cost_ok) and rec.product_id.cost_estimation:
                        for product in rec.product_id.cost_estimation:
                            if not product.cost_item_type:
                                cost_item_type = 'material'
                            else:
                                cost_item_type = product.cost_item_type
                            values = {'salable_product': rec.id,
                                      'salable_product_id': rec.product_id.id,
                                      'sp_desc': rec.description,
                                      'sp_quant': rec.quantity,
                                      'cost_item': product.product_id.id,
                                      'cost_item_description': product.description,
                                      'cost_item_unit_cost': product.product_id.estimated_cost,
                                      'cost_item_cost_currency': 1.0,
                                      'cost_item_quant_sp': product.qty,
                                      'cost_item_uom_id': product.uom.id,
                                      'cost_item_type': cost_item_type,
                                      'cost_item_cost_sp': 1.0,
                                      'taxes': False,
                                      'fx': 1.0,
                                      'total_cost_item_quantity': 1.0,
                                      'total_cost_item_cost': 1.0,
                                      'crm_product_line_id': rec.id,
                                      'sequence_float': rec.sequence_float,
                                      'sequence': rec.sequence,
                                      'display_type': rec.display_type,
                                      'name': rec.name,
                                      'from_crm': True,
                                      'cost_template_id': rec.cost_template_id.id
                                      }
                            result.append((0, 0, values))
                    else:
                        values = {'salable_product': rec.id,
                                  'salable_product_id': rec.product_id.id,
                                  'sp_desc': rec.description,
                                  'sp_quant': rec.quantity,
                                  'cost_item': False,
                                  'cost_item_description': False,
                                  'cost_item_unit_cost': rec.product_id.estimated_cost,
                                  'cost_item_cost_currency': 1.0,
                                  'cost_item_type': 'material',
                                  'cost_item_quant_sp': 1.0,
                                  'cost_item_cost_sp': 1.0,
                                  'taxes': False,
                                  'fx': 1.0,
                                  'total_cost_item_quantity': 1.0,
                                  'total_cost_item_cost': 1.0,
                                  'crm_product_line_id': rec.id,
                                  'sequence_float': rec.sequence_float,
                                  'sequence': rec.sequence,
                                  'display_type': rec.display_type,
                                  'name': rec.name,
                                  'from_crm': True,
                                  'cost_template_id': rec.cost_template_id.id
                                  }
                        result.append((0, 0, values))
                sections = []
                for i in self.product_line:
                    if i.display_type:
                        sections.append(i.id)
                est_vals = {
                    'customer': self.partner_id.id,
                    'opportunity': self.id,
                    'price_list': self.partner_id.property_product_pricelist.id,
                    'cost_estimation_line': result,
                    'seq': 'New',
                    'saleable_product_id': self.product_line[0].product_id.id,
                    'lead_section_ids': [(6, 0, sections)]
                }
                estimation_id = self.env['cost.estimation'].create(est_vals)
                if estimation_id and self.product_line:
                    self.product_line.write({'cost_estimation_id': estimation_id.id})
                    for pl in self.product_line.filtered(lambda i: i.sequence_float).sorted('sequence_float'):
                        if pl.cost_template_id:
                            estimation_id.update({
                                'template_id': pl.cost_template_id.id,
                                'saleable_product_line_id': pl.id
                            })
                            estimation_id.set_template_id_record()
                            estimation_id.update({
                                'template_id': False,
                                'saleable_product_line_id': False
                            })
                act = self.env.ref("cost_estimation.cost_estimation_form_action").sudo().read()[0]
                act['views'] = [(self.env.ref('cost_estimation.cost_estimation_form').id, 'form')]
                act['res_id'] = estimation_id.id
                act['context'] = {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
                return act

    def action_smart_estimation(self):
        action = self.env.ref('cost_estimation.action_cost_estimation').sudo().read()[0]
        action['domain'] = [('opportunity', '=', self.id)]
        return action


class crm_product_line(models.Model):
    _name = 'cost.product.line'

    sequence_float = fields.Char(string='Sequence', default=1)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string="Description1")
    description = fields.Text(string="Description")
    quantity = fields.Float(string='Quantity')
    unit_of_measure = fields.Many2one('uom.uom', string='UoM')
    idx = fields.Many2one('crm.lead')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)
    cost_estimation_id = fields.Many2one('cost.estimation', string="Cost Estimation")
    cost_template_id = fields.Many2one('cost.estimation.template', string="Cost Estimation Template")

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.update({'price_subtotal': line.price_unit * line.quantity})

    @api.onchange('product_id')
    def _onch_product(self):
        self.name = self.product_id.name
        self.unit_of_measure = self.product_id.uom_id.id

    @api.onchange('name')
    def _onch_name(self):
        self.description = self.name

    @api.model
    def create(self, vals):
        res = super(crm_product_line, self).create(vals)
        return res
