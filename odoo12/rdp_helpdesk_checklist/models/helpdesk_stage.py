#coding: utf-8

from odoo import fields, models

class helpdesk_stage(models.Model):
    _inherit = "helpdesk.stage"

    default_helpdesk_check_list_ids = fields.One2many(
        "helpdesk.check.list",
        "helpdesk_stage_st_id",
        string="Check List",
    )
    no_need_for_checklist = fields.Boolean(
        string="No need for checklist",
        help="If selected, when you move a record TO this stage, no checklist is required (e.g. for 'Cancelled')"
    )
