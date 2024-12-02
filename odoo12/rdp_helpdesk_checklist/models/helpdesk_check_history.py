#coding: utf-8

from odoo import api, fields, models

class helpdesk_check_history(models.Model):
    _name = "helpdesk.check.history"
    _description = "Check List History"

    check_list_id = fields.Many2one("helpdesk.check.list", string="Check Item")
    ticket_id = fields.Many2one("helpdesk.ticket")
    complete_date = fields.Datetime(
        string="Date",
        default=lambda self: fields.Datetime.now(),
    )
    user_id = fields.Many2one(
        "res.users",
        "User",
        default=lambda self: self.env.user.id,
    )
    done_action = fields.Selection(
        (
            ("done", "Complete"),
            ("reset", "Reset"),
        ),
        string="Action",
        default="done",
    )

    _order = "complete_date DESC,id"

