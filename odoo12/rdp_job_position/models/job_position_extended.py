from odoo import models,fields, api, _

class JobPositionExtended(models.Model):
    _inherit = 'hr.job'

    managers_responsibility = fields.Html(string='Managers Responsibility')