# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant','portal.mixin']
    _mail_post_access = 'read'
    
    applicant_user_id = fields.Many2one(
        'res.users',
        string='Applicant',
        copy=False,
    )
    number = fields.Char(
        string='Number',
        copy=False,
    )
    
    @api.model
    def create(self, vals):
        if not vals.get('applicant_user_id'):
            portal_group = self.env['res.groups'].sudo().search([('name', '=', 'Portal')])
            print("portal_group",portal_group)
            user = self.env['res.users'].sudo().search([('login', '=', vals.get('email_from'))])
            print("user",user)
            if user:
                pass
            else:
                vals_user = {
                    'name': vals.get('name'),
                    'login': vals.get('email_from'),
                    'email': vals.get('email_from'),
                    'groups_id': [(6, 0, portal_group.ids)],
                }
                print("vals_user",vals_user)
                user = self.env['res.users'].sudo().create(vals_user)
                print("user",user)
            vals['applicant_user_id'] = user.id
            print("vals['applicant_user_id']",vals['applicant_user_id'])
        vals['number'] = self.env['ir.sequence'].next_by_code('application.seq')
        print("vals['number']",vals['number'])
        return super(Applicant, self).create(vals)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
