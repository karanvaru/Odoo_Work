from odoo import models, fields, api, _
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find, geo_query_address)


class CRM(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'portal.mixin']

    bid_closing_date = fields.Datetime(
        'Bid Closing Date & Time'
    )
    date_deadline = fields.Date(
        required=False
    )
    # x_studio_product_category = fields.Selection(
    #     [
    #         ("Edge PC", "Edge PC"),
    #         ("ThinPad", "ThinPad"),
    #         ("Gaming PC", "Gaming PC"),
    #         ("Server", "Server "),
    #         ("Workstation", "Workstation"),
    #         ("Software Products", "Software Products"),
    #         ("Support Packs", "Support Packs"),
    #         ("IoT", "IoT"),
    #         ("Accessories", "Accessories"),
    #         ("Others", "Others"),
    #         ("XL Series", "XL Series"),
    #         ("Laptop", "Laptop"),
    #         ("Tablet", "Tablet"),
    #         ("Desktop/AIO", "Desktop/AIO"),
    #         ("Other", "Other"),
    #         ("SBC", "SBC"),
    #         ("Servers", "Servers")
    #     ],
    #     "Category"
    # )
    # x_studio_quantity = fields.Float(
    #     "Quantity"
    # )
    value = fields.Float(
        'Value'
    )
    crm_product_category_id = fields.Many2one(
        'crm.product.category',
        string="Product Category"
    )
    # x_studio_opportunity_type_1 = fields.Selection(
    #     [
    #         ("Runrate", "Runrate"),
    #         ("Volume", "Volume"),
    #         ("Project", "Project")
    #     ],
    #     'Opportunity Type',
    # )
    gem_customer_name = fields.Char(
        "GeM Customer Name"
    )
    customer_city = fields.Char(
        "Customer City"
    )
    customer_pincode = fields.Char(
        "Customer Pincode"
    )
    customer_state_id = fields.Many2one(
        'res.country.state',
        string="Customer State"
    )
    # x_studio_mobile = fields.Char()
    # x_studio_gem_model_no = fields.Char(
    #     "GeM Model No."
    # )
    # x_studio_gem_sku = fields.Char(
    #     "GeM SKU"
    # )
    # x_studio_catalog_id = fields.Char(
    #     "GeM Catalog ID"
    # )
    gem_customer_id = fields.Many2one(
        'res.partner',
        domain=[('is_gem_cust', '=', True)]
    )
    is_master_opportunity = fields.Boolean(
        default=False,
        string="Is Master Opportunity",
        copy=False
    )
    sales_executive_ids = fields.Many2many(
        'res.users',
        string="Picked By"
    )

    is_participated = fields.Boolean(
        "IS Participated",
        default=False,
    )
    is_l1 = fields.Boolean(
        "IS L1",
        default=False
    )
    is_contract_received = fields.Boolean(
        "IS Contract Recvd",
        default=False
    )
    is_bid_lost = fields.Boolean(
        "IS Lost",
        default=False
    )
    is_paired_catelog = fields.Boolean(
        "Is Catalog Paired"
    )
    master_latitude = fields.Float(
        string='Master Latitude',
        digits=(16, 5)
    )
    master_longitude = fields.Float(
        string='Master Longitude',
        digits=(16, 5)
    )
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
        string="Bid To RA Enabled",
        copy=True
    )
    bid_type_id = fields.Many2one(
        'crm.bid.type',
        string="Bid Type",
        copy=True
    )
    mii_purchase_preference = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='MII Purchase Preference')

    @api.onchange('customer_pincode', 'customer_state_id')
    def set_master_lati_long(self):
        for rec in self:
            rec.get_geo_master_location()

    def get_geo_master_location(self):
        google_api_key = self.env['ir.config_parameter'].sudo().get_param(
            'google.api_key_geocode', default='')
        for lead in self.with_context(lang='en_US'):
            country_india = self.env.ref("base.in")
            result = geo_find(
                addr=geo_query_address(
                    zip=lead.customer_pincode,
                    state=lead.customer_state_id.name,
                    country=country_india.name
                ),
                apikey=google_api_key)
            if result is None:
                result = geo_find(
                    addr=geo_query_address(
                        state=lead.customer_state_id.name,
                        country=country_india.name),
                    apikey=google_api_key)
            if result:
                lead.write({
                    'master_latitude': result[0],
                    'master_longitude': result[1]
                })

    def init(self):
        try:
            insert_sql = """
                    UPDATE crm_lead set x_studio_quantity=0 where x_studio_quantity is NULL; 
                    """
            self.env.cr.execute(insert_sql)
            self._cr.commit()
        except Exception as e:
            pass

    def set_oppor_stage_contract_received(self):
        for rec in self:
            rec.is_contract_received = True
            stage_id = rec.stage_id.search(['|', ('team_id', '=', rec.team_id.id), ('team_id', '=', False),
                                            ('portal_stage', 'in', ['contract_received'])], limit=1)
            if stage_id:
                rec.stage_id = stage_id.id
            else:
                rec.stage_id = rec.stage_id.id

    def set_oppor_stage_paired_catelog(self):
        for rec in self:
            rec.is_paired_catelog = True
            stage_id = rec.stage_id.search(['|', ('team_id', '=', rec.team_id.id), ('team_id', '=', False),
                                            ('portal_stage', 'in', ['paired_catelog'])], limit=1)
            if stage_id:
                rec.stage_id = stage_id.id
            else:
                rec.stage_id = rec.stage_id.id

    def set_oppor_stage_l1(self):
        for rec in self:
            self.is_l1 = True
            stage_id = rec.stage_id.search(
                ['|', ('team_id', '=', rec.team_id.id), ('team_id', '=', False), ('portal_stage', 'in', ['l1'])],
                limit=1)
            if stage_id:
                rec.stage_id = stage_id.id
            else:
                rec.stage_id = rec.stage_id.id

    def set_oppor_stage_participated(self):
        for rec in self:
            rec.is_participated = True
            stage_id = rec.stage_id.search(['|', ('team_id', '=', rec.team_id.id), ('team_id', '=', False),
                                            ('portal_stage', 'in', ['participated'])], limit=1)
            if stage_id:
                rec.stage_id = stage_id.id
            else:
                rec.stage_id = rec.stage_id.id

    def preview_crm_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.access_url,
        }

    def _compute_access_url(self):
        super(CRM, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/crm/%s' % (order.id)

    @api.onchange('gem_customer_id')
    def onchange_gem_customer_id(self):
        for rec in self:
            if rec.gem_customer_id:
                rec.gem_customer_name = rec.gem_customer_id.name

    def assign_new_partner(self, partner_ids):
        try:
            temp_id = self.env.ref('studio_customization.gem_bid_details_to_c_e79c3678-d653-432f-b98a-c4e6cf514d96')
        except:
            temp_id = False
            pass
        for rec in self:
            attachments = self.env['ir.attachment'].search([('res_model', '=', rec._name), ('res_id', '=', rec.id)])
            for partner in partner_ids:
                new_copy_list = ['x_studio_quantity', 'x_studio_opportunity_type_1', 'x_studio_gem_model_no',
                                 'x_studio_gem_sku', 'x_studio_catalog_id']
                copy_vals = {
                    'partner_id': partner.id,
                    'user_id': self.env.user.id,
                    'is_master_opportunity': False,
                    'sales_executive_ids': [(6, 0, rec.sales_executive_ids.ids)],
                    'crm_product_category_id': rec.crm_product_category_id.id
                }
                for field in new_copy_list:
                    if field in rec._fields:
                        copy_vals.update({
                            field: rec[field]
                        })
                new_id = rec.copy(copy_vals)
                if temp_id:
                    new_id.message_post_with_template(
                        temp_id.id,
                        message_type='comment', composition_mode='comment'
                    )
                for attact in attachments:
                    attact.sudo().copy({
                        'res_model': new_id._name,
                        'res_id': new_id.id
                    })

    def _cron_send_mail_reminder(self):
        template_id = self.env.ref("studio_customization.gem_congrats_email_f_383c6dd9-919f-49e6-b15f-24299490ea6e")
        if template_id:
            stage_id = self.env['crm.stage'].search([('portal_stage', '=', 'l1')], limit=1)
            if stage_id:
                crm_leads_ids = self.env['crm.lead'].search(
                    [('stage_id', '=', stage_id.id), ('is_master_opportunity', '=', False)])
                for rec in crm_leads_ids:
                    template_id.send_mail(rec.id)


class CRM_Stage(models.Model):
    _inherit = 'crm.stage'

    portal_stage = fields.Selection(
        [
            ('participated', 'Participated'),
            ('l1', 'L1'),
            ('contract_received', 'Contract RECEIVED'),
            ('bid_lost', 'Bid Lost'),
            ('paired_catelog', 'Catalog Paired '),
            ('other', 'Other')
        ],
        string="Stage Type"
    )
