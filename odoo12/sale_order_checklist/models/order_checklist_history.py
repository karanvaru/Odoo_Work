#coding: utf-8

from odoo import api, fields, models

class order_checklist_history(models.Model):
    """
    A model to keep each change of check list per sale order
    """
    _name = "order.checklist.history"
    _description = "Check List History"

    check_list_id = fields.Many2one(
        "order.check.item",
        string="Check Item",
    )
    sale_order_id = fields.Many2one("sale.order")
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

