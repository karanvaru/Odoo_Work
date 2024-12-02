#coding: utf-8

from odoo import fields, models

class purchase_checklist_history(models.Model):
    """
    A model to keep each change of check list per purchase order
    """
    _name = "purchase.checklist.history"
    _description = "Check List History"

    check_list_id = fields.Many2one(
        "purchase.check.item",
        string="Check Item",
    )
    purchase_order_id = fields.Many2one("purchase.order")
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

