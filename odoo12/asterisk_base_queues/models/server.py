from odoo import models, fields


class AsteriskServer(models.Model):
    _inherit = 'asterisk_base.server'

    queue_settings = fields.Many2one(
        'asterisk_base_queues.settings_template',
        delegate=True,
        required=True,
        ondelete='cascade')
