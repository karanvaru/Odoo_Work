from odoo import api, fields, models, _
from datetime import date, datetime



class PropertyOne(models.Model):
    _name = "property.one"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Property1 1000"


    name = fields.Char(string='Reference No', required=True, copy=False,track_visibility='always', readonly=True, index=True, default=lambda self : _('New'))
    # product_name = fields.Many2one('rdp.exit14', string="Product Name",related="service_id.vendor_product_category")
    model = fields.Many2one('property.model', string="Model", track_visibility='always')
    brand = fields.Many2one('property.brand', string="Brand", track_visibility='always')
    vendor_id = fields.Many2one('res.partner', string="Vendor", track_visibility='onchange',store=True)
    category = fields.Many2one('fm.category', string="Category", track_visibility='always')
    sub_category = fields.Many2one('fm.subcategory', string="Sub Category", track_visibility='always')
    data_sheet_attached = fields.Boolean(string="Data Sheet Attached", track_visibility='always')
    recurring_activity = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
        ('two_years', '2 Years'),
    ], string='Recurring Activity', track_visibility='always')
    next_maintainance_date = fields.Datetime("Next Maintainance Date", track_visibility='always')
    notes = fields.Html('Notes', track_visibility='always')
    property_one_purchase_order_count = fields.Integer("Purchase Order Count", compute="purchase_order_count")
    image = fields.Binary(string="Upload Image")
    product_id = fields.Many2one('product.product','Product Model',track_visibility="onchange")
    # product_model = fields.Char('Product Model',related="product_id.name")
    pdc_brand_id = fields.Many2one('product.brand.amz.ept',"Product Brand",related="product_id.product_brand_id",store=True)
    brand_country_id = fields.Many2one('res.country',string = "Brand Country",track_visibility="onchange")

    #############changed ############

    fm_admin_id = fields.Many2one('rdp.exit14',string='FM & Admin Sourcing',track_visibility="onchange")
    service_id = fields.Many2one('rdp.exit14',string="Service")
    service_product_id = fields.Many2one('vendorproduct.category','Product/Service Name',track_visibility="onchange",store=True)
    fm_product_type_id = fields.Many2one('fm.product.type',string="Product Type",track_visibility="onchange",store=True)
    fm_department_id = fields.Many2one('hr.department',string="Department",track_visibility="onchange",store=True)
    fm_vendor_quality = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
        ('Excellent', 'Excellent'),
        ('Excellent Plus', 'Excellent Plus'),
        ],string='Vendor Quality', track_visibility='always')
    assigned_to_id  = fields.Many2one('res.partner',string="Assigned To",track_visibility="onchange")
    tag_ids = fields.Many2many('property.tags', string='Tags', track_visibility='onchange')
    location_id = fields.Many2one('fm.location',string="Location",track_visibility='onchange')
    amc_state_id = fields.Many2one('property.amc.state',string="AMC Status",track_visibility='onchange')
    quick_reference = fields.Text('Quick Reference Prices',track_visibility='always')
    start_date = fields.Date('Start Date',track_visibility='always')
    end_date = fields.Date('End Date',track_visibility='always')
    
    # @api.multi
    # def compute_service_product(self):
    #     for rec in self:
    #         property_id = self.env['rdp.exit14'].search([('property1_id','=',rec.id)])
    #         for p_id in property_id:
    #             rec.service_product_id = p_id.id
    # @api.multi
    # def compute_vendor_name(self):
    #     for rec in self:
    #         v_id = self.env['rdp.exit14'].search([('property1_id','=',rec.id)])
    #         for vid in v_id:
    #             rec.vendor_id = vid.vendor






    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('property.sequence')
        res = super(PropertyOne, self).create(vals)
        active_id = self._context.get('active_id')
        # if active_id:
        #  h_id = self.env['rdp.exit14'].browse(active_id)
        #  for rec in h_id:
        #     vendor = rec.vendor
        #     vendor_product_cat = rec.vendor_product_category
        #     print('product cate',vendor_product_cat)
        #     print('product vendor',vendor)

        h_id = self.env['rdp.exit14'].browse(active_id)
        for rec in h_id:
            vendor = rec.vendor
            vendor_product_cat = rec.vendor_product_category
            print('product cate',vendor_product_cat)
            print('product vendor',vendor)


        return res


    @api.multi
    def purchase_order_count(self):
        count_values = self.env['purchase.order'].search_count([('property_one_thousand_id', '=', self.id)])
        self.property_one_purchase_order_count = count_values

    @api.multi
    def action_button(self):
        return {
            'name': 'Purchase Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('property_one_thousand_id', '=', self.id)],

        }



class ProductName(models.Model):
    _name = "product.name"

    _description = "Product Name"

    name = fields.Char('Name')

class Model(models.Model):
    _name = "property.model"

    _description = "Model"

    name = fields.Char('Name')



class Brand(models.Model):
    _name = "property.brand"

    _description = "Brand"

    name = fields.Char(string="Name")


class PropertyCategory(models.Model):
    _name = "property.category"

    _description = "Property One Category"

    name = fields.Char(string="Name")


class PropertyOneSubCategory(models.Model):
    _name = "property.sub.category"

    _description = "Property Sub Category"

    name = fields.Char(string="Name")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    property_one_thousand_id = fields.Many2one('property.one', 'Property1 1000')

class PropertyOneTags(models.Model):
    _name = "property.tags"

    _description = "Property Tags"

    name = fields.Char(string="Name")    

class PropertyLocations(models.Model):
    _name = "property.location"

    _description = "Property Locations"

    name = fields.Char(string="Name")    

class PropertyAMCState(models.Model):
    _name = "property.amc.state"

    _description = "Property State"

    name = fields.Char(string="Name") 