from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContactUserCreate(models.TransientModel):
    _name = 'contact.user.create.wizard'
    _description = 'User Create'

    name = fields.Char(
        string='Name',
        required=True,
    )
    title_id = fields.Many2one(
        'res.partner.title',
        string='Title',
    )
    function = fields.Char(
        string='Job Position',
    )
    email = fields.Char(
        string='Email',
    )
    phone = fields.Char(
        string='Phone Number',
    )
    new_password = fields.Char(
        string='Password',
        required=True,
    )

    def action_create(self):
        # user_login = False
        if self.email:
            user_login = self.email
        elif self.phone:
            user_login = self.phone
        else:
            raise ValidationError(_("Please Enter Phone Number or Email"))

        group_id = self.env.ref('ki_contract_menu.group_smart_printer_customer_user').id
        # id = self.env.ref('base.group_user').id
        if user_login == self.phone:
            vals = {
                'name': self.name,
                'login': user_login,
                'work_phone': user_login,
                'groups_id': [(6, 0, [group_id])]
            }
        else:
            vals = {
                'name': self.name,
                'login': user_login,
                'groups_id': [(6, 0, [group_id])]
            }
        user_id = self.env['res.users'].create(vals)
        if user_id:
            user_id.partner_id.type = 'contact'
            user_id.partner_id.parent_id = self._context.get('active_id')
        lines = [(0, 0, {
            'user_id': user_id.id,
            'user_login': user_id.login,
            'new_passwd': self.new_password
        })]
        record_user = self.env['change.password.wizard'].create({'user_ids': lines})
        record_user.change_password_button()
