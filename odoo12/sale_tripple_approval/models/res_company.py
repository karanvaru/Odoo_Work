# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    so_three_step_validation =  fields.Boolean(
        'Three Step Approval'
    )
    so_double_validation = fields.Selection(
        [('one_step','Confirm Sale Order in One Step'),
         ('two_step','Get 2 Level Approvals to Confirm a Sale Order')],
        default='one_step',
        string='Level of SO Approvals'
    )
    so_finance_validation_amount = fields.Monetary(
        'Finance Validation Amount',
        default=0.0
    )
    so_double_validation_amount = fields.Monetary(
        'SO Double Validation Amount',
        default=0.0
    )
    so_director_validation_amount = fields.Monetary(
        'Director Validation Amount',
        default=0.0
    )
    so_email_template_id = fields.Many2one(
        'mail.template',
        string='Sale Approval Email Template',
    )
    so_refuse_template_id = fields.Many2one(
        'mail.template',
        string='Sale Refuse Email Template',
    )
