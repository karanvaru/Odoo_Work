from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _name = "crm.cost.sheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    line_ids = fields.One2many("crm.cost.sheet.line", "crm_cost_sheet_id", string="lines")
    name = fields.Char("Name")
    date = fields.Date("Date", default=fields.Date.context_today, tracking=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    distributor_id = fields.Many2one('res.partner', string="Distributor")
    panel_distributor_id = fields.Many2one('res.partner', string="Panel Distributor")
    panel_rate = fields.Float("Panel Rate", tracking=True)
    total_cost_without_tax = fields.Float("Total Cost Without Tax", compute="_compute_total_cost_without_tax")
    tax_amount = fields.Float("Tax Amount", compute="_compute_total_cost_without_tax")
    total_amount = fields.Float("Total Amount", compute="_compute_total_amount")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Canceled'),
    ], string='Status', default="draft", readonly=True)
    capacity = fields.Float("Capacity", compute="_compute_capacity")
    crm_panel_cost_line_ids = fields.One2many("crm.panel.cost.line", "crm_cost_id", string="Crm Panel Cost Line")
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    area_type = fields.Selection([
        ('urban', 'Urban'),
        ('rural', 'Rural'),
    ], string='Area Type')
    terrif_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ], string='Terrif Type')
    internal_note = fields.Text("Internal Note")
    template_id = fields.Many2one("cost.sheet.template", string="Templates")
    per_kw_cost_wo_gst = fields.Float("per kW Cost W/O GST", compute="_compute_per_kw_cost_wo_gst")
    interest_calculation = fields.Float("Interest Calculation", compute="_compute_interest_calculation")
    profit_per_kw = fields.Float("Profit per kW", compute="_compute_profit_per_kw")
    gst_per_kw_on_costing = fields.Float("GST per kW on Costing", compute="_compute_gst_per_kw_on_costing")
    final_price_per_kw_with_gst = fields.Float("Final Price per kW With GST",
                                               compute="_compute_final_price_per_kw_with_gst")
    interest_calculation_percentage = fields.Float("Interest Calculation Percentage")
    profit_per_kw_percentage = fields.Float("Profit per kW Percentage")
    gst_per_kw_on_costing_percentage = fields.Float("GST per kW on Costing Percentage")
    total_amount_with_gst = fields.Float("Total Amount Incl. GST", compute="_compute_total_amount_with_gst")
    total_subsidy = fields.Float("Total Subsidy")
    total_amount_after_subsidy = fields.Float("Total Amount After Subsidy",
                                              compute="_compute_total_amount_after_subsidy")
    rupees_per_kw = fields.Float("Rs./Kw")
    sub_total_subsidy = fields.Float("Sub Total Subsidy")

    @api.model
    def create(self, vals_list):
        res = super(ResPartnerInherit, self).create(vals_list)
        res['name'] = self.env['ir.sequence'].next_by_code('costing.sheet')
        return res

    @api.depends('line_ids.subtotal_without_tax', 'line_ids.total_tax')
    def _compute_total_cost_without_tax(self):
        total = 0
        tax = 0
        for rec in self.line_ids:
            total += rec.subtotal_without_tax
            tax += rec.total_tax
        self.total_cost_without_tax = total
        self.tax_amount = tax

    @api.depends('total_cost_without_tax', 'tax_amount')
    def _compute_total_amount(self):
        self.total_amount = self.total_cost_without_tax + self.tax_amount

    def action_submit_button(self):
        for rec in self:
            rec.state = 'submit'

    def action_cancel_button(self):
        for rec in self:
            rec.state = 'cancel'

    def action_approve_button(self):
        for rec in self:
            rec.state = 'approve'

    def action_reject_button(self):
        for rec in self:
            rec.state = 'reject'

    @api.onchange('template_id')
    def _onchange_template_id(self):
        list_product = []
        self.line_ids = [(5, 0, 0)]
        for rec in self.template_id.line_ids:
            dict_product = {
                'product_id': rec.product_id.id,
                'quantity': rec.quantity,
            }
            list_product.append((0, 0, dict_product))
        self.line_ids = list_product
        self.line_ids.product_id_onchange()

    @api.depends('total_cost_without_tax', 'capacity')
    def _compute_per_kw_cost_wo_gst(self):
        if self.capacity != 0:
            self.per_kw_cost_wo_gst = self.total_cost_without_tax / self.capacity
        else:
            self.per_kw_cost_wo_gst = 0.00

    @api.depends('per_kw_cost_wo_gst', 'interest_calculation_percentage')
    def _compute_interest_calculation(self):
        self.interest_calculation = self.per_kw_cost_wo_gst * self.interest_calculation_percentage / 100

    @api.depends('per_kw_cost_wo_gst', 'profit_per_kw_percentage')
    def _compute_profit_per_kw(self):
        self.profit_per_kw = self.per_kw_cost_wo_gst * self.profit_per_kw_percentage / 100

    @api.depends('per_kw_cost_wo_gst', 'interest_calculation', 'profit_per_kw', 'gst_per_kw_on_costing_percentage')
    def _compute_gst_per_kw_on_costing(self):
        total = self.per_kw_cost_wo_gst + self.interest_calculation + self.profit_per_kw
        self.gst_per_kw_on_costing = total * self.gst_per_kw_on_costing_percentage / 100

    @api.depends('per_kw_cost_wo_gst', 'interest_calculation', 'profit_per_kw', 'gst_per_kw_on_costing')
    def _compute_final_price_per_kw_with_gst(self):
        self.final_price_per_kw_with_gst = self.per_kw_cost_wo_gst + self.interest_calculation + self.profit_per_kw + self.gst_per_kw_on_costing

    @api.depends('final_price_per_kw_with_gst', 'capacity')
    def _compute_total_amount_with_gst(self):
        self.total_amount_with_gst = self.final_price_per_kw_with_gst * self.capacity

    @api.depends('total_amount_with_gst', 'total_subsidy')
    def _compute_total_amount_after_subsidy(self):
        self.total_amount_after_subsidy = self.total_amount_with_gst - self.total_subsidy

    @api.depends('capacity', 'rupees_per_kw')
    def _compute_capacity(self):
        if self.capacity <= 1:
            self.rupees_per_kw = 45520
        elif self.capacity <= 2:
            self.rupees_per_kw = 49093.32
        elif self.capacity <= 3:
            self.rupees_per_kw = 47796
        elif self.capacity <= 6:
            self.rupees_per_kw = 46647.76
        elif self.capacity <= 10:
            self.rupees_per_kw = 46089
        elif self.capacity <= 25:
            self.rupees_per_kw = 43512.57
        elif self.capacity <= 50:
            self.rupees_per_kw = 42675
        elif self.capacity <= 100:
            self.rupees_per_kw = 38350.6


