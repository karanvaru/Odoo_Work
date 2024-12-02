# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    sh_is_show_garage = fields.Boolean("Garage Feature?", default=True)
    sh_do_not_consider_vehicle_over_category = fields.Boolean(
        "Do not consider vehicle when click on category")
    sh_do_not_consider_vehicle_over_attribute = fields.Boolean(
        "Do not consider vehicle when click on attributes")
    sh_do_not_consider_vehicle_over_price = fields.Boolean(
        "Do not consider vehicle when change on min/max price")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sh_is_show_garage = fields.Boolean(
        related="website_id.sh_is_show_garage",
        string="Garage Feature?",
        readonly=False,
    )
    sh_do_not_consider_vehicle_over_category = fields.Boolean(
        related="website_id.sh_do_not_consider_vehicle_over_category",
        string="Do not consider vehicle when click on category",
        readonly=False,
    )
    sh_do_not_consider_vehicle_over_attribute = fields.Boolean(
        related="website_id.sh_do_not_consider_vehicle_over_attribute",
        string="Do not consider vehicle when click on attributes",
        readonly=False,
    )
    sh_do_not_consider_vehicle_over_price = fields.Boolean(
        related="website_id.sh_do_not_consider_vehicle_over_price",
        string="Do not consider vehicle when change on min/max price",
        readonly=False,
    )
