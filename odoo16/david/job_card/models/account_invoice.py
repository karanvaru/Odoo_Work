# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoice(models.Model):
#    _inherit = 'account.invoice'
    _inherit = 'account.move'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        readonly=True,
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
