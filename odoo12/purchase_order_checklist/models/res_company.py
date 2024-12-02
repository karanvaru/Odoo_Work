#coding: utf-8

from odoo import fields, models

class res_company(models.Model):
    """
    Override to add check lists
    """
    _inherit = "res.company"

    check_line_ids = fields.One2many(
        "purchase.check.item",
        "company_id",
        string="Check Lists",
        copy=True,
    )
    no_stages_ids = fields.One2many(
        "purchase.check.item",
        "company_no_id",
        string="""Determine the states, the transfer to which does not require filling in the check lists at the current
        stage""",
        copy=True,
    )
