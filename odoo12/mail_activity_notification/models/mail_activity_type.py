# -*- coding: utf-8 -*-

from odoo import fields, models


class mail_activity_type(models.Model):
    _inherit = "mail.activity.type"

    is_notify = fields.Boolean(
        string=u'Send notification',
        help=u'Send notification for this type of activity',
        default=False,
    )
