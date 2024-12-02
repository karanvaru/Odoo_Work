# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file
# for full copyright and licensing details.

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def name_get(self):
        super(HrEmployee, self).name_get()
        result = []
        for rec in self:
            name = rec.display_name
            if rec.emp_no:
                name = rec.name + '(' + rec.emp_no + ')'
            result.append((rec.id, name))
        return result

    def _sync_user(self, user, employee_has_image=False):
        vals = super(HrEmployee, self)._sync_user(user, employee_has_image)
        if user.seq_number:
            vals.update({
                'emp_no': user.seq_number
            })
        return vals
