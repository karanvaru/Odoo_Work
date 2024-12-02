# -*- coding: utf-8 -*-

from odoo import fields, models, api

class Task(models.Model):
    _inherit = "project.task"

    register_no = fields.Char(
        string="Registration Number"
    )
    type_id = fields.Many2one(
        'vehicle.type.custom',
        string="Vehicle Type"
    )
    brand = fields.Char(
        string="Vehicle Brand"
    )
    model_name = fields.Char(
        string="Model Name"
    )
    year = fields.Char(
        string="Vehicle Manufacturing year"
    )
    vin = fields.Char(
        string="Vehicle Identification Number"
    )
    fuel_type = fields.Selection([
        ('petrol','Petrol'),
        ('diesel','Diesel'),
        ('gas','Gasoline'),
        ('electric', 'Electrical')
    ])
    vehicle_color = fields.Char(
        string="Vehicle Colors"
    )
    odometer = fields.Char(
        string="Odometer Reading"
    )
    fuel_level = fields.Char(
        string="Fuel Level"
    )
    engine = fields.Char(
        string="Engine"
    )
    gear_nos = fields.Char(
        string="No. of Gears"
    )
    repair_category = fields.Many2one(
        'repair.category.custom',
        string="Repair Category"
    )
    detail = fields.Html(
        string="Service Details"
    )
    pay_type = fields.Selection([
        ('free', 'Free'),
        ('paid', 'Paid')
    ], string="Payment Type"
    )
    average_km = fields.Integer(
        string="Average KM/Day"
    )
    is_insurance = fields.Boolean(
        string="Is Insurance Claim"
    )
    insurance_company = fields.Char(
        string="Insurance Company"
    )
    image1 = fields.Binary(
        string="Image 1"
    )
    image2 = fields.Binary(
        string="Image 2"
    )
    image3 = fields.Binary(
        string="Image 3"
    )
    image4 = fields.Binary(
        string="Image 4"
    )
    image5 = fields.Binary(
        string="Image 5"
    )
    quality_check_name_ids = fields.One2many(
        'checklist.name.line', 'task_id',
        string="Checklist Names"
    )

    @api.onchange('quality_checklist_id')
    def _onchange_checklist_id(self):
        for rec in self:
            lines=[]
            for checklist in rec.quality_checklist_id:
                checklist_ids = self.mapped('quality_check_name_ids.checklist_id')
                if checklist._origin not in checklist_ids:
                    for name in checklist.checklist_name_ids:
                        lines.append((0,0,{'checklist_name_id':name._origin.id, 'checklist_id':checklist._origin.id, 'task_id': rec.id}))
            rec.quality_check_name_ids = lines