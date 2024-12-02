# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ASPPartner(models.Model):
    _name = "asp.partner"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ASP Partner'

    name = fields.Char('Name', default=lambda self: _('New'), store=True,track_visibility='onchange')
    vendor = fields.Many2one('res.partner',string='Vendor')
    street = fields.Char( string='Street', track_visibility='onchange')
    street2 = fields.Char(string='Street2', track_visibility='onchange')
    city = fields.Char(string='City',track_visibility='always')
    state_id = fields.Many2one('res.country.state', string='State id')
    # state = fields.Char(string='State', related='vendor.state.name', readonly=True, track_visibility='onchange')
    # country = fields.Char('Country', related='vendor.country.name', readonly=True, track_visibility='onchange')
    asc_portal_access = fields.Boolean('ASC Portal Access')
    rma_center = fields.Boolean('RMA Center')
    is_active = fields.Boolean('Is Active')

    service_product_cat = fields.Many2many('service.product_cat', string='Service Product Categories', track_visibility='onchange')
    service_states = fields.Many2many('res.country.state', string='Serviceable states/cities', track_visibility='onchange')
    service_dist = fields.Many2many('service.districts', string='Serviceable Districts', track_visibility='onchange')
    service_types = fields.Many2one('service.types',string='Serviceable Types', track_visibility='onchange')
    service_categories = fields.Many2many('service.categories', string='Service Categories', track_visibility='onchange')
    service_delivery_by = fields.Many2many('service.delivery_by', string='Service Delivery By', track_visibility='onchange')
    priority = fields.Selection([
        ('0','Low'),
        ('1','Normal'),
        ('2','High'),
        ('3','Very High'),
        ('4','Excelent '),
        ('5','Awesome'),
    ], string='PPT', track_visibility='always')
    status= fields.Selection([
        ('draft', 'Draft'), 
        ('inprogress', 'In Progress'),
        ('active', 'Active'),
        ('onhold','On Hold'),
        ('inactive', 'Inactive'),
        ('close', 'Close'),
        ('cancel', 'Cancel')

    ], string='Status', readonly=True, default='draft',track_visibility='always')
    regironal_category = fields.Selection([
         ('national', 'National Player'), 
        ('regional', 'Regional Player'),
        ('multiregional', 'Multi Regional Player'),
        ('rdpfe','RDP FE')
    ], string='ASP Category',track_visibility='always')

    notes = fields.Text('Notes',track_visibility='always')

    spoc = fields.Many2one('res.partner', string='SPOC', track_visibility='onchange')
    md_ceo_director = fields.Many2one('res.partner',string='MD/CEO/Director/Owner', track_visibility='onchange')
    spoc_alternate = fields.Many2one('res.partner',string='SPOC Alternate', track_visibility='onchange')

    asp_other_brands = fields.Many2many('product.brand.amz.ept', string='ASP Other Brands')
    number_of_engineers = fields.Char('Number of Engineers')
    no_of_years = fields.Char('Number of years in Service')


    @api.model
    def create(self, vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('asp.partner.sequence'),
		})
        return super(ASPPartner, self).create(vals)

    @api.multi 
    def action_to_inprogress(self):
        self.status = "inprogress"   

    @api.multi 
    def action_to_active(self):
        self.status = "active"    

    @api.multi 
    def action_to_inactive(self):
        self.status = "inactive"    

    @api.multi 
    def action_to_close(self):
        self.status = "close"   

    @api.multi 
    def action_to_cancel(self):
        self.status = "cancel"    
    @api.multi
    def action_set_draft(self):
        self.write({'status': 'draft'}) 

    @api.multi
    def action_to_onhold(self):
        self.status = "onhold" 
        # raise ValidationError("Are sure you want move the stage?")
   
        
        
      
           
     

     

class ServiceProductCategory(models.Model):
    _name = 'service.product_cat'
    name = fields.Char(required=True)

class ServiceTypes(models.Model):
    _name = 'service.types'
    name = fields.Char(required=True)

class ServicableDistricts(models.Model):
    _name = 'service.districts'
    name = fields.Char(required=True)

class ServiceDeliveryBy(models.Model):
    _name = 'service.delivery_by'
    name = fields.Char(required=True)

class ServiceCategories(models.Model):
    _name = 'service.categories'
    name = fields.Char(required=True)

