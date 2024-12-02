# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ctx = self._context
        args = args or []
        if ctx.get('has_deputy_groups'):
            # [[6, False, [id1, id2]]]
            group_ids = ctx['has_deputy_groups'][0][2]
            if group_ids:
                group_ids += [-1]
                sql = """
                    SELECT uid FROM res_groups_users_rel WHERE gid IN %s
                """
                self._cr.execute(sql, (tuple(group_ids),))
                user_ids = [x[0] for x in self._cr.fetchall()]
                args += [('id', 'in', user_ids)]
        return super(ResUsers, self).name_search(name, args, operator, limit)