from odoo  import models,fields,api,_
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockPickingExtended(models.Model):
    _inherit = "stock.picking"

    gate_pass = fields.Many2one('gate.pass', string="Gate Pass",readonly=1)
    gate_pass_hide = fields.Boolean('Gate Pass Hide')
    vehicle_detail_ids = fields.One2many('transport.details', 'stock_picking_id')
    transport_details_ids = fields.One2many('vehicle.details.line', 've_picking_id')
    no_of_shipping_boxes = fields.Integer(String="Number Of Boxes")
    logistic_executive = fields.Many2one('hr.employee', string='Logistic Executive')

    @api.multi
    def create_gate_pass(self):
        for rec in self:
            sale_record = rec.env['sale.order'].search([('id', '=', rec.sale_id.id)])
            invoice_id = rec.env['account.invoice'].search([('origin', '=', sale_record.name)], limit=1)
            invoice = invoice_id.move_id.name
            gate_pass = rec.env['gate.pass'].search([('picking_id', '=', rec.id)])
            if rec.vehicle_detail_ids or rec.transport_details_ids:
                for record in rec.vehicle_detail_ids:
                    if not record.partner_transport_id:
                        if not record.date:
                            if not record.transport_number:
                                raise ValidationError("Please Fill the Vehicle details before generating gate pass...")
                # if rec.transport_details_ids:
                for transport in rec.transport_details_ids:
                    if not transport.partner_vehicle_id:
                        if not transport.doc_date:
                            if not transport.alternative_number:
                                raise ValidationError("Please  Fill the Transport Details before generating gate pass...")
            # if not rec.transport_details_ids:
            #     raise ValidationError("Please  Fill the Transporter details before generating gate pass...")
            else:
                raise ValidationError("Please Fill the Vehicle/Transporter details before generating gate pass...")
            if not rec.logistic_executive:
                raise ValidationError("Please  Fill the Logistic Executive ...")
            if not rec.no_of_shipping_boxes:
                raise ValidationError("Please  Fill the Total Boxes ...")
            if not gate_pass:
                vals = {
                    'picking_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'company_id': rec.company_id.id,
                    'date': datetime.today(),
                    'picking': rec.name,
                    'invoice_number': invoice,
                    'logistic_executive': rec.logistic_executive.id,
                    'number_of_shipping_boxes': rec.no_of_shipping_boxes,
                    'source_document': rec.origin,
                    'product_details_ids': [(0,0,{
                        'product': line.product_id.id,
                        'description': line.name,
                        'quantity': line.quantity_done,
                        'unit_of_measure': line.product_uom.id,
                    })for line in rec.move_ids_without_package],
                    'transport_ids':[(0,0,{
                        # 'transport_name': record.transport_name,
                        'partner_transport_id':record.partner_transport_id.id,
                        'date': record.date,
                        'transport_number': record.transport_number,
                        'person_name': record.person_name,
                        'ph_number':record.ph_number,
                    })for record in rec.vehicle_detail_ids],
                    'gate_pass_line_ids': [(0,0,{
                        # 'doc_name': tr.doc_name,
                        'partner_vehicle_id': tr.partner_vehicle_id.id,
                        'doc_date': tr.doc_date,
                        'p_name': tr.p_name,
                        'phone_number': tr.phone_number,
                        'alternative_number': tr.alternative_number,
                    })for tr in rec.transport_details_ids]

                }
                res = rec.env['gate.pass'].create(vals)
                rec.gate_pass = res.id
                rec.gate_pass_hide = True
        else:
            product=[(5,0,0)]
            for line in rec.vehicle_detail_ids:
                product.append({
                    'partner_transport_id': line.partner_transport_id.id,
                    # 'transport_name': line.transport_name.id,
                    'date': line.date,
                    'transport_number': line.transport_number,
                    'person_name': line.person_name,
                    'ph_number': line.ph_number,
                })

            product_line = [5,0,0]
            for pr in rec.move_ids_without_package:
                product_line.append({
                    'product': pr.product_id.id,
                    'description': pr.name,
                    'quantity': pr.quantity_done,
                    'unit_of_measure': pr.product_uom.id,
                })

            transport = [5,0,0]
            for tr in rec.transport_details_ids:
                transport.append({
                    # 'doc_name': tr.doc_name.id,
                    'partner_vehicle_id': tr.partner_vehicle_id.id,
                    'doc_date': tr.doc_date,
                    'p_name': tr.p_name,
                    'phone_number': tr.phone_number,
                    'alternative_number': tr.alternative_number,
                })

            vals = {
                'picking_id': rec.id,
                'partner_id': rec.partner_id.id,
                'company_id': rec.company_id.id,
                'date': datetime.today(),
                'picking': rec.name,
                'invoice_number': invoice,
                'source_document': rec.origin,
                'logistic_executive': rec.logistic_executive.id,
                'number_of_shipping_boxes': rec.no_of_shipping_boxes,
                'product_details_ids': product_line,
                'transport_ids': product,
                'gate_pass_line_ids': transport

            }
            gate_pass.update(vals)



