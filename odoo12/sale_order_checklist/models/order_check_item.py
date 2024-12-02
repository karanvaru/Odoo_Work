#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

ACESSERRORMESSAGE = _(u"""Sorry, but you don't have rights to confirm/disapprove '{0}'!
Contact your system administator for assistance.""")


class order_check_item(models.Model):
    """
    The model to keep each item of a check list
    """
    _name = "order.check.item"
    _description = "Sale Order Check Item"

    @api.model
    def state_selection(self):
        """
        The method to return possible states according to a sale order
        """
        states = self.env["sale.order"]._fields["state"]._description_selection(self.env)
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
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
    )
    group_ids = fields.Many2many(
        "res.groups",
        "res_groups_order_check_list_rel_table",
        "res_groups_id",
        "order_check_list_id",
        string="User groups",
        help="Leave it empty if any user may confirm this checklist item,"
    )
    should_be_reset = fields.Boolean(
        string="Should be recovered",
        default=False,
        help="""
            If checked each time a sale order is reset back to this stage (e.g. after cancellation), this check list
            item would be recovered to the initial state
        """,
    )
    team_no_id = fields.Many2one(
        "crm.team",
        string="Sales Team to no states",
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
        if not self.env.user.has_group("sale_order_checklist.group_sale_order_checklist_superuser"):
            for item in self:
                if item.group_ids:
                    if not (self.env.user.groups_id & item.group_ids):
                        raise AccessError(ACESSERRORMESSAGE.format(item.name))


