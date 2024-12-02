# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo.http import request
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ASPExtended(models.Model):

    _inherit = 'asp.partner'

    rating = fields.Selection([
        ('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('excellent', 'Excellent'),
        ('extraordinary', 'Extraordinary'),
        ('awesome', 'Awesome')
    ], string="ASP Rating") 
    service_type_ids = fields.Many2many('service.types', string='Serviceable Types', track_visibility='onchange')
    vendor_id = fields.Many2one('res.partner',"ASP Partner",track_visibily="onchange")
    state = fields.Many2one('res.country.state','State',track_visibility='always')
    country = fields.Many2one('res.country',string='Country',track_visibility='onchange')
    avg_turn_over = fields.Char(string="Last 2 years avg turnover",track_visibily="always")
    ##Basic company Information
    year_established = fields.Char('Year established',track_visibility='always')
    city = fields.Char('City',track_visibility='always')
    zip = fields.Char('Pincode',track_visibility='always')
    location_ids = fields.Many2many('asp.locations',string='Branch locations') 
    company_mail = fields.Char('Company mail')
    company_mobile = fields.Char('Company contact number',track_visibility='always') 
    gst_number = fields.Char('GST number',track_visibility='always')
    tag_ids = fields.Many2many('asp.tags', string='Tags', track_visibility='onchange')
    source_ids = fields.Many2many('asp.source',string='Source', track_visibility='onchange')
    company_name = fields.Char('Company Name',track_visibility='always')

    # Business Information

    is_gst_registered = fields.Boolean('Is GST Registered')
    using_crm_ids = fields.Many2many('asp.crms',string="Name of crm's using")
    total_people = fields.Char('Total no.of people in company',track_visibility='always')
    # rma_centers = fields.Many2many('rma.centers',string="RMA Centers")
    ###########Contact Information##################
    promoter_name = fields.Char('Proprietary name',track_visibility='always')
    promoter_email = fields.Char('proprietary email',track_visibility='always')
    promoter_mobile = fields.Char('proprietary mobile',track_visibility='always')
    service_delivery_head_name = fields.Char('Support head name',track_visibility='always')
    service_delivery_head_email = fields.Char('Support head email',track_visibility='always')
    service_delivery_head_mobile = fields.Char('Support head mobile',track_visibility='always')
    senior_technical_person_name = fields.Char('Sr.tech person name',track_visibility='always')
    senior_technical_person_email = fields.Char('Sr.tech person email',track_visibility='always')
    senior_technical_person_mobile = fields.Char('Sr.tech person mobile',track_visibility='always')



    ########Extran fields Added##################

    list_of_certificates = fields.Char('List of Certificates',track_visibility='always')
    list_of_awards = fields.Char('List awards',track_visibility='always')
    service_delivery_years = fields.Char('Number of years in service delivery',track_visibility='always')
    service_delivery_achivements= fields.Char('Service delivery achivements',track_visibility='always')
    company_profile = fields.Binary('Company Profile',track_visibility='always')
    customer_testmonial = fields.Binary('Customer Testimonial',track_visibility='always')
    sla_document = fields.Binary('SLA Documents',track_visibility='always')
    escalation_document = fields.Binary('Escalation Documents',track_visibility='always')
    customer_feedback = fields.Char('Customer Feedback',track_visibility='always')
    shelf_place = fields.Char('Can you provide shelf space?',track_visibility='always')
    ready_to_use_rdp_crm = fields.Char('Ready to use RDP crm',track_visibility='always')
    ready_to_for_weekly_sla_reviews = fields.Char('Ready for weekly SLA reviews',track_visibility='always')
    onsite_support_executives = fields.Char('Total no.of onsite support executives',track_visibility='always')
    insite_support_executives = fields.Char('Total no.of inside support executives',track_visibility='always')
    number_of_calls_expecting_from_rdp_per_month = fields.Char('Number of calls expecting from RDP per month',track_visibility='always')
    number_of_calls_you_are_attending_per_day = fields.Char('Number of calls you are attending everyday',track_visibility='always')
    onsite_calls_every_day = fields.Char('Max no.of onsite calls every',track_visibility='always')
    training_certificates = fields.Char('List of traing certificates',track_visibility='always')
    training_on_softskills = fields.Char('How often you train your executives on softskills',track_visibility='always')
    training_on_hardskills = fields.Char('How often you train your executives on hardskills',track_visibility='always')



    # @api.onchange('country')
    # def _onchange_country_id_wrapper(self):
    #     res = {'domain': {'state': []}}
    #     if self.country_id:
    #          res['domain']['state'] = [('country', '=', self.country.id)]
    #     return res 







class ASPServiceTypes(models.Model):

    _name = 'service.types'
    _description = "ASP Service Types"

    name = fields.Char('Name')
    
class ASPServiceLocations(models.Model):

    _name = 'asp.locations'
    _description = "ASP  Locations"

    name = fields.Char('Name')
class ASPCrms(models.Model):

    _name = 'asp.crms'
    _description = "ASP  CRMS"

    name = fields.Char('Name') 

class ASPTags(models.Model):

    _name = 'asp.tags'
    _description = "ASP Tags"

    name = fields.Char('Name')   

class ASPSourceIds(models.Model):

    _name = 'asp.source'
    _description = "ASP Source"

    name = fields.Char('Name')








