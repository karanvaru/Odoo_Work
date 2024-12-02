# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MotorcycleMotorcycle(models.Model):
    _name = "motorcycle.motorcycle"
    _description = "Motorcycle"
    _order = "id desc"

    name = fields.Char(string="Name", compute="_compute_complete_name")
    year_id = fields.Many2one(comodel_name="motorcycle.year",
                              string="Start year", required=True)
    end_year_id = fields.Many2one(comodel_name="motorcycle.year",
                                  string="End year", required=True)
    mmodel_id = fields.Many2one(comodel_name="motorcycle.mmodel",
                                string="Model", required=True)
    type_id = fields.Many2one(comodel_name="motorcycle.type",
                              string="Type",
                              related="mmodel_id.type_id",
                              store=True
                              )
    make_id = fields.Many2one(comodel_name="motorcycle.make",
                              string="Make",
                              related="mmodel_id.make_id",
                              store=True
                              )
    product_ids = fields.Many2many('product.product',
                                   'product_product_motorcycle_motorcycle_rel',
                                   'motorcycle_id', 'product_id',
                                   string='Products', copy=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )
    garde = fields.Many2many(comodel_name='motorcycle.garde', string='Grade')
    engine = fields.Many2many(
        comodel_name='motorcycle.engine', string='Engine')
    transmission_ids = fields.Many2many(
        comodel_name='motorcycle.transmission', string='Transmission')
    p_type_ids = fields.Many2many(
        comodel_name='motorcycle.product.type', string='Product Type')
    vehicle_image = fields.Image("Image")

    def _compute_complete_name(self):
        if self:
            for rec in self:
                name = ''
                if rec.make_id:
                    name += rec.make_id.name + ' '
                if rec.mmodel_id:
                    name += rec.mmodel_id.name + ' '
                if rec.year_id:
                    name += str(rec.year_id.name)
                if rec.end_year_id:
                    name = name + ' - ' + str(rec.end_year_id.name)
                if name == '':
                    name = False
                rec.name = name

    @api.constrains('year_id', 'end_year_id')
    def _constraint_check_year(self):
        if self.filtered(lambda c: c.end_year_id.name and c.year_id.name > c.end_year_id.name):
            raise ValidationError(_('Start year must be less than end year.'))
