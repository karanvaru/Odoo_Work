from odoo import models,api,fields

class Res_users(models.Model):
    _inherit = 'res.users'

    mobi_device_ids = fields.One2many(
        'res.mobile.user',
        'user_id',
        string = "Mobile Devices"
    )

class Mobile_Device(models.Model):
    _name = 'res.mobile.user'
    _description = "Mobile Devices"

    user_id = fields.Many2one(
        'res.users',
        string = "User Id"
    )
    device_id = fields.Char(
        string = "Device Id"
    )
    device_type = fields.Char(
        string = "Device Type"
    )
    session_id = fields.Char(
        string = "Session"
    )