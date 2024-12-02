# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    motorcycle_ids = fields.Many2many(
        'motorcycle.motorcycle',
        'product_product_motorcycle_motorcycle_rels',
        'product_ids',
        'motorcycle_ids',
        string='Vehicle',
        copy=True
    )
    sh_is_common_product = fields.Boolean(
        string="Common Products?"
    )
    garde = fields.Many2many(
        comodel_name='motorcycle.garde',
        string='Grade'
    )
    engine = fields.Many2many(
        comodel_name='motorcycle.engine',
        string='Engine'
    )
    product_type = fields.Many2many(
        comodel_name='motorcycle.product.type',
        string='Vehicle Product Type'
    )
    brand = fields.Many2one(
        comodel_name='motorcycle.brand',
        string='Brand'
    )
    made_in = fields.Many2one(
        comodel_name='res.country',
        string='Made In'
    )
    transmission_ids = fields.Many2many(
        comodel_name='motorcycle.transmission',
        string='Transmission'
    )

    @api.onchange('sh_is_common_product')
    def onchange_sh_is_common_product(self):
        if self:
            for record in self:
                if record.sh_is_common_product:
                    record.motorcycle_ids = False


class ProductProduct(models.Model):
    _inherit = "product.product"

    engine_number = fields.Char(
        string="Engine Number"
    )
    serial_number = fields.Char(
        string="Serial Number"
    )
    motorcycle_ids = fields.Many2many(
        'motorcycle.motorcycle',
        'product_product_motorcycle_motorcycle_rel',
        'product_id', 'motorcycle_id',
        string='Vehicle',
        copy=True,
        related="product_tmpl_id.motorcycle_ids",
        readonly=False
    )
    sh_is_common_product = fields.Boolean(
        string="Common Products?",
        related="product_tmpl_id.sh_is_common_product",
        readonly=False
    )
    garde = fields.Many2many(
        comodel_name='motorcycle.garde',
        string='Grade',
        related="product_tmpl_id.garde",
        readonly=False
    )
    engine = fields.Many2many(
        comodel_name='motorcycle.engine',
        string='Engine',
        related="product_tmpl_id.engine",
        readonly=False
    )
    product_type = fields.Many2many(
        comodel_name='motorcycle.product.type',
        string='Vehicle Product Type',
        related="product_tmpl_id.product_type",
        readonly=False
    )
    brand = fields.Many2one(
        comodel_name='motorcycle.brand',
        string='Brand',
        related="product_tmpl_id.brand",
        readonly=False
    )
    made_in = fields.Many2one(
        comodel_name='res.country',
        string='Made In',
        related="product_tmpl_id.made_in",
        readonly=False
    )
    transmission_ids = fields.Many2many(
        comodel_name='motorcycle.transmission',
        string='Transmission',
        related="product_tmpl_id.transmission_ids",
        readonly=False
    )
    vin_number = fields.Char(
        string="VIN Number",
        readonly=False
    )
    vehicle_oem_lines = fields.One2many(
        'sh.vehicle.oem',
        'product_product_id',
        string='Vehicle OEM Lines',
        copy=True,
        related="product_tmpl_id.vehicle_oem_lines",
        readonly=False
    )
    specification_lines = fields.One2many(
        'sh.product.specification',
        'product_product_id',
        string='Specification Lines',
        copy=True,
        related="product_tmpl_id.specification_lines",
        readonly=False
    )

    @api.constrains('engine_number', 'serial_number', 'vin_number')
    def unique_vin_engine_serial_number(self):
        for rec in self:
            if rec.engine_number:
                products_engine_number = self.search_count([(
                    'engine_number', '=', rec.engine_number)
                ])
                if products_engine_number > 1:
                    raise ValidationError(_("Engine Number Should Be Unique"))
            if rec.serial_number:
                products_serial_number = self.search_count([
                    ('serial_number', '=', rec.serial_number)
                ])
                if products_serial_number > 1:
                    raise ValidationError(_("Serial Number Should Be Unique"))
            if rec.vin_number:
                products_vin_number = self.search_count([
                    ('vin_number', '=', rec.vin_number)
                ])
                if products_vin_number > 1:
                    raise ValidationError(_("VIN Number Should Be Unique"))
