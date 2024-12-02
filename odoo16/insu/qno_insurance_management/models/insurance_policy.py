# -*- coding: utf-8 -*-

from datetime import date, datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )
    phone = fields.Char(
        related="partner_id.phone",
        string="Phone"
    )
    mobile = fields.Char(
        related="partner_id.mobile",
        string="Mobile",
        store=True
    )
    email = fields.Char(
        related="partner_id.email",
        string="Email"
    )
    agent_id = fields.Many2one(
        'res.partner',
        string='Agent',
        required=True
    )
    insurance_company_id = fields.Many2one(
        'res.partner',
        string='Insurance Agency',
        # required=True
    )
    start_date = fields.Date(
        string='Date Started',
        default=fields.Date.context_today,
        required=True
    )
    end_date = fields.Date(
        string='Date Expire',
        readonly=True
    )
    invoice_ids = fields.One2many(
        'account.move',
        'policy_id',
        string='Invoices',
        readonly=True
    )
    commission_rate = fields.Float(
        string='Commission Percentage',
        copy=False
    )
    policy_product_id = fields.Many2one(
        'product.product',
        string='Policy',
        required=True
    )

    policy_category_id = fields.Many2one(
        'product.category',
        string='Policy Category',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    # gross_premimum = fields.Monetary(
    #     string='Gross Premium'
    # )
    ncb_amount = fields.Monetary(
        string='NCB'
    )
    gross_premimum = fields.Monetary(
        string='Gross Premium'
    )
    sum_assured = fields.Monetary(
        string='Sum Assured'
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes'
    )
    tax_amount = fields.Monetary(
        string="Tax Amount"
    )
    discount = fields.Float(
        string="Discount%"
    )
    discount_amount = fields.Monetary(
        string="Discount Amount"
    )
    net_amount = fields.Monetary(
        string="Net Premimum"
    )

    invoice_status = fields.Selection(
        selection=[
            ('invoiced', 'Invoiced'),
            ('to_invoice', 'To invoice')
        ],
        required=True,
        default="to_invoice",
        copy=False
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Running'),
            # ('invoiced', 'Invoiced'),
            ('closed', 'Closed')
        ],
        required=True,
        default='draft',
        copy=False
    )
    hide_inv_button = fields.Boolean(
        copy=False
    )
    notes = fields.Html(
        string='Comment'
    )
    policy_number = fields.Char(
        string="Policy Number",
        required=False,
        help="""
            Policy number is a unique number that 
            an insurance company uses to identify
            you as a policyholder
        """
    )
    policy_duration = fields.Integer(
        string='Duration in Days',
        required=False
    )
    order_ref_id = fields.Many2one(
        'sale.order',
        string='Order Ref',
        copy=False,
        readonly=True
    )

    commission_amount = fields.Monetary(
        string="Commission Amount",
        compute='_get_commission_amount',
        store=True
    )
    policy_holders_ids = fields.Many2many(
        'policy.details.holder',
        string='Policy Holders'
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
    policy_document = fields.Binary(
        string="Attachment",
        readonly=True
    )

    idv_value = fields.Float(
        string="IDV value"
    )
    policy_type = fields.Selection(
        selection=[
            ('vehicle', 'Vehicle'),
            ('health', 'Health'),
            ('corporate', 'SME')
        ],
        string="Policy Type",
    )
    od_amount = fields.Float(
        string="OD Amount",
    )
    addon_amount = fields.Float(
        string="Addon Amount",
    )

    cac_amount = fields.Float(
        string='CAC Amount',
    )

    third_party = fields.Float(
        string="Third Party",
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
    company_id = fields.Many2one(
        'res.company',
        string="Company",
    )

    agency_agent_id = fields.Many2one(
        'res.partner',
        string='Agency Agent',
        domain=[('partner_type', '=', 'insurance_company_agent')],
    )
    owd_amount = fields.Float(
        string="OWD Amount",
    )
    bank_id = fields.Many2one(
        'payment.bank',
        string='Payment Bank',
    )
    payment_method = fields.Char(
        string="Payment Method",
    )
    department_remark = fields.Selection(
        selection=[
            ('renewal', 'RENEWAL'),
            ('fresh', 'FRESH'),
            ('rollover', 'ROLLOVER'),
            ('endorsement', 'ENDORSEMENT'),
            ('cancelled', 'CANCELLED'),
        ],
        copy=False,
        string="Department Remark",
    )
    agent_remark = fields.Text(
        string="Agent Remark"
    )
    document_verified = fields.Boolean(
        copy=True,
        string="Document Verified?",
    )
    policy_date = fields.Date(
        string='Policy Date',
        default=fields.Date.context_today,
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

    # partner_relative_ids = fields.Many2many(
    #     'partner.relative.lines',
    #     string='Partner Relative'
    # )
    @api.onchange('od_amount', 'addon_amount')
    def onchange_owd_amount(self):
        for rec in self:
            rec.owd_amount = rec.od_amount + rec.addon_amount

    @api.depends(
        'gross_premimum',
        'commission_rate',
        'od_amount',
        'addon_amount'
    )
    def _get_commission_amount(self):
        for line in self:
            commissionable_amount = line.gross_premimum
            if line.policy_type == 'vehicle':
                commissionable_amount = line.gross_premimum - line.third_party
            line.commission_amount = (commissionable_amount * line.commission_rate) / 100.0

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        if self.filtered(
                lambda reward: (
                        reward.commission_rate < 0 or reward.commission_rate > 100
                )
        ):
            raise ValidationError(
                _('Commission Percentage should be between 1-100')
            )

    #     @api.constrains('policy_number')
    #     def _check_policy_number(self):
    #         if not self.policy_number:
    #             raise ValidationError(
    #                 _('Please add the policy number'))

    def action_convert_policy(self):
        act_read = self.env.ref(
            'qno_insurance_management.action_sale_policy_detail_wizard'
        ).sudo().read([])[0]
        return act_read

    def action_confirm_insurance(self):
        if self.gross_premimum > 0:
            self.state = 'confirmed'
            self.hide_inv_button = True
        else:
            raise UserError(_("Amount should be greater than zero"))

    def write(self, vals):
        super_res = super(InsurancePolicy, self).write(vals)
        if 'commission_rate' in vals:
            for record in self:
                record.action_create_invoice()
        return super_res

    def action_print_policy(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/insurance.policy/%s/policy_document/policy_document.pdf?download=true' % (self.id),
            'name': self.name,
        }

    def action_create_invoice(self):
        if self.commission_rate <= 0:
            raise ValidationError(_('Please add valid commission rate!'))

        #         amount = (self.gross_premimum * self.commission_rate) / 100.0
        amount = self.commission_amount
        account = self.env.ref('l10n_in.1_p20013').sudo().read([])[0]
        created_invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.context_today(self),
            'partner_id': self.policy_product_id.insurance_company_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': 'Invoice for commission on policy %s' % (
                    self.policy_number
                ),
                'quantity': 1,
                'price_unit': amount,
                'account_id': account['id'],
                'tax_ids': []
            })],
        })
        self.update({
            'invoice_status': 'invoiced',
            'invoice_ids': created_invoice
        })
        created_invoice._post(soft=False)

    def action_close_insurance(self):
        for records in self.invoice_ids:
            if records.state == 'paid':
                raise UserError(_("All invoices must be paid"))
        self.update({
            'state': 'closed',
            'end_date': fields.Date.context_today(self),
            'hide_inv_button': False
        })

    def action_renew_policy(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read([])[0]
        form_view = [(self.env.ref('qno_insurance_management.view_order_policy_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view

        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_agent_id': self.agent_id.id,
            'default_policy_type': self.policy_type,
            'default_vehicle_number': self.vehicle_number,
            'default_vehicle_manufacturing_year': self.vehicle_manufacturing_year,
            'default_vehicle_model': self.vehicle_model,
            'default_vehicle_make': self.vehicle_make,
            'default_idv_value': self.idv_value,
        }

        return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'insurance.details') or 'New'
        return super(InsurancePolicy, self).create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You can not delete non-draft policies!'))
        return super(InsurancePolicy, self).unlink()

    @api.model
    def insurance_policy_stage_status(self):
        today_date = str(date.today())
        search_end_date = datetime.strptime(today_date, '%Y-%m-%d').date()
        self.search([
            ('end_date', '<', search_end_date),
            ('invoice_ids.state', '!=', 'paid')
        ]).write({'state': 'closed'})
        self.search([
            ('start_date', '<=', search_end_date),
            ('state', '=', 'draft'),
            ('gross_premimum', '>', 0)
        ]).write({'state': 'confirmed'})

    @api.model
    def customer_policy_expire_15_daya(self):
        today = date.today()
        after_15_day = today + relativedelta(days=15)
        policy = self.search([('end_date', '>=', today), ('end_date', '<=', after_15_day)])
        for rec in policy:
            template_id = self.env.ref('qno_insurance_management.customer_policy_expire_15_daya_template')
            template_id.send_mail(rec.id)

    @api.model
    def customer_policy_expire_7_daya(self):
        today = date.today()
        after_7_day = today + relativedelta(days=7)
        policy = self.search([('end_date', '>=', today), ('end_date', '<=', after_7_day)])
        for rec in policy:
            template_id = self.env.ref('qno_insurance_management.customer_policy_expire_15_daya_template')
            template_id.send_mail(rec.id)

    @api.model
    def customer_policy_expire_2_daya(self):
        today = date.today()
        after_2_day = today + relativedelta(days=2)
        policy = self.search([('end_date', '>=', today), ('end_date', '<=', after_2_day)])
        for rec in policy:
            template_id = self.env.ref('qno_insurance_management.customer_policy_expire_15_daya_template')
            template_id.send_mail(rec.id)

    @api.model
    def customer_policy_expire_1_daya(self):
        today = date.today()
        after_1_day = today + relativedelta(days=1)
        policy = self.search([('end_date', '>=', today), ('end_date', '<=', after_1_day)])
        for rec in policy:
            template_id = self.env.ref('qno_insurance_management.customer_policy_expire_15_daya_template')
            template_id.send_mail(rec.id)

    @api.model
    def customer_policy_suggested_product(self):
        today = date.today()
        policy = self.search([])
        for rec in policy:
            after_1_month = rec.start_date + relativedelta(months=1)
            if after_1_month == today:
                template_id = self.env.ref('qno_insurance_management.customer_suggested_mail_template')
                template_id.send_mail(rec.id)


class PolicyDetailsHolder(models.Model):
    _name = "policy.details.holder"
    _inherit = ['mail.thread']
    _description = "Policy Details Holder"

    relation_id = fields.Many2one(
        'partner.relative.relation',
        string="Relation",
        required=True
    )
    name = fields.Char(
        string="Name",
        required=True
    )
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        string='Gender',
        tracking=True
    )
    date_of_birth = fields.Date(
        string='Date of Birth'
    )
    age = fields.Float(
        string='Age',
        tracking=True,
        compute='age_compute'
    )
    sum_assured = fields.Monetary(
        string='Sum Assured'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    policy_id = fields.Many2one(
        'insurance.policy'
    )

    order_id = fields.Many2one(
        'sale.order'
    )

    # @api.onchange('date_of_birth')
    # def onchange_date_of_birth(self):
    #     for rec in self:
    #         today = date.today()
    #         if rec.date_of_birth:
    #             rec.age = today.year - rec.date_of_birth.year
    #         else:
    #             rec.age = 0

    @api.depends('date_of_birth')
    def age_compute(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0
