# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailActivity(models.Model):
   
    _inherit = 'mail.activity'
    
    supervisor_user_id = fields.Many2one(
        'res.users',
        string='Supervisor',
        copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
