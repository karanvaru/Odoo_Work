from odoo import api, fields, models, _
import random


class UserOtp(models.Model):
    _inherit = "res.users"

    otp_number = fields.Integer(
        string='OTP'
    )

    otp_validate = fields.Boolean(
        string='OTP Validate'
    )
    work_phone = fields.Char(
        store=True,
    )
    parent_id = fields.Many2one(
        'res.partner',
        string='Customer',
        store=True,
    )
    partner_parent_id = fields.Many2one(
        'res.partner', 'Customer',
        related='partner_id.parent_id'
    )

    def action_create_employee(self):
        self.ensure_one()
        self.env['hr.employee'].create(dict(
            name=self.name,
            work_phone=self.work_phone,
            **self.env['hr.employee']._sync_user(self)
        ))
