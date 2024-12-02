# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime


class SourcingMaster(models.Model):
    _name = "sourcing.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sourcing Master'

    name = fields.Char('Name', default=lambda self: _('New'), store=True, track_visibility='onchange')
    vendor = fields.Many2one('res.partner', string='Vendor')
    nature = fields.Many2many('vendor.nature', string='Nature', track_visibility='onchange')
    vendor_components = fields.Many2many('vendor.components', string='Trading Components', track_visibility='onchange')
    vendor_geo = fields.Selection([
        ('international', 'International'),
        ('domestic', 'Domestic'),
    ], string='Vendor Geo')
    state = fields.Selection(
        [('new', 'New'), ('inprogress', 'Inprogress'), ('mvl', 'MVL'), ('avl', 'AVL'), ('scrapped', 'Scrapped'),
         ('bank', 'Bank')],
        default='new', track_visibility='onchange')

    component_vendor = fields.Many2many('component.vendor', string='Component Vendor', track_visibility='onchange')
    quality_grade = fields.Many2many('quality.grade', string='Quality Grades', track_visibility='onchange')
    qiqo = fields.Selection([
        ('aplusplus', 'A++'),
        ('aplus', 'A+'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
    ], string='QIQO')
    brand_ids = fields.Many2many('product.brand.amz.ept', 'product_brand_amz_ept_sourcing_master_rel',
                                 string='Trading Brands',
                                 track_visibility='always')
    website = fields.Char(string="Website")
    vendor_operations_ids = fields.Many2many('vendor.operations', 'sourcing_master_vendor_operations',
                                             string="Vendor Operations",
                                             track_visibility='always')
    #need to convert field in contacts
    last_2_yr_avg_revenue_in_crores = fields.Char(string="Last 2 Yr Avg Revenue (in Cr)", track_visibility='always')
    vendor_head_count = fields.Integer(string="Vendor Head Count", store=True)
    product_category_ids = fields.Many2many('product.category', 'product_category_sourcing_master_rel',
                                            string='Product Category', track_visibility='always')
    qiqo_ids = fields.Many2many('sourcing.qiqo', 'sourcing_master_qiqo_rel', string="QIQO",
                                track_visibility='always', store=True)

    standardization_type_ids = fields.Many2many('standardization.type', 'sourcing_master_standardization_type_rel',
                                                string="Standardization Type",
                                                track_visibility='always',store=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms", track_visibility='always', store=True)
    ppt_rating = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
        ('excellent', 'Excellent'),
        ('awesome', 'Awesome'),
    ], string="PPT Rating", track_visibility='always')
    established_in = fields.Date(string="Established In", track_visibility='always')
    years_in_business = fields.Char(string="Years in Business", compute="no_years_in_business")
    company_profile_last_attached = fields.Date(string="Company Profile Last Attached", track_visibility='always')
    roadmap_last_attached = fields.Date(string="Roadmap Last Attached", track_visibility='always')
    # need to convert field in contacts
    top_5_customers_for_reference = fields.Char(string="Top 5 Customers (for Reference)", track_visibility='always')
    rdp_spoc_id = fields.Many2one('res.partner', string="RDP SPOC", track_visibility='always')
    vendor_spoc_id = fields.Many2one('res.partner', string="Vendor SPOC", track_visibility='always')
    nd_components_ids = fields.Many2many('vendor.components', 'sourcing_master_vendor_components_rel',
                                          string="ND Components", track_visibility='always')
    nd_brands_ids = fields.Many2many('product.brand.amz.ept', 'product_brand_amz_ept_sourcing_master_rel',
                                     string="ND Brands",
                                     track_visibility='always')
    rd_components_ids = fields.Many2many('vendor.components', 'sourcing_master_vendor_components_rel',
                                         string="RD Components", track_visibility='always')
    rd_brands_ids = fields.Many2many('product.brand.amz.ept', 'product_brand_amz_ept_sourcing_master_rel',
                                      string="RD Brands",
                                     track_visibility='always')
    notes = fields.Text('Notes')

    street = fields.Char(string="Street", compute="compute_contact")
    street_two = fields.Char(string="Street2", compute="compute_contact")
    city = fields.Char(string="City", compute="compute_contact")
    state_name = fields.Char(string="State Name", compute="compute_contact")
    country = fields.Many2one('res.country', string="Country", compute="compute_contact")
    image = fields.Binary(string="Image")

    #

    # @api.depends('established_in')
    # def no_years_in_business(self):
    #     for record in self:
    #         if record['established_in']:
    #             record['years_in_business'] = date.today() - record['established_in']
    #             record['years_in_business'] = record['years_in_business'].split(' ')[0]
    #             if record['years_in_business']:
    #                 new_date = int(record['years_in_business'])
    #                 years = new_date // 365
    #                 months = (new_date % 365) // 30
    #                 record['years_in_business'] = str(str(years) + ' Years, ' + str(months) + ' Months')

    @api.depends('established_in')
    def no_years_in_business(self):
        for record in self:
            if record['established_in']:
                years_in_business = date.today() - record['established_in']
                years = years_in_business.days // 365
                months = (years_in_business.days % 365) // 30
                record['years_in_business'] = str(years) + ' Years, ' + str(months) + ' Months'

    supply_type = fields.Selection([
        ('standard_components', 'Standard Components'),
        ('back2back', 'Back2Back'),
    ], string='Supply Type')

    c_user = fields.Boolean('user', compute='compute_user_allowed')
    closed_date = fields.Datetime(string="Closed Date")
    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('sourcing.master.sequence'),
        })
        return super(SourcingMaster, self).create(vals)

    @api.multi
    def compute_user_allowed(self):
        # for rec in self:
        user_id = self.env.user.id
        if user_id in [6, 54, 16, 17, 8865]:
            self.c_user = True

    @api.multi
    def button_inprogress(self):
        for rec in self:
            rec.state = 'inprogress'

    @api.multi
    def button_mvl(self):
        for rec in self:
            rec.state = 'mvl'

    @api.multi
    def button_avl(self):
        for rec in self:
            rec.state = 'avl'

    @api.multi
    def button_scrapped(self):
        for rec in self:
            rec.state = 'scrapped'

    @api.multi
    def button_bank(self):
        for rec in self:
            rec.state = 'bank'

    @api.depends('vendor')
    def compute_contact(self):
        for rec in self:
            rec.street = rec.vendor.street
            rec.street_two = rec.vendor.street2
            rec.city = rec.vendor.city
            rec.state_name = rec.vendor.state_id.name
            rec.country = rec.vendor.country_id
            rec.image = rec.vendor.image
            # rec.last_2_yr_avg_revenue_in_crores = rec.vendor.last_2_yr_avg_revenue_in_crores
            # rec.top_5_customers_for_reference = rec.vendor.top_5_customers_for_reference







class VendorNature(models.Model):
    _name = 'vendor.nature'
    name = fields.Char(required=True)


class VendorComponents(models.Model):
    _name = 'vendor.components'
    name = fields.Char(required=True)


class ComponentVendor(models.Model):
    _name = 'component.vendor'
    name = fields.Char(required=True)


class QualityGrade(models.Model):
    _name = 'quality.grade'
    name = fields.Char(required=True)


class VendorOperations(models.Model):
    _name = 'vendor.operations'
    _description = "Vendor Operations"

    name = fields.Char(required=True)


class Qiqo(models.Model):
    _name = 'sourcing.qiqo'
    _description = "QIQO"

    name = fields.Char(required=True)


class StandardizationType(models.Model):
    _name = 'standardization.type'
    _description = "Standardization Type"

    name = fields.Char(required=True)
