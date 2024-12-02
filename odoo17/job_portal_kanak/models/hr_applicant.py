# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
import random
import json

from odoo import api, fields, models


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(20))


class Applicant(models.Model):
    _inherit = "hr.applicant"

    applicant_number = fields.Char('Application')
    last_name = fields.Char("Last Name")
    personal_detail_ids = fields.One2many('personal.detail', 'personal_detail_id')
    certificate_detail_ids = fields.One2many('certificate.detail', 'certificate_detail_id')
    professional_detail_ids = fields.One2many('professional.detail', 'professional_detail_id')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], default="male", tracking=True)
    birthday = fields.Date('Date of Birth', tracking=True)
    place_of_birth = fields.Many2one(
        'res.country.state', 'Place of Birth', domain="[('country_id', '=', country_id)]")
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", tracking=True)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single', tracking=True)
    address1 = fields.Char(string="Flat/House No.")
    address2 = fields.Char(string="Stree/Society.")

    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    city = fields.Char("city")
    zipcode = fields.Char("Zip")
    personal_detail_ids = fields.One2many('personal.detail', 'personal_detail_id', string="Academic Details")
    certificate_detail_ids = fields.One2many('certificate.detail', 'certificate_detail_id', string="Certificate details")
    professional_detail_ids = fields.One2many('professional.detail', 'professional_detail_id', string="Professional details")
    partner_id = fields.Many2one('res.partner', string="Customer")
    access_token = fields.Char(copy=False, groups="base.group_erp_manager")

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['applicant_number'] = self.env['ir.sequence'].next_by_code('hr.applicant', sequence_date=None)
        result = super(Applicant, self).create(vals)
        if result:
            result.access_token = random_token()
        return result


    def _get_employee_create_vals(self):
        vals = super(Applicant, self)._get_employee_create_vals()
        address_id = self.partner_id.address_get(['contact'])['contact']
        address_sudo = self.env['res.partner'].sudo().browse(address_id)
        
        partner = self.partner_id
        
        default_academic_ids = []
        
        partner.write({
            'name': self.partner_name,
            'street': self.address1,
            'street2': self.address2,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'city': self.city,
            'zip': self.zipcode,
            'mobile': self.partner_mobile,
            'phone': self.partner_phone
        })
        for rem in self.personal_detail_ids:
            default_academic_ids.append([0, 0, {
                'course_name': rem.course_name,
                'branch': rem.branch,
                'organization': rem.organization,
                'start_date': rem.start_date,
                'end_date': rem.end_date,
                'marks': rem.marks
            }])
        default_certificate_ids = []
        for red in self.certificate_detail_ids:
            default_certificate_ids.append([0, 0, {
                'course_name': red.course_name,
                'branch': red.branch,
                'organization': red.organization,
                'certificate_des': red.certificate_des,
                'attachment_ids': red.attachment_ids.ids,
                'start_date': red.start_date,
                'end_date': red.end_date
            }])
            
        default_profession_ids = []
        for dem in self.professional_detail_ids:
            default_profession_ids.append([0, 0, {
                'name': dem.name,
                'organization': dem.organization,
                'department': dem.department,
                'start_date': dem.start_date,
                'end_date': dem.end_date,
                'work_exp': dem.work_exp,
                'work_des': dem.work_des,
                'projects': dem.projects
            }])

        vals.update({
            'academic_ids': default_academic_ids,
            'certificate_ids': default_certificate_ids,
            'profession_ids': default_profession_ids,
        })
        return vals

#     def create_employee_from_applicantXXX(self):
#         value = []
#         lst = []
#         val = []
#         context = res['context']
#         context = json.loads(context)
#         context.update({
#             'default_description': self.description
#         })
# #         context['default_description'] = self.description
#         context['default_gender'] = self.gender
#         context['default_marital'] = self.marital
#         context['default_birthday'] = self.birthday
#         context['default_country_of_birth'] = self.country_of_birth.id
#         vals = self.env['res.partner'].search([('name', '=', self.partner_name)])
#         vals.write({
#             'name': self.partner_name,
#             'street': self.address1,
#             'street2': self.address2,
#             'country_id': self.country_id.id,
#             'state_id': self.state_id.id,
#             'city': self.city,
#             'zip': self.zipcode,
#             'mobile': self.partner_mobile,
#             'phone': self.partner_phone
#         })
# 
#         for rem in self.personal_detail_ids:
#             value.append([0, 0, {
#                 'course_name': rem.course_name,
#                 'branch': rem.branch,
#                 'organization': rem.organization,
#                 'start_date': rem.start_date,
#                 'end_date': rem.end_date,
#                 'marks': rem.marks
#             }])
#         context['default_academic_ids'] = value
# 
#         for red in self.certificate_detail_ids:
#             lst.append([0, 0, {
#                 'course_name': red.course_name,
#                 'branch': red.branch,
#                 'organization': red.organization,
#                 'certificate_des': red.certificate_des,
#                 'attachment_ids': red.attachment_ids.ids,
#                 'start_date': red.start_date,
#                 'end_date': red.end_date
#             }])
#         context['default_certificate_ids'] = lst
# 
#         for dem in self.professional_detail_ids:
#             val.append([0, 0, {
#                 'name': dem.name,
#                 'organization': dem.organization,
#                 'department': dem.department,
#                 'start_date': dem.start_date,
#                 'end_date': dem.end_date,
#                 'work_exp': dem.work_exp,
#                 'work_des': dem.work_des,
#                 'projects': dem.projects
#             }])
#         context['default_profession_ids'] = val
#         res = super(Applicant, self.with_context(context)).create_employee_from_applicant()
#         return res
