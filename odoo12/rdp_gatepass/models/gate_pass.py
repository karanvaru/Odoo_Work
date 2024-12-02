from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import RedirectWarning, UserError, ValidationError



class GatePass(models.Model):
    _name = 'gate.pass'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    picking_id = fields.Many2one('stock.picking')
    name = fields.Char(string='Sequence Number',
                               readonly=True, default='New', required=True)
    partner_id = fields.Many2one('res.partner',string='Partner')
    company_id = fields.Many2one('res.company',string='Company')
    date = fields.Datetime(string='Created Date')
    picking = fields.Char(string='Picking')
    source_document = fields.Char(string='Source Document')
    reason = fields.Char(string='Internal Notes')
    number_of_shipping_boxes = fields.Integer(string="Number Of Boxes")
    product_details_ids = fields.One2many('product.details.line','product_details_id')
    gate_pass_line_ids = fields.One2many('vehicle.details.line','vehicle_details_id')
    confirmed_date = fields.Datetime(string="Confirmed Date")
    state = fields.Selection([('draft', 'Draft'),
                                 ('confirmed', 'Confirmed'),
                                 ('cancel', 'Cancel')], string='Status', default='draft')
    loader = fields.Many2many('hr.employee', string="Loader")
    logistic_executive = fields.Many2one('hr.employee', string="Logistic Executive")
    invoice_number = fields.Char(string="Invoice Number")
    transport_ids = fields.One2many('transport.details', 'transport_id', string="Vehicle Details")

    @api.model
    def create(self, vals):
        print(vals)
        print(self)
        vals['name'] = self.env['ir.sequence'].next_by_code('gate.pass.sequence')
        res = super(GatePass, self).create(vals)
        return res

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_confirmed(self):
        for rec in self:
            print('============================', rec.gate_pass_line_ids)
            # if rec.gate_pass_line_ids:
            rec.confirmed_date = datetime.today()
            rec.state = 'confirmed'
            # else:
            #     raise ValidationError("Please  Fill the Vehicle Details before Confirm...")
            #


class ProductDetails(models.Model):
    _name = 'product.details.line'

    product_details_id = fields.Many2one('gate.pass')
    product = fields.Many2one('product.product',string='Product')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    unit_of_measure = fields.Many2one('uom.uom',string='Unit Of Measure')


class TraansportDetails(models.Model):
    _name = 'transport.details'

    stock_picking_id = fields.Many2one('stock.picking')
    transport_id = fields.Many2one('gate.pass')
    partner_transport_id = fields.Many2one('res.partner', string='Transport Name')
    transport_name = fields.Char(string="Transporter Name")
    date = fields.Datetime(string='Date')
    transport_number = fields.Char(string='Vehicle Number')
    person_name = fields.Char(string='Person Name')
    ph_number = fields.Char(string="Mobile Number")

class VehicleDetails(models.Model):
    _name = 'vehicle.details.line'

    ve_picking_id = fields.Many2one('stock.picking')
    vehicle_details_id = fields.Many2one('gate.pass')
    doc_name = fields.Char(string='Transporter Name')
    partner_vehicle_id = fields.Many2one('res.partner', string="Transporter Name")
    doc_date = fields.Datetime(string='Docket Date')
    p_name = fields.Char(string='Person Name')
    phone_number = fields.Char(string='Mobile Number')
    alternative_number = fields.Char(string="Docket Number")
