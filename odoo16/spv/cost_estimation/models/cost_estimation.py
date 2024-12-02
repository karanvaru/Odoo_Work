# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class cost_estimation(models.Model):
    _name = 'cost.estimation'
    _inherit = ['mail.thread']
    orderby = "create_date DESC"
    _rec_name = 'seq'

    seq = fields.Char(readonly=True, string="CE No.")
    state = fields.Selection([('draft', 'Draft'),
                             ('first_approval', 'Waiting 1st Approval'),
                             ('second_approval', 'Waiting 2nd Approval'),
                             ('approved', 'Approved'),
                             ('rejected', 'Rejected'),
                             ('cancelled', 'Cancelled')], string="State", default='draft', tracking=True)
    customer = fields.Many2one('res.partner', string="Customer", readonly=True, store=True)
    opportunity = fields.Many2one('crm.lead', string="Opportunity", readonly=True, store=True)
    sales_team = fields.Many2one("crm.team", string="Sales Team", related='opportunity.team_id', tracking=True)
    sales_person = fields.Many2one("res.users", string="Sales Person", related='opportunity.user_id', tracking=True)

    price_list = fields.Many2one('product.pricelist', string="PriceList", tracking=True)
    estimate_date = fields.Datetime(readonly=True, default=fields.Datetime.now(), string="Estimation Date", store=True, tracking=True)

    t_margin = fields.Float(string='Total Margin', store=True, readonly=True, digits=(12, 4), tracking=True, compute="_compute_total")
    t_margin_percentage = fields.Float(string='Margin Percent', store=True, readonly=True, digits=(12, 4), tracking=True, compute="_compute_total")
    fx = fields.Float('Fx Rate', default=1.0, store=True, digits=(12, 4), tracking=True)

    cost_estimation_line = fields.One2many('cost.estimation.line', 'idx_cost')
    products_line = fields.One2many('products.line', 'idx_cost')

    total_material_cost = fields.Float('Total Materials Cost', store=True, compute="_compute_total", tracking=True)
    total_labour_cost = fields.Float('Total labour Cost', store=True, compute="_compute_total", tracking=True)
    total_overhead_cost = fields.Float('Total Overhead Cost', store=True, compute="_compute_total", tracking=True)
    total_subcontractor_cost = fields.Float('Total Subcontractor Cost', store=True, compute="_compute_total", tracking=True)
    total_selling_price = fields.Float('Selling Price', store=True, compute="_compute_total", tracking=True)

    total_cost = fields.Float('Total Cost', store=True, compute="_compute_total", tracking=True)
    total_unit_price = fields.Float('Total Selling Price', store=True, compute="_compute_product_line_total", tracking=True)
    quotations_count = fields.Integer()
    notes = fields.Text('Notes', tracking=True)
    total_product_line_tax = fields.Float('Taxes', compute='_compute_product_line_total', tracking=True)
    currency_id = fields.Many2one('res.currency', related='price_list.currency_id')
    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', default=lambda self: self.env.company)

    sale_order = fields.Many2one('sale.order', readonly=True, string='Sale Order')
    ci_summary_ids = fields.One2many('ci.summary', 'cost_estimation_id')
    include_taxes = fields.Boolean(string="Include Taxes", help="sum the taxes in the total cost Or Include the taxes in the total cost")
    saleable_product_id = fields.Many2one('product.product', string="Manual Saleable Product")
    saleable_product_line_id = fields.Many2one('cost.product.line', string="Saleable Product")
    template_id = fields.Many2one('cost.estimation.template', string="Template")
    computed = fields.Boolean('Computed')
    opportunity_product_ids = fields.Many2many(
        'product.product',
        compute="_compute_opportunity_products",
        store=True
    )
    lead_section_ids = fields.Many2many(
        'cost.product.line',
        string="Sections",
        copy=False
    )

    @api.depends('cost_estimation_line', 'cost_estimation_line.salable_product_id')
    def _compute_opportunity_products(self):
        for rec in self:
            rec.opportunity_product_ids = rec.cost_estimation_line.mapped('salable_product_id').ids

    def set_template_id_record(self):
        if not self.template_id:
            raise ValidationError(_('Please set template!'))
        seq_list = []
        if self.template_id:
            if self.saleable_product_line_id:
                for res in self.cost_estimation_line:
                    seq_list.append(res.sequence)
                seq_list = list(set(seq_list))
                lines_to_generate = []
                current_line = self.cost_estimation_line.filtered(lambda cost_line: self.saleable_product_line_id == cost_line.crm_product_line_id)
                product_line = current_line.crm_product_line_id
                if current_line.sequence == 0:
                    raise UserError(_("You can't set same product template again"))
                main_position = current_line.sequence
                delete_seq = False
                if main_position in seq_list:
                    if seq_list.index(main_position) > 0:
                        delete_seq = seq_list[seq_list.index(main_position) - 1]
                    elif seq_list.index(main_position) == 0:
                        delete_seq = main_position
                    if delete_seq:
                        rem_line = self.cost_estimation_line.filtered(lambda cost_line: cost_line.crm_product_line_id and cost_line.display_type and cost_line.from_crm and cost_line.sequence == delete_seq)
                        rem_line.unlink()
                update_seq = seq_list[seq_list.index(main_position) + 1:]
                updae_seq_line = self.cost_estimation_line.filtered(lambda cost_line: cost_line.sequence in update_seq)
                if current_line:
                    cnt = 1
                    for tmpl_line in self.template_id.template_line_ids:
                        vals = {
                            'salable_product': product_line.id,
                            'salable_product_id': product_line.product_id.id,
                            'sp_desc': product_line.name,
                            'sp_quant': product_line.quantity,
                            'cost_item': tmpl_line.cost_items_id.product_tmpl_id.id,
                            'cost_item_description': tmpl_line.ci_description_id,
                            'cost_item_unit_cost':  tmpl_line.cost_items_id.product_tmpl_id.estimated_cost,
                            'cost_item_cost_currency': tmpl_line.cost_items_id.product_tmpl_id.estimated_cost,
                            'cost_item_quant_sp': tmpl_line.quantity,
                            'cost_item_uom_id': tmpl_line.uom_id.id,
                            'cost_item_type': tmpl_line.cost_item_type,
                            'cost_item_cost_sp': 1.0,
                            'taxes': False,
                            'fx': 1.0,
                            'total_cost_item_quantity': 1.0,
                            'total_cost_item_cost': 1.0,
                            'budgetary_position': tmpl_line.budgetary_position.id,
                            'budgetary_position_id': tmpl_line.budgetary_position.id,
                            'cost_template_id': self.template_id.id,
                            'sequence': main_position + cnt,
                            'sequence_float': tmpl_line.sequence_float,
                            'display_type': tmpl_line.display_type,
                            'name': tmpl_line.name,
                            'from_crm': True
                            # 'crm_product_line_id': product_line.id
                        }
                        lines_to_generate.append((0, 0, vals))
                        cnt += 1
                    # remove_lines = self.cost_estimation_line.filtered(lambda cost_line: cost_line.salable_product == self.saleable_product_line_id)
                    # remove_lines.unlink()
                    current_line.unlink()
                    u_cnt = cnt
                    for update_seq in updae_seq_line:
                        update_seq.write({'sequence': main_position + u_cnt})

                        u_cnt += 1
            self.cost_estimation_line = lines_to_generate

    @api.onchange('saleable_product_line_id')
    def onchange_saleable_product_line_id(self):
        if self.saleable_product_id and self.saleable_product_line_id:
            self.saleable_product_id = False
        self.template_id = False
        return {
            'domain': {
                'template_id': [('product_id', 'in', [self.saleable_product_line_id.product_id.id, self.saleable_product_id.id])]
            }
        }

    def set_markup_value(self):
        return {
            'name': _('Set Markup Value'),
            'view_mode': 'form',
            'res_model': 'set.markup.value',
            'view_id': self.env.ref('cost_estimation.set_markup_value_view').id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.onchange('price_list')
    def onch_pricelist(self):
        self.fx = self.price_list.currency_id.rate

    @api.depends('cost_estimation_line.markup_value', 'include_taxes', 'cost_estimation_line.tax_value')
    def _compute_product_line_total(self):
        for rec in self:
            rec.total_product_line_tax = sum(rec.cost_estimation_line.mapped('tax_value'))
            rec.total_unit_price = rec.total_cost+sum(rec.cost_estimation_line.mapped('markup_value'))

    @api.depends('cost_estimation_line.total_cost_item_cost', 'total_unit_price', 'total_cost', 'cost_estimation_line.markup_perc')
    def _compute_total(self):
        for rec in self:
            material_list = []
            labour_list = []
            overhead_list = []

            for line in rec.cost_estimation_line:
                if line.cost_item_type == 'material':
                    material_list.append(line.total_cost_item_cost)
                if line.cost_item_type == 'labour':
                    labour_list.append(line.total_cost_item_cost)
                if line.cost_item_type == 'overhead':
                    overhead_list.append(line.total_cost_item_cost)

            total_subcontractor_cost = sum(
                i.total_cost_item_cost
                for i in rec.cost_estimation_line.filtered(
                    lambda l: l.cost_item_type == 'subcontractor'
                )
            )
            rec.total_subcontractor_cost = total_subcontractor_cost

            total_selling_price = sum(i.markup_value for i in rec.cost_estimation_line)

            rec.total_material_cost = sum(material_list)
            rec.total_labour_cost = sum(labour_list)
            rec.total_overhead_cost = sum(overhead_list)
            if rec.include_taxes:
                rec.total_cost = rec.total_material_cost + rec.total_labour_cost + rec.total_overhead_cost + rec.total_product_line_tax + rec.total_subcontractor_cost
            else:
                rec.total_cost = rec.total_material_cost + rec.total_labour_cost + rec.total_overhead_cost + rec.total_subcontractor_cost

            cost_total_include_taxes = sum(i.cost_total_include_taxes for i in rec.cost_estimation_line)
            rec.t_margin = 0
            rec.t_margin_percentage = 0
            if total_selling_price:
                rec.t_margin = rec.total_unit_price - rec.total_cost
                rec.t_margin_percentage = cost_total_include_taxes / total_selling_price  # (rec.t_margin / rec.total_unit_price) * 100

            if rec.total_cost:
                rec.t_margin_percentage = (rec.t_margin / rec.total_cost) * 100.0
            else:
                rec.t_margin_percentage = 0

    @api.model
    def create(self, vals):
        if vals.get('seq', 'New') == 'New':
                vals['seq'] = self.env['ir.sequence'].next_by_code('cost.estimation') or 'New'
        result = super(cost_estimation, self).create(vals)
        return result

    def write(self, vals):
        if 'cost_estimation_line' in vals:
            removing_sections = []
            for i in vals['cost_estimation_line']:
                if i[0] == 2:
                    line_id = self.env['cost.estimation.line'].browse(i[1])
                    crm_product_line_id = line_id.crm_product_line_id
                    if crm_product_line_id in self.lead_section_ids:
                        removing_sections.append((3, crm_product_line_id.id))
            if removing_sections:
                vals.update({'lead_section_ids': removing_sections})
        result = super(cost_estimation, self).write(vals)
        return result

    def button_compute(self):
        products_list = []
        sequence = 10
        for oline in self.env['cost.product.line'].search([('cost_estimation_id', '=', self.id)]):
            exist_line = self.cost_estimation_line.filtered(lambda i: i.salable_product.id == oline.id and not i.display_type)
            if exist_line:
                unit_cost_list = []
                product_cost_total_include_taxes = []
                descp_list = []
                markup_perc = False
                markup_value = False
                n = 0
                # sequence = 10
                # sequence_float = ''
                name = ''
                for line in exist_line:
                    unit_cost_list.append(line.cost_item_cost_sp)
                    product_cost_total_include_taxes.append(line.cost_total_include_taxes)
                    if line.cost_item_description:
                        descp_list.append(line.cost_item_description)
                    n += 1
                    markup_perc += line.markup_perc
                    markup_value += line.markup_value
                    # sequence = oline.sequence
                    # sequence_float = oline.sequence_float
                    name = oline.name
                t = ""
                if descp_list:
                    for desc in descp_list:
                        t = t + '- ' + desc + '\n'
                margin = 0
                if sum(product_cost_total_include_taxes):
                    margin = (markup_value/sum(product_cost_total_include_taxes)) * 100

                sp_quant = 0
                # product_lines = self.cost_estimation_line.filtered(lambda line: line.salable_product_id.id == oline.id)
                sp_quant = line.sp_quant  # sum(i.sp_quant for i in product_lines)
                sp_desc = line.sp_desc  # ' ,'.join([i.sp_desc for i in product_lines])
                products_list_data = {
                    'idx_cost': self.id,
                    'cost_item_description': t,
                    'salable_product_id': oline.product_id.id,
                    'unit_cost': sum(unit_cost_list),
                    'margin': margin,
                    'markup_value': markup_value,
                    # 'sequence': oline.sequence,
                    'sequence': sequence + len(products_list),
                    'sequence_float': oline.sequence_float,
                    'name': name,
                    'cost_total_include_taxes': sum(product_cost_total_include_taxes),
                    'sp_quant': sp_quant,
                    'sp_desc': sp_desc,
                    'display_type': oline.display_type
                }
                products_list.append((0, 0, products_list_data))
            elif oline.display_type:
                section_data = {
                    'idx_cost': self.id,
                    'name': oline.name,
                    'display_type': oline.display_type,
                    # 'sequence': oline.sequence,
                    'sequence': sequence + len(products_list),
                    'sequence_float': oline.sequence_float,
                }
                products_list.append((0, 0, section_data))

        user_line_ids = []
        for line in self.cost_estimation_line.filtered(lambda i: not i.salable_product and i.from_crm):
            if line.cost_template_id and line.display_type:
                continue
            if line.id in user_line_ids:
                continue
            exist_lines = self.cost_estimation_line.filtered(lambda i: i.salable_product_id == line.salable_product_id and not i.salable_product)

            unit_cost_list = []
            product_cost_total_include_taxes = []
            descp_list = []
            markup_perc = False
            markup_value = False
            n = 0
            name = ''
            for line in exist_lines:
                if not line.display_type:
                    unit_cost_list.append(line.cost_item_cost_sp)
                    product_cost_total_include_taxes.append(line.cost_total_include_taxes)
                    if line.cost_item_description:
                        descp_list.append(line.cost_item_description)
                    n += 1
                    markup_perc += line.markup_perc
                    markup_value += line.markup_value
                name = name + ', ' + line.name
            t = ""
            if descp_list:
                for desc in descp_list:
                    t = t + '- ' + desc + '\n'

            margin = 0
            if sum(product_cost_total_include_taxes):
                margin = (markup_value/sum(product_cost_total_include_taxes)) * 100

            sp_quant = 0

            sp_quant = sum(i.sp_quant for i in exist_lines)
            sp_desc = ' ,'.join([i.sp_desc or '' for i in exist_lines])
            line_data = {
                'idx_cost': self.id,
                'cost_item_description': t,
                'salable_product_id': line.salable_product_id.id,
                'unit_cost': sum(unit_cost_list),
                'margin':  margin,
                'markup_value': markup_value,
                # 'sequence': line.sequence,
                'sequence': sequence + len(products_list),
                'sequence_float': line.sequence_float,
                'name': line.name,
                'cost_total_include_taxes': sum(product_cost_total_include_taxes),
                'sp_quant': line.sp_quant,
                'sp_desc': line.sp_desc,
                'display_type': line.display_type
            }
            products_list.append((0, 0, line_data))
            user_line_ids += exist_lines.ids
        self.products_line = False
        self.products_line = products_list
        datas = self.env['cost.estimation.line'].read_group([('idx_cost', 'in', self.ids), ('cost_item', '!=', False)], ['cost_item', 'total_cost_item_quantity', 'cost_total_include_taxes'], ['cost_item'])
        ci_summary = []
        for dt in datas:
            ci_summary.append((0, 0, {'cost_item': dt['cost_item'][0], 'ci_description': dt['cost_item'][1], 'total_quantity': dt['total_cost_item_quantity'], 'total_cost': dt['cost_total_include_taxes']}))
        self.ci_summary_ids = False
        self.ci_summary_ids = ci_summary

        if any(not line.cost_item for line in self.cost_estimation_line.filtered(lambda i: not i.display_type)):
            raise ValidationError(_("You can't compute cost estimation without atleast one cost item per saleable product."))
        self.computed = True
        self._compute_total()

    def create_quotation(self):
        quotation = self.env['sale.order'].search([])
        quotation_description_product = self.env['ir.config_parameter'].sudo().get_param('quotation_description_product') or False

        product_list = []
        for line in self.products_line:
            if not line.display_type:
                if quotation_description_product == 'sp':
                    description = line.sp_desc
                else:
                    description = line.cost_item_description
            else:
                description = line.name

            product_list.append((0, 0, {'product_id': line.salable_product_id.id,
                                        'name': description,
                                        'product_uom_qty': line.sp_quant,
                                        'price_unit': line.unit_price,
                                        'tax_id': line.taxes.ids,
                                        'sequence': line.sequence,
                                        'display_type': line.display_type,
                                        'manual_purchase_price': line.unit_cost
                                        }))

        vals = {'partner_id': self.customer.id,
                'cost_estimation_ref': self.id,
                'total_margin': self.t_margin,
                'margin_percent': self.t_margin_percentage,
                'total_cost': self.total_cost,
                'user_id': self.sales_person.id,
                'team_id': self.sales_team.id,
                'pricelist_id': self.price_list.id,
                'opportunity_id': self.opportunity.id,
                'order_line': product_list}
        res_id = quotation.create(vals)
        self.quotations_count = len(self.env['sale.order'].search([('cost_estimation_ref', '=', self.id)]))
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': res_id.id,
            # 'domain': [('id', '=', self.env['sale.order'].search([('cost_estimation_ref','=', self.id)], order='name desc',limit=1).id)],
            'view_type': 'form',
            'view_mode': 'form',
        }

    def action_view_quotation(self):
        return {
            'name': _('Quotations'),
            'domain': [('cost_estimation_ref', '=', self.id)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }

    def submit(self):
        self.state = 'first_approval'
        if any(not line.cost_item for line in self.cost_estimation_line.filtered(lambda i: not i.display_type)):
            raise ValidationError(_("You can't submit cost estimation without cost item."))
        if not self.computed:
            raise ValidationError(_("You can not submit the cost estimation before computing the estimate, please perform the computation first."))

    def approve_1(self):
        cost_estimations = self.env['cost.estimation'].search([('opportunity.id', '=', self.opportunity.id), ('state', 'not in', ['approved', 'rejected'])])
        cancel_non_conf_ce = self.env['ir.config_parameter'].sudo().get_param('cancel_non_conf_ce') or False

        if cancel_non_conf_ce:
            for rec in cost_estimations:
                rec.state = 'cancelled'
        self.state = 'second_approval'

    def approve_2(self):
        one_approved_cost_est = self.env['ir.config_parameter'].sudo().get_param('one_approved_cost_est') or False
        multiple_ce = self.search([('opportunity', '=', self.opportunity.id), ('state', '=', 'approved')])
        if one_approved_cost_est and (len(multiple_ce) >= 1):
            raise ValidationError(_("You can't Approve Multiple cost estimation "))
        else:
            self.state = 'approved'

    def reject_1(self):
        self.state = 'rejected'

    def reject_2(self):
        self.state = 'rejected'

    def cancel(self):
        self.state = 'cancelled'

    def set_draft(self):
        self.state = 'draft'


class ProductsLine(models.Model):
    _name = 'products.line'

    salable_product = fields.Many2one('cost.product.line', string='Salable Product', store=True, readonly=True)
    salable_product_id = fields.Many2one('product.product', string="Saleable Product", readonly=True)
    sp_desc = fields.Text(string="SP Description")  # ,related='salable_product.description')
    cost_item_description = fields.Text(string='CI Description', store=True, readonly=True)
    sp_quant = fields.Float(string="SP Qty")  # ,related='salable_product.quantity')
    taxes = fields.Many2many('account.tax', string='Taxes', default=False, domain=[('type_tax_use', '=', 'sale')])
    unit_of_measure = fields.Many2one('uom.uom', string='UoM', related='salable_product.unit_of_measure')
    unit_cost = fields.Float(string="Unit Cost", store=True, readonly=True)
    total_cost = fields.Float(string="Total Cost", compute='_product_line_calculations', store=True)
    cost_total_include_taxes = fields.Float(string="Total Cost")
    margin = fields.Float(string="Markup %")
    markup_value = fields.Float(string="Markup value")
    subtotal = fields.Float(string="Subtotal", compute='_set_subtotal')
    subtotal_taxed = fields.Float(string="Subtotal Taxed", store=True, readonly=True)
    unit_price = fields.Float(string="Unit Price", compute='_product_line_calculations')
    idx_cost = fields.Many2one('cost.estimation')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    sequence_float = fields.Char(string='Sequence', default=1)

    @api.depends('unit_cost', 'sp_quant', 'margin')
    def _product_line_calculations(self):
        for rec in self:
            rec.total_cost = rec.unit_cost * rec.sp_quant
            # rec.subtotal = rec.total_cost + (rec.total_cost * rec.margin/100)
            if rec.sp_quant:
                rec.unit_price = (rec.cost_total_include_taxes + rec.markup_value) / rec.sp_quant  # rec.unit_cost + (rec.unit_cost * rec.margin/100)
            else:
                rec.unit_price = 0
            tax_list = []
            if rec.taxes:
                for tax in rec.taxes:
                    tax_list.append(tax.amount)
                rec.subtotal_taxed = rec.subtotal * (sum(tax_list)/100)

    @api.model
    def create(self, vals):
        res = super(ProductsLine, self).create(vals)
        return res

    @api.depends('unit_price', 'sp_quant')
    def _set_subtotal(self):
        for rec in self:
            rec.subtotal = rec.unit_price * rec.sp_quant


class CostEstimationLine(models.Model):
    _name = 'cost.estimation.line'

    sequence_float = fields.Char(string='Sequence', default=1)
    sequence = fields.Integer(string='Sequence', default=10)
    salable_product = fields.Many2one('cost.product.line', string='Salable Product', domain=[('display_type', '=', False)])  # , domain=lambda self: self._domain_product_id())
    salable_product_id = fields.Many2one('product.product', string='Salable Product')  # , domain=lambda self: self._domain_product_id())
    sp_desc = fields.Text(string="SP Description")  # , related='salable_product.description')
    sp_quant = fields.Float(string="SP Qty")  # , related='salable_product.quantity', store=True)
    cost_item = fields.Many2one('product.template', string="Cost Item")
    cost_item_description = fields.Text(string='CI Description', store=True)
    cost_item_type = fields.Selection([('material', 'Material'), ('labour', 'Labour'), ('overhead', 'Overhead'), ('subcontractor', 'Subcontractor')], string="CI Type", required=False, default='material')
    cost_item_quant_sp = fields.Float(string="CI Qty/SP", default='1')
    cost_item_cost_currency = fields.Float(string="CI Unit Cost(Currency)", default='1')
    fx = fields.Float('Fx Rate', related='idx_cost.fx', store=True, digits=(12, 4))
    taxes = fields.Many2many('account.tax', string='Taxes', default=False, domain=[('type_tax_use', '=', 'purchase')])
    cost_item_unit_cost = fields.Float(string="CI Unit Cost EGP", compute='_calculations')
    cost_item_cost_sp = fields.Float(string="CI Cost/SP", compute='_calculations')
    total_cost_item_quantity = fields.Float(string='Total CI Qty', compute='_calculations', store=True)
    total_cost_item_cost = fields.Float(string='CI Total Cost', compute='_calculations')
    cost_item_uom_id = fields.Many2one('uom.uom', string='CI Unit of Measure', related='cost_item.uom_id')
    cost_total_include_taxes = fields.Float(compute="_compute_cost_total_taxes", string="Total Cost", store=True)
    task_id = fields.Many2one('project.task')
    markup_perc = fields.Float(string="Markup %", store=True)
    markup_value = fields.Float(string="Markup value", compute="_compute_cost_total_taxes", store=True)
    budgetary_position_id = fields.Many2one('account.budget.post', string="Budgetary Position")
    practical_amount = fields.Float(string="Practical Amount", compute="compute_practical_amount")
    tax_value = fields.Float(string="Tax Value", compute="_compute_tax_value")
    crm_product_line_id = fields.Many2one('cost.product.line', strong="CRM Product Line", copy=False)

    idx_cost = fields.Many2one('cost.estimation')
    project_id = fields.Many2one('project.project', string="Project Ref")
    cost_template_id = fields.Many2one('cost.estimation.template', copy=False)

    selling_price = fields.Float(compute="_compute_selling_price", string="Selling Price", store=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='CI Description', store=True)
    from_crm = fields.Boolean(string="From CRM?")

    @api.onchange('salable_product', 'salable_product_id')
    def onchange_salable_products(self):
        if self.salable_product:
            self.update({
                'sp_desc': self.salable_product.description,
                'sp_quant': self.salable_product.quantity
            })
        elif self.salable_product_id:
            self.update({
                'sp_desc': self.salable_product_id.name,
                'sp_quant': 1
            })

    @api.depends('budgetary_position_id')
    def compute_practical_amount(self):
        for rec in self:
            practical_amount = 0.0
            analytic_account_id = self.project_id.analytic_account_id.id
            if rec.budgetary_position_id and analytic_account_id:
                cob_id = self.env['crossovered.budget.lines'].search([
                    ('analytic_account_id', '=', analytic_account_id),
                    ('general_budget_id', '=', rec.budgetary_position_id.id),
                ], limit=1)
                if cob_id:
                    practical_amount = cob_id.practical_amount
            rec.practical_amount = practical_amount

    @api.depends('taxes', 'total_cost_item_quantity')
    def _compute_tax_value(self):
        for line in self:
            line.tax_value = (line.taxes.amount/100) * line.total_cost_item_cost

    @api.onchange('markup_value')
    def onchange_markup_value(self):
        for line in self:
            if line.cost_total_include_taxes:
                line.markup_perc = (line.markup_value * 100) / line.cost_total_include_taxes
            else:
                line.markup_perc = 0

    @api.depends('total_cost_item_cost', 'idx_cost.include_taxes', 'tax_value', 'taxes')
    def _compute_cost_total_taxes(self):
        for line in self:
            # price = line.cost_item_unit_cost
            # taxes = line.taxes.compute_all(price, self.env.user.company_id.currency_id, line.cost_item_quant_sp)
            if line.idx_cost.include_taxes:
                line.cost_total_include_taxes = line.total_cost_item_cost + line.tax_value
            else:
                line.cost_total_include_taxes = line.total_cost_item_cost
            line.markup_value = (line.cost_total_include_taxes * line.markup_perc) / 100
            line.selling_price = line.markup_value + line.cost_total_include_taxes

    @api.depends('markup_value', 'cost_total_include_taxes')
    def _compute_selling_price(self):
        for line in self:
            line.selling_price = line.markup_value + line.cost_total_include_taxes

    @api.depends('cost_item_cost_currency', 'taxes', 'fx', 'cost_item_quant_sp', 'sp_quant')
    def _calculations(self):
        for rec in self:
            taxes_list = []
            for tax in rec.taxes:
                taxes_list.append(tax.amount)
            if rec.fx > 0:
                rec.cost_item_unit_cost = (rec.cost_item_cost_currency * rec.fx)
            else:
                rec.cost_item_unit_cost = rec.cost_item_cost_currency
            rec.cost_item_cost_sp = rec.cost_item_unit_cost * rec.cost_item_quant_sp
            rec.total_cost_item_quantity = rec.cost_item_quant_sp * rec.sp_quant
            rec.total_cost_item_cost = rec.cost_item_cost_sp * rec.sp_quant

    @api.onchange('cost_item')
    def onchange_cost_item(self):
        self.name = self.cost_item.name
        self.cost_item_description = self.cost_item.name
        self.cost_item_unit_cost = self.cost_item.estimated_cost
        self.cost_item_cost_currency = self.cost_item.estimated_cost
        self.cost_item_type = self.cost_item.cost_item_type

    def _domain_product_id(self):
        if self.env.context.get('active_id'):
            return "[('id', 'in', %s)]" % self.env['crm.lead'].search([('id', '=', self.env.context.get('active_id'))]).product_line.ids

    @api.onchange('name')
    def onchange_name(self):
        self.cost_item_description = self.name

    @api.model
    def create(self, vals):
        result = super(CostEstimationLine, self).create(vals)

        if not result.from_crm:
            data = {
                'product_id': result.salable_product_id and result.salable_product_id.id or False,
                'name': result.salable_product_id and result.salable_product_id.name or '',
                'description': result.sp_desc,
                'quantity': result.sp_quant and result.sp_quant or 1.0,
                'display_type': result.display_type,
                'price_unit': result.cost_item_unit_cost,
                'cost_estimation_id': result.idx_cost and result.idx_cost.id or result.idx_cost._origin
            }
            if result.display_type:
                data.update({"name": result.name})
            crm_product_line_id = self.env['cost.product.line'].create(data)
            print ("......", crm_product_line_id)
            if crm_product_line_id.display_type and not crm_product_line_id.name:
                print ("result.idx_cost.lead_section_ids", result.idx_cost.lead_section_ids)
                result.idx_cost.lead_section_ids = [(4, crm_product_line_id.id)]
                print ("result.idx_cost.lead_section_ids after", result.idx_cost.lead_section_ids)
            if crm_product_line_id and not crm_product_line_id.display_type:
                result.crm_product_line_id = crm_product_line_id.id
        return result

    # def write(self, vals):
    #     res = super(CostEstimationLine, vals).write(vals)
    #     if 'product_id' in vals and self.crm_product_line_id and not self.from_crm:
    #         data = {
    #             'product_id': self.salable_product_id and self.salable_product_id.id or False,
    #             'name': self.salable_product_id and self.salable_product_id.name or '',
    #             'description': self.sp_desc,
    #             'quantity': self.sp_quant and self.sp_quant or 1.0,
    #             'display_type': self.display_type,
    #             'price_unit': self.cost_item_unit_cost,
    #         }
    #         self.crm_product_line_id.update_seq(data)
    #     return res


class Ci_Summary(models.Model):
    _name = 'ci.summary'
    _description = "CI Summary"

    cost_estimation_id = fields.Many2one('cost.estimation')
    cost_item = fields.Many2one('product.template', string="Cost Item", readonly=True)
    ci_description = fields.Char(string="CI Description")
    total_quantity = fields.Float(string="Total Quantity", readonly=True)
    total_cost = fields.Float(string="Total Cost", readonly=True)


class CostEstimationTemplate(models.Model):
    _name = "cost.estimation.template"
    _description = "Cost Estimation Template"

    product_id = fields.Many2one('product.product', string="Product Name", required=True)
    name = fields.Char(string="Name", required=True)
    template_line_ids = fields.One2many('cost.estimation.template.line', 'cost_template_id')


class CostEstimationTemplateLine(models.Model):
    _name = "cost.estimation.template.line"
    _description = "Cost Estimation Template Line "
    _order = 'sequence'

    sequence_float = fields.Char(string='Sequence', default=1)
    sequence = fields.Integer(string='Sequence', default=10)
    cost_template_id = fields.Many2one('cost.estimation.template')
    cost_items_id = fields.Many2one('product.product', string="Cost items")
    ci_description_id = fields.Char(string="CI Description")
    cost_item_type = fields.Selection([('material', 'Material'), ('labour', 'Labour'), ('overhead', 'Overhead'), ('subcontractor', 'Subcontractor')], string="CI Type", default='material')
    quantity = fields.Float(string="Quantity")

    product_uom_id = fields.Many2one('uom.uom', related="cost_items_id.uom_id", string="Product UOM", store=True)
    product_uom_categ_id = fields.Many2one('uom.category', related="product_uom_id.category_id", string="Product UOM Category", store=True)
    name = fields.Char(string="CI Description", required=True)

    uom_id = fields.Many2one('uom.uom', string="UOM")
    budgetary_position = fields.Many2one('account.budget.post', string="Budgetary Position")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('cost_items_id')
    def onchange_cost_items_id(self):
        if self.cost_items_id:
            self.update({
                'product_uom_id': self.cost_items_id.uom_id.id,
                'name': self.cost_items_id.name,
                'cost_item_type': self.cost_items_id.cost_item_type,
                'uom_id': self.cost_items_id.uom_id.id,
            })

    @api.onchange('name')
    def onchange_name(self):
        self.ci_description_id = self.name