class CrmCostSheetLine(models.Model):
    _name = "crm.cost.sheet.line"

    crm_cost_sheet_id = fields.Many2one("crm.cost.sheet")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity")
    description = fields.Char(string="Description")
    price_unit = fields.Float(str="Price Unit")
    tax_ids = fields.Many2many('account.tax', string="Tax")
    subtotal_without_tax = fields.Float("Total Without Tax", compute="_compute_subtotal_without_tax")
    subtotal = fields.Float("Sub Total", compute="_compute_subtotal")
    total_tax = fields.Float("Total Tax")

    @api.onchange("product_id")
    def product_id_onchange(self):
        total = 0
        for rec in self:
            rec.update({
                'price_unit': rec.product_id.list_price,
                'description': rec.product_id.display_name,
                'tax_ids': rec.product_id.taxes_id,
            })

    @api.depends('price_unit', 'quantity')
    def _compute_subtotal_without_tax(self):
        for rec in self:
            rec.subtotal_without_tax = rec.price_unit * rec.quantity

    @api.depends('subtotal_without_tax', 'tax_ids', 'total_tax')
    def _compute_subtotal(self):
        for res in self:
            res.total_tax = res.subtotal_without_tax * res.tax_ids.amount / 100
            res.subtotal = res.subtotal_without_tax + res.total_tax

    def action_open_cost_sheet_template_wizard(self):
        return {
            'name': _('Cost Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cost.template.wizard',
            'target': 'new',
        }
