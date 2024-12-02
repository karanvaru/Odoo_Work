import string
from odoo import api, fields, models, _
from datetime import date, datetime
import time



class FMAdminInherited(models.Model):
    _inherit ="rdp.exit14"


    property1_id = fields.Many2one('property.one',string='Property One')
    property_one_ticket_count = fields.Integer(string="P1",compute="compute_property_count")
    location_id = fields.Many2one('fm.location',string="Location",track_visibility='onchange')
    state = fields.Selection([
        ('sourcing', 'Sourcing'),
        ('finalized_vendors', 'Finalized vendors'),
       
    ], string='Status',default="sourcing",track_visibility='always',store=True)
    @api.multi
    def compute_property_count(self):
        for rec in self:
            count_values = self.env['property.one'].search_count([('fm_admin_id','=',rec.id)])
            rec.property_one_ticket_count = count_values


    def open_property_one(self):
        self.ensure_one()
        return {
                'name': 'FM & Admin Vendors',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'property.one',
                'domain': [('fm_admin_id','=',self.id)],
            }

       
        # vals = {
        #     'fm_admin_id':self.id
        # }
        # return {
        #     'name': 'FM & Admin Vendor',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree,form',
        #     'res_model': 'property.one',
        #     # 'vals' : vals,
        #     'context': {
        #         'default_service_product_id':self.vendor_product_category.id,
        #         'default_vendor_id':self.vendor.id,
        #         'default_fm_admin_id':self.id,
        #         'default_category':self.category_id.id,
        #         'default_sub_category':self.sub_category_id.id,
        #         'default_fm_department_id':self.department_id.id,
        #         'default_fm_product_type_id':self.product_type_id.id,
        #         'default_fm_vendor_quality': self.x_studio_priority,
        #         },
        #     'domain': [('fm_admin_id','=',self.id)],
            
            
        # }
    def action_to_fm_admin_vendors(self):
        fm_vendor_id = self.env['property.one']
        vals = {
            'fm_admin_id': self.id,
            'service_product_id':self.vendor_product_category.id,
            'vendor_id':self.vendor.id,
            'category':self.category_id.id,
            'sub_category':self.sub_category_id.id,
            'fm_department_id':self.department_id.id,
            'fm_product_type_id':self.product_type_id.id,
            'fm_vendor_quality':self.x_studio_priority,
            'location_id':self.location_id.id,
            'notes':self.notes,
            'quick_reference':self.x_studio_quick_reference_prices,
            'start_date':self.x_studio_start_date,
            'end_date':self.x_studio_end_date,

        }
        new_val = fm_vendor_id.create(vals)
        for rec in self:
            attachment = rec.env['ir.attachment'].search([('res_model','=','rdp.exit14'), ('res_id','=', rec.id)])
            for record in attachment:  
                rec.env['ir.attachment'].create({
                'name': record.name ,
                'res_name': record.name,
                'type': 'binary',
                'datas': record.datas,
                'res_model': 'property.one',
                'res_id':new_val.id,

                })
        self.state="finalized_vendors" 
        return new_val

class FMLocation(models.Model):
    _name = "fm.location"

    _description = "Property State"

    name = fields.Char(string="Name")   