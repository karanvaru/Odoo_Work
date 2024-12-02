# -*- coding: utf-8 -*-

from odoo import models, fields

class Task(models.Model):
    _inherit = 'project.task'
   
    custom_is_field_service = fields.Boolean(
        string='Is Field Service?',
        copy=True,
    )

    def view_sale_estimate_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('odoo_sale_estimates.action_estimate')
        action['domain'] = [('custom_field_service','=', self.id)]
        action['context'] ={
            'default_custom_field_service': self.id,
            'default_partner_id': self.partner_id.id,
            'default_source': self.name,
        }
        return action