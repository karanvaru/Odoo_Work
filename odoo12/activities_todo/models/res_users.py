# -*- coding: utf-8 -*-

from odoo import models, fields


class res_users(models.Model):
    """
    Re write to add activities to-do settings
    """
    _inherit = "res.users"

    act_type_ids = fields.Many2many(
        "mail.activity.type",
        "mail_activity_type_res_users_rel_table",
        "mail_activity_type_id",
        "res_users_id",
        string='To-Do Activity Types',
        help="If not selected all activity types would be included in to-do lists",
    )
    only_old_activities = fields.Boolean(
        "No future activites in to-do",
        help="If checked activities to-do would not include activites with deadline in the Future",
        default=True,
    )

    def __init__(self, pool, cr):
        """
        Overwrite to redefine SELF_WRITEABLE_FIELDS in order to let user change their preferences
        """
        init_res = super(res_users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['act_type_ids', 'only_old_activities'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['act_type_ids', 'only_old_activities'])
        return init_res
