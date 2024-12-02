from odoo import models, fields, api, _


class MailTemplateInherit(models.Model):
    _inherit = 'mail.template'

    reddot_specific = fields.Boolean(
        string="Is Reddot Specific?"
    )