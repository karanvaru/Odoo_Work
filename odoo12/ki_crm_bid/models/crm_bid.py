from odoo import models, fields, api, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.crm.models import crm_stage
import datetime


class CRM_BID(models.Model):
    _name = 'crm.bid'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin',
                'mail.blacklist.mixin']
    _primary_email = ['email_from']

    def _default_probability(self):
        return 10

    name = fields.Char('Bid', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', track_sequence=1,
                                 index=True,
                                 help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    active = fields.Boolean('Active', default=True, track_visibility=True)
    email_from = fields.Char('Email', help="Email address of the contact", track_visibility='onchange',
                             track_sequence=4, index=True)
    website = fields.Char('Website', index=True, help="Website of the contact")
    description = fields.Text('Notes')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")

    probability = fields.Float('Probability', group_operator="avg", copy=False,
                               default=lambda self: self._default_probability())
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', track_visibility='always')
    expected_revenue = fields.Monetary('Prorated Revenue', currency_field='company_currency', store=True,
                                       compute="_compute_expected_revenue")
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.",
                                required=False)

    # Fields for address, due to separation from crm and res.partner
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char('Phone', track_visibility='onchange', track_sequence=5)
    mobile = fields.Char('Mobile')
    function = fields.Char('Job Position')
    title = fields.Many2one('res.partner.title')
    lost_reason = fields.Many2one('crm.lost.reason', string='Lost Reason', index=True, track_visibility='onchange')

    # web Fields
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              default=lambda self: self.env.user, required=True,  domain=[('active', '=', True)])
    team_id = fields.Many2one('crm.team', string='Sales Team',
                              default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(
                                  user_id=self.env.uid),
                              index=True, track_visibility='onchange',
                              help='When sending mails, the default email address is taken from the Sales Team.',
                              required=True)
    bid_closing_date = fields.Datetime(
        'Bid Closing Date & Time',
        required=True,
        track_visibility='onchange',
        track_sequence=2
    )
    x_studio_product_category = fields.Selection(
        [
            ("Edge PC", "Edge PC"),
            ("Remote PC", "Remote PC"),
            ("Desk PC", "Desk PC"),
            ("ThinBook", "ThinBook"),
            ("ThinPad", "ThinPad"),
            ("Gaming PC", "Gaming PC"),
            ("Server", "Server "),
            ("Workstation", "Workstation"),
            ("Software Products", "Software Products"),
            ("Support Packs", "Support Packs"),
            ("IoT", "IoT"),
            ("Accessories", "Accessories"),
            ("Others", "Others"),
            ("XL Series", "XL Series"),
            ("Laptop", "Laptop"),
            ("Tablet", "Tablet"),
            ("Desktop/AIO", "Desktop/AIO"),
            ("Other", "Other"),
            ("SBC", "SBC"),
            ("Servers", "Servers")
        ],
        "Category",
        # track_visibility='onchange',
        # track_sequence=3,
        # required=True
    )
    crm_product_category_id = fields.Many2one(
        'crm.product.category',
        string="Product Category",
        track_visibility='onchange',
        track_sequence=3,
        required=True
    )
    x_studio_quantity = fields.Float(
        "Quantity",
        track_visibility='onchange',
        track_sequence=6,
        required=True
    )
    value = fields.Float(
        'Value',
        track_visibility='onchange',
        track_sequence=7,
        required=True
    )
    x_studio_opportunity_type_1 = fields.Selection(
        [
            ("Runrate", "Runrate"),
            ("Volume", "Volume"),
            ("Project", "Project")
        ],
        'Opportunity Type',
        required=True
    )
    gem_customer_name = fields.Char(
        "GeM Customer Name",
        track_visibility='onchange',
        track_sequence=8,
        required=True
    )
    customer_city = fields.Char(
        "Customer City",
        track_visibility='onchange',
        track_sequence=9,
        required=True
    )
    customer_pincode = fields.Char(
        "Customer Pincode",
        track_visibility='onchange',
        track_sequence=10,
        required=True
    )
    customer_state_id = fields.Many2one(
        'res.country.state',
        string="Customer State",
        track_visibility='onchange',
        track_sequence=11,
        required=True
    )
    x_studio_gem_model_no = fields.Char(
        "GeM Model No.",
        track_visibility='onchange',
        track_sequence=12,
    )
    x_studio_gem_sku = fields.Char(
        "GeM SKU",
        track_visibility='onchange',
        track_sequence=13,
    )
    x_studio_catalog_id = fields.Char(
        " GeM Catalog ID (Intel)",
        track_visibility='onchange',
        track_sequence=14,
    )
    catalog_id_amd = fields.Char(
        "GeM Catalog ID (AMD)",
        track_visibility='onchange',
        track_sequence=14,
    )
    gem_customer_id = fields.Many2one(
        'res.partner',
        domain=[('is_gem_cust', '=', True)]
    )
    crm_lead_id = fields.Many2one(
        'crm.lead',
        readonly=True,
        copy=False
    )
    sales_executive_ids = fields.Many2many(
        'res.users',
        string="Picked By"
    )
    file_upload = fields.Binary(
        "File Upload",
        copy=False
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('opportunity', 'Opportunity')
        ],
        default='draft',
        track_visibility='onchange',
        track_sequence=15,
    )
    #----------------pavan---------------

    mii_purchase_preference = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='MII Purchase Preference')

    crm_mii_content_id = fields.Many2one(
        'crm.mii.content',
        string="MII Content Required"
    )
    crm_capture_type_id = fields.Many2one(
        'crm.capture.type',
        string="Bid Capture Type"
    )
    crm_category_type_id = fields.Many2one(
        'crm.category.type',
        string="Bid Category Type"
    )
    bid_to_ra_id = fields.Many2one(
        'crm.bid.ra',
        string="Bid To RA Enabled"
    )
    bid_type_id = fields.Many2one(
        'crm.bid.type',
        string="Bid Type"
    )
    ########pavan######
    bid_published_date = fields.Datetime(string="Bid Published Date")
    priority = fields.Selection(crm_stage.AVAILABLE_PRIORITIES, string='Priority', index=True,
                                default=crm_stage.AVAILABLE_PRIORITIES[0][0])

    _sql_constraints = [
        ('check_probability', 'check(probability >= 0 and probability <= 100)',
         'The probability of closing the deal should be between 0% and 100%!')
    ]

    @api.depends('planned_revenue', 'probability')
    def _compute_expected_revenue(self):
        for lead in self:
            lead.expected_revenue = round((lead.planned_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)

    @api.multi
    def preview_crm_Bid(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.access_url,
        }

    def _compute_access_url(self):
        super(CRM_BID, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/bid/%s' % (order.id)

    def get_crm_oppoptunity_values(self):
        vals = self.copy_data()[0]
        fild_list = self.env['crm.lead'].fields_get()
        for val in list(vals.keys()):
            if not val in list(fild_list.keys()):
                vals.pop(val)
        return vals

    def action_master_opportunity(self, for_website=False):
        attach_sudo = self.env['ir.attachment']
        for rec in self:
            if not for_website:
                if not rec.x_studio_gem_model_no or not rec.x_studio_gem_sku or not rec.x_studio_catalog_id:
                    raise ValidationError(_("GeM Fields Missing Model No./SKU/Catalog ID"))
            vals = rec.get_crm_oppoptunity_values()
            vals.update({
                'is_master_opportunity': True,
                'user_id': self.env.user.id,
                'partner_id': self.env.user.partner_id.id,
                'sales_executive_ids': [(6, 0, rec.sales_executive_ids.ids)],
                'type': 'opportunity',
                'planned_revenue': rec.value
            })
            crm_lead_id = self.env['crm.lead'].create(vals)
            if crm_lead_id:
                rec.crm_lead_id = crm_lead_id.id
                rec.state = 'opportunity'
                attachments = attach_sudo.search([('res_model', '=', rec._name), ('res_id', '=', rec.id)])
                for attact in attachments:
                    attact.sudo().copy({
                        'res_model': crm_lead_id._name,
                        'res_id': crm_lead_id.id
                    })
                crm_lead_id.set_master_lati_long()

    @api.onchange('gem_customer_id')
    def onchnage_gem_customer_id(self):
        for rec in self:
            if rec.gem_customer_id:
                rec.gem_customer_name = rec.gem_customer_id.name

    def init(self):
        rule = self.env.ref('crm.crm_rule_personal_lead')
        if rule:
            rule.domain_force = "['|','|',('user_id','=',user.id),('user_id','=',False),('partner_id','=',user.partner_id.id)]"
