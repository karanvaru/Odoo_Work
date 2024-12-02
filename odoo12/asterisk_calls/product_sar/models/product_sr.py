# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _



class ProductSendAndRequest(models.Model):

    _name = "product.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Send and Request"

    @api.model
    def _default_source_location(self):
        """
            Get defaule source location
        """
        partner_location = self.env.ref('stock.stock_location_customers')
        if partner_location:
            return partner_location
        return False

    @api.model
    def _default_dest_location(self):
        """
            Get default destination location
        """
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        if warehouse_id:
            return warehouse_id.lot_stock_id
        return False

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string="Helpdesk Ticket", track_visibility='onchange')
    customer_id = fields.Many2one("res.partner" , string="Customer",
                                  # related='helpdesk_ticket_id.x_studio_end_customer_company',
                                  track_visibility='onchange',store="True")
    serial_num = fields.Char("Serial No",
                             # related='helpdesk_ticket_id.x_studio_serial_no',
                             track_visibility='always')
    # model_name = fields.Selection("Model Name",
    #                               # related='helpdesk_ticket_id.x_studio_model_name',
    #                               track_visibility='always')
    pspr_assign_to= fields.Many2one('res.users',string='Assign To',track_visibility='onchange', states={'draft': [('readonly', False)]},domain=[('is_int_user','=',True)])
    pspr_customer = fields.Many2one('res.partner', string='Customer')
    name = fields.Char(string='PSPR ID', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('part_request', 'PART REQUEST'),
        ('request_accept', 'REQUEST ACCEPTED'),
        ('purchase_request', 'PURCHASE REQUEST'),
        # ('received_material', 'RECEIVED MATERIAL'),
        ('part_dispatched', 'DISPATCHED'),
        ('part_reached', 'REACHED TO CX'),
        ('repair_started', 'Repair started'),
        ('repaired', 'Repaired'),
        ('request_for_part_pickup', 'PICKUP INITIATED'),
        ('in_transit', 'Return Picked'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),

    ], string='Status', readonly=True, default='draft',track_visibility='always')
    part_details_ids = fields.One2many('part.details', 'pspr_reference_id', string="Part Details")
    part_pspr_details = fields.Many2many('part.details',string="Part Details")
    street = fields.Char('Street',
                         # related='helpdesk_ticket_id.x_studio_street'
                         )
    street2 = fields.Char('Street2',
                          # related='helpdesk_ticket_id.x_studio_street_2'
                          )
    city = fields.Char('City',
                       # related='helpdesk_ticket_id.x_studio_city'
                       )
    pincode = fields.Char('Pincode',
                          # related='helpdesk_ticket_id.x_studio_pincode'
                          )
    state_name = fields.Char('State Name',
                             # related='helpdesk_ticket_id.x_studio_state'
                             )
    country = fields.Many2one('res.country', 'Country',
                              # related='helpdesk_ticket_id.x_studio_country'
                              )
    email = fields.Char('Email',
                        # related='helpdesk_ticket_id.x_studio_email'
                        )
    phone = fields.Char('Phone',
                        # related='helpdesk_ticket_id.x_studio_mobile'
                        )
    contact_person = fields.Many2one('res.partner','Contact person', related='helpdesk_ticket_id.x_studio_contact_person' ,store="True")
    inward_screen = fields.Integer('Inward Screen',compute="inward_count")
    repair_count_id = fields.Integer('repair count',compute="repair_count")
    helpdesk_product = fields.Many2one('product.product', string ="Helpdesk Product" ,related ='helpdesk_ticket_id.serial_product',store="True")
    helpdesk_lot_id = fields.Many2one('stock.production.lot',string="Helpdesk Serial No",related='helpdesk_ticket_id.product_serial_no',store="True")


    @api.multi
    def inward_count(self):
        for order in self:
            stock_picking_ids = self.env['stock.picking'].search_count([('picking_type_code', 'ilike', 'internal'),('pspr_stock_id','=',order.id)])
            order.inward_screen = stock_picking_ids

    @api.multi
    def repair_count(self):
        count_values = self.env['repair.order'].search_count([('pspr_repair_id','=',self.id)])
        self.repair_count_id = count_values

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('product.details.sequence'),
        })
        return super(ProductSendAndRequest, self).create(vals)




    @api.multi
    def action_to_part_request(self):
        self.state = 'part_request'

    # @api.multi
    # def action_to_request_accept(self):
    #     self.state = 'request_accept'

    @api.multi
    def action_to_part_dispatched(self):
        self.state = 'part_dispatched'

    @api.multi
    def action_to_part_reached(self):
        self.state = 'part_reached'

    @api.multi
    def action_to_request_for_part_pickup(self):
        pspr_details = self.env['stock.picking']

        # pspr_part_lines = self.env['part.details']
        # for product in self.part_details_ids

        vals = {
            'partner_id': self.customer_id.id,
            'location_id': 11,
            'location_dest_id': 11,
            'picking_type_id': 5,
            'picking_type_code': 'internal',
            'pspr_stock_id': self.id,
            'move_ids_without_package': [(0, 0,{'product_id': product.product.id, 'product_uom_qty': product.part_rq_qty, 'name': "test", 'product_uom': 1, 'location_id': 11, 'location_dest_id': 11})for product in self.part_details_ids]

        }
        new_val = pspr_details.create(vals)
        self.state = 'request_for_part_pickup'

        return new_val

    @api.multi
    def action_to_in_transit(self):
        self.state = 'in_transit'

    @api.multi
    def action_to_closed(self):
        # self.closed_date = datetime.datetime.now()
        self.state = 'closed'

    # @api.multi
    # def action_to_hold(self):
    #     self.state = 'hold'

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_to_purchase_request(self):
        self.write({'state': 'purchase_request'})

    # @api.multi
    # def action_to_received_material(self):
    #     self.write({'state': 'received_material'})

    @api.multi
    def action_to_partsend(self):

        self.write({'state': 'part_dispatched'})

    @api.multi
    def action_to_repaired(self):

        self.write({'state': 'repaired'})

    def open_inward_screen(self):

            self.ensure_one()
            return {
                'name': 'Internal screen',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('picking_type_code', '=', 'internal'),('pspr_stock_id','=',self.id)],
            }

    def open_repair_screen(self):
        self.ensure_one()
        return {
            'name': 'Repair Screen',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'domain': [('invoice_method', 'ilike', 'none'),('pspr_repair_id','=',self.id)],
        }


    @api.multi
    def action_to_request_accept(self, vals):



        pspr_details = self.env['stock.picking']

        # pspr_part_lines = self.env['part.details']
        # for product in self.part_details_ids

        vals = {
            'partner_id': self.customer_id.id,
            'location_id': 11,
            'location_dest_id': 11,
            'picking_type_id': 5,
            'picking_type_code': 'internal',
            'pspr_stock_id': self.id,
            'move_ids_without_package':[(0,0, {'product_id':product.product.id,'product_uom_qty':product.part_rq_qty,'name':"test",'product_uom':1,'location_id':11,'location_dest_id':11}) for product in self.part_details_ids]

        }
        new_val = pspr_details.create(vals)
        self.state = 'request_accept'

        return new_val

    @api.multi
    def action_to_repair_request(self, vals):

        pspr_repair_details = self.env['repair.order']

        vals = {
            'product_id': self.helpdesk_product.id,
            'product_qty': 1,
            'product_uom': 1,
            'lot_id': self.helpdesk_lot_id.id,
            'location_id': 12,
            'invoice_method': 'none',
            'pspr_repair_id': self.id,


        }
        updated_val = pspr_repair_details.create(vals)
        self.state = 'repair_started'

        return updated_val



class PartDetails(models.Model):
    _name = "part.details"
    _description = "Part Details"

    pspr_reference_id = fields.Many2one('product.details','PR Reference')
    part_name = fields.Many2one('pspr_part.name',string="Part Name")
    part_desc = fields.Text(string="Part Description")
    part_rq_qty = fields.Integer(string="Request QTY")
    part_sent_qty = fields.Integer(string="Sent QTY")
    part_rv_qty = fields.Integer(string="Received QTY")
    product = fields.Many2one('product.product',string="Product")


class PSPRPartDetails(models.Model):
    _name = "pspr_part.name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PSPR Part Details"

    name = fields.Char(string="Name", track_visibility='always')

class StockPicking(models.Model):
    _inherit = "stock.picking"

    pspr_stock_id = fields.Many2one('product.details', string = "PSPR")


class RepairCountValues(models.Model):
    _inherit = "repair.order"

    pspr_repair_id = fields.Many2one('product.details', string = "PSPR Repair")














