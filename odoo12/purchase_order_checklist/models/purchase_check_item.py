#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

ACESSERRORMESSAGE = _(u"""Sorry, but you don't have rights to confirm/disapprove '{0}'!
Contact your system administator for assistance.""")


class purchase_check_item(models.Model):
    """
    The model to keep each item of a check list
    """
    _name = "purchase.check.item"
    _description = "Purchase Order Check Item"

    @api.model
    def state_selection(self):
        """
        The method to return possible states according to a purchase order
        """
        states = self.env["purchase.order"]._fields["state"]._description_selection(self.env)
        return states

    @api.multi
    @api.depends("color_sel")
    def _compute_color(self):
        """
        Compute method for color
        """
        for checklist in self:
            checklist.color = int(checklist.color_sel)

    name = fields.Char(
        string="What should be done on this stage",
        required=True,
    )
    state = fields.Selection(
        state_selection,
        string="State",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
    )
    group_ids = fields.Many2many(
        "res.groups",
        "res_groups_purchase_check_item_list_rel_table",
        "res_groups_id",
        "purchase_check_item_id",
        string="User groups",
        help="Leave it empty if any user may confirm this checklist item,"
    )
    should_be_reset = fields.Boolean(
        string="Should be recovered",
        default=False,
        help="""
            If checked each time a purchase order is reset back to this stage (e.g. after cancellation), this check list
            item would be recovered to the initial state
        """,
    )
    company_no_id = fields.Many2one(
        "res.company",
        string="Company TO no states",
    )
    check_company_list_id = fields.Many2one(
        "check.company.list",
        string="Check List for Company",
    )
    check_no_company_list_id = fields.Many2one(
        "check.company.list",
        string="No Stages for Company",
    )
    color_sel = fields.Selection(
        (
            ("1", "Red"),
            ("2", "Orange"),
            ("3", "Yellow"),
            ("4", "Light Blue"),
            ("5", "Dark Purple"),
            ("6", "Salmon Pink"),
            ("7", "Medium Blue"),
            ("8", "Dark Blue"),
            ("9", "Fushia"),
            ("10", "Creen"),
            ("11", "Purple"),
        ),
        string="Color",
    )
    color = fields.Integer(
        compute=_compute_color,
        store=True,
        string="Tech Color",
    )

    _order = "state, id"

    @api.multi
    def _check_cheklist_rights(self):
        """
        The method to check rights to fill check list item
        """
        if not self.env.user.has_group("purchase_order_checklist.group_purchase_order_checklist_superuser"):
            for item in self:
                if item.group_ids:
                    if not (self.env.user.groups_id & item.group_ids):
                        raise AccessError(ACESSERRORMESSAGE.format(item.name))


