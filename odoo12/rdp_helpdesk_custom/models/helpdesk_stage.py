# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _



class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    rdp_mail_notify_type = fields.Selection([
        ('PSR_opened_stage', 'PSR opened stage'),
        ('back_order_stage', 'Back order stage'),
        ('customer_side_pending_stage', 'Customer side pending stage'),
    ],
        string="Mail Notify Type",
    )