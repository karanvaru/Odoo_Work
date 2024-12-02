#coding: utf-8

from odoo import fields, models

class crm_stage(models.Model):
    _inherit = "crm.stage"

    default_crm_check_list_ids = fields.One2many(
        "crm.check.list",
        "crm_stage_st_id",
        string="Check List",
    )
    no_need_for_checklist = fields.Boolean(
        string="No need for checklist",
        help="If selected, when you move a lead TO this stage, no checklist is required (e.g. for 'Cancelled')"
    )
