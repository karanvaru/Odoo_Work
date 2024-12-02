# -*- coding: utf-8 -*-

from odoo import api, fields, models


class res_users(models.Model):
    """
    Overwrite to add properties to restrict choice only to portal users
    """
    _inherit = "res.users"

    @api.multi
    @api.depends("groups_id")
    def _compute_is_int_user(self):
        """
        Compute method for is_int_user
        """
        for user in self:
            user.is_int_user = user.has_group('base.group_user')

    is_int_user = fields.Boolean(
        string="Internal user",
        compute=_compute_is_int_user,
        compute_sudo=True,
        store=True,
    )


