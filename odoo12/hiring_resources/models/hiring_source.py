# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class HiringSources(models.Model):
    _name = "hiring.sources"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hiring Sources'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='always')
    responsible = fields.Many2one('res.users', 'Responsible', store=True, domain="[('is_int_user','=',True)]",track_visibility='onchange')
    hiring_sources= fields.Many2one('res.partner',string='Hiring Source', store=True,track_visibility='onchange')
    hs_category= fields.Many2many('hs.category', string='HS Category', store=True,track_visibility='onchange')
    internal_notes = fields.Text('Notes', store=True, track_visibility='always')
    address = fields.Char('Address', Track_visibility='always')
    city = fields.Char('City', Track_visibility='always')
    logo = fields.Binary('Logo')
    password = fields.Char('Password', Track_visibility='always')
    state = fields.Char('State', Track_visibility='always')
    hs_status = fields.Selection([("active", "Active"),
                               ("in_active", "In Active")], string=" HS Status", required=True, track_visibility='always')
    category = fields.Selection([("Recruitment Agency", "Recruitment Agency"),
                                 ("Recruitment Intuitions", "Recruitment Intuitions"),
                                 ("Skill Development Center", "Skill Development Center")
                                 ], string="Category")

    total_applications = fields.Integer('Total Applications', compute="compute_total_applications")
    url = fields.Char('URL', Track_visibility='always')
    user_name = fields.Char('User Name', Track_visibility='always')
    website = fields.Char('Website', Track_visibility='always')
    department_id = fields.Many2one('hr.department','For Department',Track_visibility='onchange')


    @api.model
    def create(self,vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('hiring.sources.sequence'), })
        return super(HiringSources, self).create(vals)


    @api.multi
    def compute_total_applications(self):
        for record in self:
            rec_partner = record['hiring_sources'].name
            total_app_count = self.env['hr.applicant'].search_count([('vendor_source_id', 'in', rec_partner)])
            if self.env['hr.applicant'].search_count([('vendor_source_id.parent_id', 'in', rec_partner)]) != 0:
                record['total_applications'] = total_app_count + self.env['hr.applicant'].search_count(
                    [('vendor_source_id.parent_id', 'in', rec_partner)])
            else:
                record['total_applications'] = total_app_count


class HSCategory(models.Model):
    _name = 'hs.category'
    _description = 'Hiring Source Category'

    name = fields.Char('Hiring Source Category')

class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    vendor_source_id = fields.Many2one('res.partner', string='Vendor Source',track_visibility='onchange')

