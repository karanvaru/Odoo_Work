# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class RDPExit14(models.Model):
    _name = "rdp.exit14"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'RDP EXit 14'
    _order = 'id desc'

    name = fields.Char('Name', default=lambda self: _('New'), store=True, track_visibility='onchange')
    vendor = fields.Many2one('res.partner', 'Vendor', store=True)
    address = fields.Char(string='Address', readonly='True', compute='compute_address')
    vendor_product_category = fields.Many2one('vendorproduct.category', string='Vendor Product / Service Category',
                                              track_visibility='onchange')
    category_type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service'),
        ('other', 'Other'),
    ], string='Product/Service', default='product')
    notes = fields.Text(string='Notes', store=True, track_visibility='onchange')
    address = fields.Char(string='Address', readonly='True', compute='compute_address')
    city = fields.Char(string='City', readonly='True', compute='compute_address')
    state_id = fields.Many2one('res.country.state', string='State', readonly='True', compute='compute_address')
    country_id = fields.Many2one('res.country', string='Country', readonly='True', compute='compute_address')
    website = fields.Char(string="Website")
    mc_nda_signed = fields.Boolean(string="MC NDA Signed")
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Low"), ("2", "High"), ("3", "Very High"), ("excellent", "Excellent"),
         ("excellent_plus", "Excellent Plus")], string="Vendor Quality")
    tags_ids = fields.Many2many('fm.tags', string="Tags")
    vendor_relation = fields.Selection([("New", "New"), ("Existing", "Existing"), ("Other", "Other")],
                                       string="Vendor Relation")
    quick_reference_prices = fields.Text(string="Quick Reference Prices")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    state = fields.Char(string="Test")
    category_id = fields.Many2one('fm.category','Category',track_visibility="onchange")
    sub_category_id = fields.Many2one('fm.subcategory','Sub Category',track_visibility="onchange")
    product_type_id = fields.Many2one('fm.product.type',string='Product Type',track_visibility="always")
    department_id = fields.Many2one('hr.department', 'Department')

    @api.depends('vendor')
    def compute_address(self):
        for rec in self:
            # rec.street = rec.env['res.partner'].sudo().search([('user_id', '=', rec.env.uid)])
            rec.address = str(rec.vendor.street) + ' ' + str(rec.vendor.street2) + ' ' + str(rec.vendor.zip)
            rec.city = rec.vendor.city
            rec.state_id = rec.vendor.state_id
            rec.country_id = rec.vendor.country_id

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('rdp.exit14.sequence'),
        })
        return super(RDPExit14, self).create(vals)


class VendorProductCategory(models.Model):
    _name = 'vendorproduct.category'
    name = fields.Char(required=True)


class RdpExitMany2many(models.Model):
    _name = "fm.tags"
    _description = " RDP Exit14 FM Tags"

    name = fields.Char(string='Name')


class FMCategory(models.Model):
    _name = "fm.category"
    _description = "FM Category"

    name = fields.Char('Name')


class FMSubCategory(models.Model):
    _name = "fm.subcategory"
    _description = "FM Subcategory"

    name = fields.Char('Name')


class FMSubCategory(models.Model):
    _name = "fm.product.type"
    _description = "FM Product Type"

    name = fields.Char('Name')


class FMDepartment(models.Model):
    _name = "fm.department"
    _description ="FM Admin Department"

    name = fields.Char('Name')






