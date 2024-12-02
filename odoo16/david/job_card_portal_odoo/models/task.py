# -*- coding: utf-8 -*-

from odoo import fields,models

class Task(models.Model):
    _inherit = "project.task"

    custom_signature_job_card = fields.Image(
        string="Signature",
        copy=False
    )
    custom_job_sign_by = fields.Many2one(
        'res.users',
        string="Signed by",
        copy=False
    )
    custom_job_sign_date = fields.Datetime(
        string='Signed Date',
        copy=False
    )