# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ResBranch(models.Model):
    _name = 'res.branch'
    _description = "Res Branch"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name", required=True, copy=False,)

    street = fields.Char('Street', readonly=False, store=True)
    street2 = fields.Char('Street2', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, readonly=False, store=True)
    city = fields.Char('City', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)

    address = fields.Char(
        "Address")
    phone = fields.Char(
        "Phone No.")

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)

    user_id = fields.Many2one(
        'res.users', string='User', index=True, default=lambda self: self.env.user)

    email = fields.Char('Email', help="Email of Invited Person")
    mobile = fields.Char('Mobile', help="Phone number of Invited Person")
    user_ids = fields.Many2many("res.users", string="Users")
