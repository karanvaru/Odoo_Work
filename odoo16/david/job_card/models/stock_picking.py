# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    jobcard_id = fields.Many2one(
        'project.task',
        string='Job Card',
        #readonly=True,
    )
    custom_project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    custom_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )

    #@api.multi
    @api.onchange('jobcard_id')
    def onchange_jobcard(self):
        for rec in self:
            rec.custom_project_id = rec.jobcard_id.project_id.id
            rec.custom_analytic_account_id = rec.jobcard_id.analytic_account_id.id
