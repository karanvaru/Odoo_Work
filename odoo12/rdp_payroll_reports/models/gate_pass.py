from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import RedirectWarning, UserError, ValidationError



class GatePass(models.Model):
    _name = 'gate.pass'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Sequence Number',
                               readonly=True, default='New', required=True)
    partner_id = fields.Many2one('res.partner',string='Partner')
    company_id = fields.Many2one('res.company',string='Company')
    date = fields.Datetime(string='Date')
    picking = fields.Char(string='Picking')
    source_document = fields.Char(string='Source Document')
    reason = fields.Char(string='Remarks')
    product_details_ids = fields.One2many('product.details.line','product_details_id')
    gate_pass_line_ids = fields.One2many('vehicle.details.line','vehicle_details_id')
    state = fields.Selection([('draft', 'Draft'),
                                 ('confirmed', 'Confirmed'),
                                 ('cancel', 'Cancel')], string='Status', default='draft')
   
    @api.multi
    def create(self, vals):
        print(vals)
        print(self)
        vals['name'] = self.env['ir.sequence'].next_by_code('gate.pass.sequence')
        res = super(GatePass, self).create(vals)
        return res

    @api.multi
    def print_gatepass(self):
        if self.gate_pass_line_ids:
            return self.env.ref('rdp_gatepass.report_rdp_gatepass').report_action(self)
        else:
            raise ValidationError("Please fill the Vehicle Details...")
        
    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_confirmed(self):
        for rec in self:
            print('============================',rec.gate_pass_line_ids)
            if rec.gate_pass_line_ids:
                rec.state = 'confirmed'
            else:
                raise ValidationError("Please fill the Vehicle Details before Confirm...")



class ProductDetails(models.Model):
    _name = 'product.details.line'

    product_details_id = fields.Many2one('gate.pass')
    product = fields.Many2one('product.product',string='Product')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    unit_of_measure = fields.Many2one('uom.uom',string='Unit Of Measure')
    # source_location = fields.Many2one('stock.picking',string='Source Location')
    # resigned = fields.Many2one('stock.picking',string='Designation')

class VehicleDetails(models.Model):
    _name = 'vehicle.details.line'

    vehicle_details_id = fields.Many2one('gate.pass')
    vehicle_number = fields.Char(string='vehicle Number')
    driver_name = fields.Char(string='Driver Name')
    phone_number = fields.Char(string='Phone Number')
    alternative_number = fields.Char(string='Alternative Number')