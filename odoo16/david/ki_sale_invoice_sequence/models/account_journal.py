# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    category_type = fields.Selection(
        selection=[
            ('rental', 'Rental'),
            ('service', 'Service'),
            ('parts', 'Parts'),
            ('sale', 'Sales')
        ],
        string='Category Type',
        # required=True
    )
