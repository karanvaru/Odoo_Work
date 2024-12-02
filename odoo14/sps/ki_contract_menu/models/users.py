from odoo import api, fields, models, _


class UserForm(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals_list):
        res = super(UserForm, self).create(vals_list)
        if res.partner_id.email == False:
            res.partner_id.email = res.login
        return res
