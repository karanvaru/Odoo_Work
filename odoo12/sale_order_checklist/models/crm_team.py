#coding: utf-8

from odoo import api, fields, models

class crm_team(models.Model):
    """
    Override to add check lists
    """
    _inherit = "crm.team"

    check_line_ids = fields.One2many(
        "order.check.item",
        "team_id",
        string="Check Lists",
        copy=True,
    )
    no_stages_ids = fields.One2many(
        "order.check.item",
        "team_no_id",
        string="""Determine the states, the transfer to which does not require filling in the check lists at the current
        stage""",
        copy=True,
    )

