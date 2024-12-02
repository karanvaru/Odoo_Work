# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from time import strptime
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductSendAndRequest(models.Model):
    _name = "product.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Send and Request"

    ############  action_to_request_accept   ############

    location_id = fields.Many2one(
        'stock.location',
        'Source Location',

    )
    dest_location_id = fields.Many2one(
        'stock.location',
        'Destination Location',
    )
    stock_picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Picking Type',
        default=lambda self: self._default_picking_type()
    )
    is_accept = fields.Boolean("Accept")

    ############  action_to_repair_request   ############

    repair_location_id = fields.Many2one(
        'stock.location',
        'Repair Location',
    )
    is_repair = fields.Boolean("Repair")

    ############  action_to_request_for_part_pickup   ############

    part_pickup_source_location_id = fields.Many2one(
        'stock.location',
        'Part Pickup Source Location',
    )

    part_pickup_dest_location_id = fields.Many2one(
        'stock.location',
        'Part Pickup Dest Location',
    )

    is_part_pickup = fields.Boolean("Part Pickup")

    ############  action_to_sent_to_rma_tech   ############

    rma_source_location_id = fields.Many2one(
        'stock.location',
        'RMA Source Location',
    )

    rma_dest_location_id = fields.Many2one(
        'stock.location',
        'RMA Dest Location',
    )

    is_rma_tech = fields.Boolean("RMA Tech")

    @api.model
    def _default_picking_type(self):
        company_id = self.env.user.company_id.id,
        picking_type = self.env['stock.picking.type'].sudo().search(
            [('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        return picking_type


    @api.onchange('stock_picking_type_id')
    def onchange_stock_picking_type_id(self):
        self.location_id = self.stock_picking_type_id.default_location_src_id.id
        self.dest_location_id = self.stock_picking_type_id.default_location_dest_id.id

        self.part_pickup_source_location_id = self.stock_picking_type_id.default_location_src_id.id
        self.part_pickup_dest_location_id = self.stock_picking_type_id.default_location_dest_id.id

        self.rma_source_location_id = self.stock_picking_type_id.default_location_src_id.id
        self.rma_dest_location_id = self.stock_picking_type_id.default_location_dest_id.id

        self.repair_location_id = self.stock_picking_type_id.default_location_src_id.id

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
    pspr_closed_days = fields.Datetime('Closed Date')
    pspr_open_days = fields.Char('Open Days', compute="calulate_pspr_open_days")

    # Dayan 26.10.2022 ====================================Own=======================================
    # customer_id = fields.Many2one("res.partner" , string="Customer", related='helpdesk_ticket_id.x_studio_end_customer_company',track_visibility='onchange',store="True")
    customer_id = fields.Many2one("res.partner", string="Customer", track_visibility='onchange', store="True")
    # customer_id = fields.Many2one("res.partner" , string="Customer",track_visibility='onchange',store="True")

    # Dayan 26.10.2022 ====================================Own=======================================
    # serial_num = fields.Char("Serial No",related='helpdesk_ticket_id.x_studio_serial_no',track_visibility='always')
    serial_num = fields.Char("Serial No", track_visibility='always')
    # serial_num = fields.Char("Serial No",track_visibility='always')

    # Dayan 26.10.2022 ==================================Own=========================================
    # model_name = fields.Selection("Model Name", track_visibility='always')
    # model_name = fields.Selection("Model Name", related='helpdesk_ticket_id.x_studio_model_name',track_visibility='always')
    # model_name = fields.Selection("Model Name", track_visibility='always')
    pspr_assign_to = fields.Many2one('res.users', string='Assign To', track_visibility='onchange',
                                     states={'draft': [('readonly', False)]}, domain=[('is_int_user', '=', True)])
    pspr_customer = fields.Many2one('res.partner', string='Customer')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    # Test Records========30.10.2022=========================Product==Details===========================Dayan=========================
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('part_request', 'PART REQUEST'),
        ('request_accept', 'REQUEST ACCEPTED'),
        ('purchase_request', 'PURCHASE REQUEST'),
        ('part_dispatched', 'DISPATCHED'),
        ('part_reached', 'REACHED TO CX'),
        ('repair_started', 'REPLACED COMPONENT'),
        ('repaired', 'UPDATED IN REPAIR APP'),
        ('request_for_part_pickup', 'INITIATE PICKUP'),
        ('ready_for_pickup', 'READY FOR PICKUP'),
        ('in_transit', 'RETURN PICKED'),
        ('return_received', 'RETURN RECEIVED'),
        ('sent_to_rma_tech', 'SENT TO RMA TECH'),
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')

    ####adding product_id in filters##############
    ps_product_id = fields.Many2one('product.product', 'Product', compute="compute_product_name", store=True)
    # Dayan Created on 29.10.2022 ==============================Date=============in=========================
    draft_in = fields.Datetime('Draft In', compute='compute_draft_in_date')
    # draft_in = fields.Datetime('Draft In')
    part_request_in = fields.Datetime('Part Request In')
    request_accept_in = fields.Datetime('Request Accept In')
    purchase_request_in = fields.Datetime('Purchase Request In')
    part_dispatched_in = fields.Datetime('Part Dispatched In')
    part_reached_in = fields.Datetime('Part Reached In')
    repair_started_in = fields.Datetime('Repair Start In')
    repaired_in = fields.Datetime('Repaired In')
    request_for_part_pickup_in = fields.Datetime('Part Pickup In')
    in_transit_in = fields.Datetime('Transit In')
    closed_in = fields.Datetime('Close In')
    cancel_in = fields.Datetime('Cancel In')

    # Dayan Created on 29.10.2022 ==============================Date=============out=========================
    draft_out = fields.Datetime('Draft Out')
    part_request_out = fields.Datetime('Part Request Out')
    request_accept_out = fields.Datetime('Request Accept Out')
    purchase_request_out = fields.Datetime('Purchase Request Out')
    part_dispatched_out = fields.Datetime('Part Dispatched Out')
    part_reached_out = fields.Datetime('Part Reached Out')
    repair_started_out = fields.Datetime('Repair Start Out')
    repaired_out = fields.Datetime('Repaired Out')
    request_for_part_pickup_out = fields.Datetime('Part Pickup Out')
    in_transit_out = fields.Datetime('Transit Out')
    closed_out = fields.Datetime('Close Out')
    cancel_out = fields.Datetime('Cancel Out')

    # Dayan Created on 29.10.2022 =======================Date========Open Stage=============Total===============
    draft_days = fields.Char('Draft Open Days')
    part_request_days = fields.Char('Part Request Days')
    request_accept_days = fields.Char('Request Accept Days')
    purchase_request_days = fields.Char('Purchase Request Days')
    part_dispatched_days = fields.Char('Part Dispatched Days')
    part_reached_days = fields.Char('Part Reached Days')
    repair_started_days = fields.Char('Repair Start Days')
    repaired_days = fields.Char('Repaired Days')
    request_for_part_pickup_days = fields.Char('Part Pickup Days')
    in_transit_days = fields.Char('Transit Days')
    closed_days = fields.Datetime('Close Days')
    # closed_days = fields.Char('Close Days', compute="compute_closed_date")
    cancel_days = fields.Char('Cancel Days')
    ready_for_pickup_days = fields.Char('Ready For Pickup Days')
    return_receive_days = fields.Char('Return Receive Days')

    # Dayan 26.10.2022 ===========================================================================

    part_details_ids = fields.One2many('part.details', 'pspr_reference_id', string="Part Details")
    part_pspr_details = fields.Many2many('part.details', string="Part Details")
    # street = fields.Char('Street', related='helpdesk_ticket_id.x_studio_street')
    street = fields.Char('Street', )
    # street2 = fields.Char('Street2', related='helpdesk_ticket_id.x_studio_street_2')
    street2 = fields.Char('Street2', )
    # city = fields.Char('City', related='helpdesk_ticket_id.x_studio_city')
    city = fields.Char('City')
    # pincode = fields.Char('Pincode', related='helpdesk_ticket_id.x_studio_pincode')
    pincode = fields.Char('Pincode')
    # state_name = fields.Char('State Name', related='helpdesk_ticket_id.x_studio_state')
    state_name = fields.Char('State Name')
    # country = fields.Many2one('res.country', 'Country', related='helpdesk_ticket_id.x_studio_country')
    country = fields.Many2one('res.country', 'Country')
    # email = fields.Char('Email', related='helpdesk_ticket_id.x_studio_email')
    email = fields.Char('Email', )
    # phone = fields.Char('Phone', related='helpdesk_ticket_id.x_studio_mobile')
    phone = fields.Char('Phone')
    # contact_person = fields.Many2one('res.partner','Contact person', related='helpdesk_ticket_id.x_studio_contact_person' ,store="True")
    contact_person = fields.Many2one('res.partner', 'Contact person', store="True")
    inward_screen = fields.Integer('Inward Screen', compute="inward_count")
    repair_count_id = fields.Integer('repair count', compute="repair_count")
    purchase_tender_count = fields.Integer('Purchase Tender count', compute="compute_purchase_tender_count")
    helpdesk_product = fields.Many2one('product.product', string="Helpdesk Product",
                                       related='helpdesk_ticket_id.serial_product', store="True")
    helpdesk_lot_id = fields.Many2one('stock.production.lot', string="Helpdesk Serial No",
                                      related='helpdesk_ticket_id.product_serial_no', store="True")

    # ======

    # part_details_ids = fields.One2many('part.details', 'pspr_reference_id', string="Part Details")
    # part_pspr_details = fields.Many2many('part.details',string="Part Details")
    # street = fields.Char('Street')
    # street2 = fields.Char('Street2')
    # city = fields.Char('City')
    # pincode = fields.Char('Pincode')
    # state_name = fields.Char('State Name')
    # country = fields.Many2one('res.country', 'Country')
    # email = fields.Char('Email')
    # phone = fields.Char('Phone')
    # contact_person = fields.Many2one('res.partner','Contact person',store="True")
    # inward_screen = fields.Integer('Inward Screen',compute="inward_count")
    # repair_count_id = fields.Integer('repair count',compute="repair_count")
    # helpdesk_product = fields.Many2one('product.product', string ="Helpdesk Product")
    # helpdesk_lot_id = fields.Many2one('stock.production.lot',string="Helpdesk Serial No")# Dayan Created on 29.10.2022 ==============================Date=============out=========================

    # sabitha Created on 27.02.2023 =======================Extra fields in List View relared to Helpdesk=========================================
    # h_stage_id = fields.Many2one('helpdesk.stage','Helpdesk Stage')
    # h_team_id = fields.Many2one('helpdesk.team','Helpdesk Team')
    helpdesk_state_id = fields.Many2one('helpdesk.stage', 'HD Status', compute="compute_hd_team_status", store=True)
    helpdesk_team_id = fields.Many2one('helpdesk.team', 'HD Team', compute="compute_hd_team_status", store=True)
    opendays_count = fields.Integer('Opendays Count', compute="compute_opendays_count", store=True)
    category_id = fields.Many2one('pspr.category', string="Category", track_visibility='always')
    sub_category_id = fields.Many2one('pspr.sub.category', string="Sub Category", track_visibility='always')
    tag_ids = fields.Many2many('pspr.tags', 'pspr_tags_rel', 'name', string='Tags',
                               track_visibility='onchange')
    # sabitha Created on 31.03.2023 =======================Extra fields in
    part_value_id = fields.Many2one('pspr.part.value', string='Part Value', track_visibility="onchange", required=True)
    no_damage_id = fields.Many2one('pspr.no.damage', string='No Damage(2.0)', track_visibility="onchange",
                                   required=True)
    internal_notes = fields.Html(string='Internal Notes', track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', track_visibility='onchange',
                                 default=lambda self: self.env.user.company_id)
    assigned_id = fields.Many2one('res.users', string="Assigned To", track_visibility='onchange')
    is_damaged = fields.Boolean('Damage 2.0', track_visibility='always')
    damaged_date = fields.Datetime('Damage 2.0 Assign Date')
    damage_category_id = fields.Many2one('pspr.damage.category', 'Damage(2.0) Category', track_visibility='onchange')

    closed_date = fields.Datetime('Closed Date')
    cancel_date = fields.Datetime('Cancel Date')
    total_opendays = fields.Char('Open Days', compute="compute_opendays")
    part_request_opendays = fields.Char('Part Request Open Days', compute="compute_part_request_opendays")
    current_stage_in = fields.Datetime('Current Stage Datetime')
    current_stage_opendays = fields.Char('Current Stage Open Days', compute="compute_current_stage_opendays")
    complete_cycle_opendays = fields.Char('Complete Cycle OD', compute="compute_complete_cycle")
    part_request_date = fields.Datetime('Part Reuest Date')
    ready_for_pickup_in = fields.Datetime('Ready For Pickup In')
    ready_for_pickup_out = fields.Datetime('Ready For Pickup Out')
    return_received_in = fields.Datetime('Return Received In')
    return_received_out = fields.Datetime('Return Received In')
    company_ids = fields.Many2many('res.company', string="Companies", required=True,
                                   default=lambda self: self.env.user.company_id,
                                   help="When require multiple companies than select useful companies.")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Retrieve the current user's company and its child companies
        current_company = self.env.user.company_id
        child_company_ids = current_company | current_company.child_ids

        # Apply the domain filter to include current company and child companies
        args.append(('company_id', 'in', child_company_ids.ids))

        return super(ProductSendAndRequest, self).search(args, offset, limit, order, count)

    @api.onchange('no_damage_id')
    def onchange_no_damage_id(self):
        for rec in self:
            # _logger.info("------after rec----------")
            if rec.no_damage_id.id == 10:
                # _logger.info("------immediate if----------")
                rec.damaged_date = datetime.today()
                # _logger.info("------after if----------",rec.damaged_date)
                rec.is_damaged = True
                # if rec.is_damaged == True:

    @api.multi
    def compute_opendays(self):
        for record in self:
            c_date = record.create_date
            today = datetime.today()
            if record.closed_date:
                closed_d = datetime.strftime(record.closed_date, '%Y-%m-%d %H:%M:%S')
                closed_dt = datetime.strptime(closed_d, '%Y-%m-%d %H:%M:%S')
                create_d = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M:%S')
                create_dt = datetime.strptime(create_d, '%Y-%m-%d %H:%M:%S')

                record.total_opendays = (closed_dt - create_dt)
                # record.total_opendays =record.total_opendays[:-10] 
                # record['total_opendays'] = record.total_opendays.split('.')[0]

            elif record.cancel_date:
                cancel_d = datetime.strftime(record.cancel_date, '%Y-%m-%d %H:%M:%S')
                cancel_dt = datetime.strptime(cancel_d, '%Y-%m-%d %H:%M:%S')
                create_d = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M:%S')
                create_dt = datetime.strptime(create_d, '%Y-%m-%d %H:%M:%S')

                record.total_opendays = (cancel_dt - create_dt)
                # record.total_opendays =record.total_opendays[:-10] 
            else:
                create_d = datetime.strftime(record.create_date, '%Y-%m-%d %H:%M:%S')
                create_dt = datetime.strptime(create_d, '%Y-%m-%d %H:%M:%S')
                today_t = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
                today_dt = datetime.strptime(today_t, '%Y-%m-%d %H:%M:%S')
                record.total_opendays = (today_dt - create_dt)
                # record.total_opendays =record.total_opendays

                # record['total_opendays'] = str((datetime.today())- c_date)

    #             # record['total_opendays'] = record.total_opendays.split('.')[0]
    # @api.multi
    # def compute_part_request_opendays(self):
    #     for rec in self:
    #         date_in = rec.draft_out
    #         date_out = rec.part_request_out
    #         if rec.part_request_out and rec.part_request_in:
    #         # td = datetime.today()
    #         # if rec.part_request_out:
    #         #     start = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
    #         #     end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
    #         #     start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    #         #     end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    #         #     rec.part_request_opendays = end_last - start_last
    #         # else:
    #         #     start_d = datetime.strftime(td, '%Y-%m-%d %H:%M:%S')  
    #         #     start =   datetime.strptime(start_d, '%Y-%m-%d %H:%M:%S') 
    #         #     end_d = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')  
    #         #     end = datetime.strptime(end_d, '%Y-%m-%d %H:%M:%S')
    #         #     rec.part_request_opendays = start - end

    #             # rec['part_request_opendays'] = str(date_out - date_in)
    #             p_date_in = datetime.strftime(rec.draft_out, '%Y-%m-%d %H:%M')
    #             p_date_in_dt = datetime.strptime(p_date_in, '%Y-%m-%d %H:%M')
    #             p_date_out = datetime.strftime(rec.part_request_out, '%Y-%m-%d %H:%M')
    #             p_date_out_dt = datetime.strptime(p_date_out, '%Y-%m-%d %H:%M')
    #             rec.part_request_opendays = (p_date_out_dt - p_date_in_dt)
    #             rec.part_request_opendays = rec.current_stage_opendays.split('.')[0]

    #             # rec.part_request_opendays = rec.part_request_opendays.split('.')[0]
    #         elif rec.part_request_in: 
    #             today = datetime.today()
    #             today_t = datetime.strftime(today, '%Y-%m-%d %H:%M')
    #             today_dt = datetime.strptime(today_t, '%Y-%m-%d %H:%M')
    #             pr_date_out = datetime.strftime(rec.draft_out, '%Y-%m-%d %H:%M')
    #             pr_date_out_dt = datetime.strptime(pr_date_out, '%Y-%m-%d %H:%M')
    #             rec.part_request_opendays = (today_dt - pr_date_out_dt)
    #             rec.part_request_opendays = rec.current_stage_opendays.split('.')[0]

    #             #  rec['part_request_opendays'] = str(datetime.today() - date_in)
    #             #  rec.part_request_opendays = rec.part_request_opendays.split('.')[0]
    #         else:
    #              rec.part_request_opendays = 0

    # @api.multi
    # @api.onchange('no_damage_id')
    # def onchange_no_damage_id(self):
    #     # _logger.info("------Tafter rec----------")
    #     for rec in self:
    #         # _logger.info("------after rec----------")
    #         if rec.no_damage_id.id == 10:
    #             # _logger.info("------immediate if----------")
    #             rec.damaged_date = datetime.today()
    #             # _logger.info("------after if----------",rec.damaged_date)
    #             rec.is_damaged = True
    # if rec.is_damaged == True:

    @api.multi
    def compute_part_request_opendays(self):
        for rec in self:
            date_in = rec.draft_out
            date_out = rec.part_request_out
            if rec['part_request_out'] and rec['part_request_in']:
                # td = datetime.today()
                # if rec.part_request_out:
                #     start = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
                #     end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
                #     start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                #     end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                #     rec.part_request_opendays = end_last - start_last
                # else:
                #     start_d = datetime.strftime(td, '%Y-%m-%d %H:%M:%S')
                #     start =   datetime.strptime(start_d, '%Y-%m-%d %H:%M:%S')
                #     end_d = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
                #     end = datetime.strptime(end_d, '%Y-%m-%d %H:%M:%S')
                #     rec.part_request_opendays = start - end

                rec['part_request_opendays'] = str(date_out - date_in)
                rec.part_request_opendays = rec.part_request_opendays.split('.')[0]
            elif rec['part_request_in']:
                rec['part_request_opendays'] = str(datetime.today() - date_in)
                rec.part_request_opendays = rec.part_request_opendays.split('.')[0]
            else:
                rec['part_request_opendays'] = 0

    # @api.onchange('state')
    # def onchange_stage(self):
    #     for rec in self:
    #         rec.current_stage_in = datetime.today()  
    @api.multi
    def compute_current_stage_opendays(self):
        for rec in self:
            today = datetime.today()
            today_d = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
            today_dt = datetime.strptime(today_d, '%Y-%m-%d %H:%M:%S')

            if rec.state == 'draft':
                draft_d = datetime.strftime(rec.create_date, '%Y-%m-%d %H:%M:%S')
                draft_dt = datetime.strptime(draft_d, '%Y-%m-%d %H:%M:%S')
                rec.current_stage_opendays = (today_dt - draft_dt)
                rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'part_request':
                if rec.part_request_in:
                    partrq_d = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
                    partrq_dt = datetime.strptime(partrq_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - partrq_dt)
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'request_accept':
                if rec.request_accept_in:
                    request_accept_d = datetime.strftime(rec.request_accept_in, '%Y-%m-%d %H:%M:%S')
                    request_accept_dt = datetime.strptime(request_accept_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - request_accept_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.request_accept_in)
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'purchase_request':
                if rec.purchase_request_in:
                    purchase_request_d = datetime.strftime(rec.purchase_request_in, '%Y-%m-%d %H:%M:%S')
                    purchase_request_dt = datetime.strptime(purchase_request_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - purchase_request_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.purchase_request_in)
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'part_dispatched':
                if rec.part_dispatched_in:
                    part_dispatched_d = datetime.strftime(rec.part_dispatched_in, '%Y-%m-%d %H:%M:%S')
                    part_dispatched_dt = datetime.strptime(part_dispatched_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - part_dispatched_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.part_dispatched_in) 
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'part_reached':
                if rec.part_reached_in:
                    part_reached_d = datetime.strftime(rec.part_reached_in, '%Y-%m-%d %H:%M:%S')
                    part_reached_dt = datetime.strptime(part_reached_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - part_reached_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.part_reached_in) 
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'repair_started':
                if rec.repair_started_in:
                    repair_started_d = datetime.strftime(rec.repair_started_in, '%Y-%m-%d %H:%M:%S')
                    repair_started_dt = datetime.strptime(repair_started_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - repair_started_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.repair_started_in) 
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'repaired':
                if rec.repaired_in:
                    repaired_d = datetime.strftime(rec.repaired_in, '%Y-%m-%d %H:%M:%S')
                    repaired_dt = datetime.strptime(repaired_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - repaired_dt)
                    # rec.current_stage_opendays  = str(datetime.today()-  rec.repaired_in)  
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'request_for_part_pickup':
                if rec.request_for_part_pickup_in:
                    req_pickup_d = datetime.strftime(rec.request_for_part_pickup_in, '%Y-%m-%d %H:%M:%S')
                    req_pickup_dt = datetime.strptime(req_pickup_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - req_pickup_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.request_for_part_pickup_in)  
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'ready_for_pickup':
                if rec.ready_for_pickup_in:
                    ready_pickup_d = datetime.strftime(rec.ready_for_pickup_in, '%Y-%m-%d %H:%M:%S')
                    ready_pickup_dt = datetime.strptime(ready_pickup_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - ready_pickup_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.request_for_part_pickup_in)  
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'in_transit':
                if rec.in_transit_in:
                    in_transit_d = datetime.strftime(rec.in_transit_in, '%Y-%m-%d %H:%M:%S')
                    in_transit_dt = datetime.strptime(in_transit_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - in_transit_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.in_transit_in) 
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'return_received':
                if rec.return_received_in:
                    return_received_d = datetime.strftime(rec.return_received_in, '%Y-%m-%d %H:%M:%S')
                    return_received_dt = datetime.strptime(return_received_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - return_received_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.in_transit_in) 
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            elif rec.state == 'closed':
                if rec.closed_in:
                    closed_in_d = datetime.strftime(rec.closed_in, '%Y-%m-%d %H:%M:%S')
                    closed_in_dt = datetime.strptime(closed_in_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - closed_in_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.closed_in)  
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
            else:
                if rec.cancel_in:
                    cancel_in_d = datetime.strftime(rec.cancel_in, '%Y-%m-%d %H:%M:%S')
                    cancel_in_dt = datetime.strptime(cancel_in_d, '%Y-%m-%d %H:%M:%S')
                    rec.current_stage_opendays = (today_dt - cancel_in_dt)
                    # rec.current_stage_opendays  = str((datetime.today())-  rec.cancel_in)
                    rec.current_stage_opendays = rec.current_stage_opendays.split('.')[0]
                # rec.current_stage_opendays  = 0

    @api.multi
    def compute_complete_cycle(self):
        for rec in self:

            if rec.closed_date and rec.part_request_in:
                rec.complete_cycle_opendays = str(rec.closed_date - rec.part_request_in)
                rec.complete_cycle_opendays = rec.complete_cycle_opendays.split('.')[0]
            elif rec.cancel_date and rec.part_request_in:
                rec.complete_cycle_opendays = str(rec.cancel_date - rec.part_request_in)
                rec.complete_cycle_opendays = rec.complete_cycle_opendays.split('.')[0]

            elif rec.part_request_in:
                today = datetime.today()
                # part_rq_date = rec.part_request_date
                today_d = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
                today_dt = datetime.strptime(today_d, '%Y-%m-%d %H:%M:%S')
                part_rq_d = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
                part_rq_dt = datetime.strptime(part_rq_d, '%Y-%m-%d %H:%M:%S')
                rec.complete_cycle_opendays = (today_dt - part_rq_dt)
            else:
                rec.complete_cycle_opendays = 0

                # rec.complete_cycle_opendays = 0

    #         #    rec.ccod_days = rec.ccod_days.split('.')[0]
    #         #    _logger.info("------TODAY----------",type(today))
    #         #    _logger.info("------Part Request Date----------",type(part_rq_dt))
    #             # rec.ccod_days = str((datetime.today()) - rec.part_request_date)
    #             # rec.ccod_days = rec.ccod_days.split('.')[0]
    #              rec['ccod_days'] = str((datetime.today())- part_rq_date)

    #         #    rec.ccod_days = 0
    #         # if not rec.draft_out:
    #         #     rec.ccod_days = 0
    #         # # else:
    #         #     rec.ccod_days = 0

    # @api.multi
    # def compute_complete_cycle(self):
    #      for rec in self:
    #         part_rq_date = rec.part_request_date
    #         if rec.closed_date:
    #             rec.ccod_days = str(rec.closed_date - rec.draft_out)
    #             rec.ccod_days = rec.ccod_days.split('.')[0]
    #         elif rec.cancel_date:
    #             rec.ccod_days = str(rec.cancel_date - rec.draft_out)
    #             rec.ccod_days = rec.ccod_days.split('.')[0]
    #         else:
    #             rec['ccod_days'] =(datetime.today()- part_rq_date)

    @api.multi
    @api.depends('helpdesk_ticket_id', 'helpdesk_ticket_id.team_id', 'helpdesk_ticket_id.stage_id')
    def compute_hd_team_status(self):
        for rec in self:
            rec.helpdesk_team_id = rec.helpdesk_ticket_id.team_id.id
            rec.helpdesk_state_id = rec.helpdesk_ticket_id.stage_id.id

    @api.multi
    def compute_opendays_count(self):
        for rec in self:
            rec.opendays_count = rec.x_studio_date_count
        #     # records = rec.search([('x_studio_date_count', '>=', 0)], order='x_studio_date_count DESC')
        # return records

    @api.depends('part_details_ids.part_name')
    def compute_product_name(self):
        # _logger.info("------before self----------")
        pr_id = self.env['part.details']
        for rec in self:
            #     for pr_id in rec.part_details_ids:
            #         _logger.info("------before assigning----------",rec.part_details_ids)
            #         rec.ps_product_id = pr_id.product.id
            #         _logger.info("------after assigning----------",rec.ps_product_id)
            #  for pr in pr_id:
            for product in rec.part_details_ids:
                rec.ps_product_id = product.product.id

    @api.model
    def calulate_pspr_open_days(self):
        for rec in self:
            current_date = datetime.today()
            if rec.create_date:
                rec.pspr_open_days = str((current_date - rec.create_date).days) + " Days"

    def compute_draft_in_date(self):
        for rec in self:
            rec.draft_in = rec.create_date

    @api.multi
    def inward_count(self):
        for order in self:
            stock_picking_ids = self.env['stock.picking'].search_count([('pspr_stock_id', '=', order.id)])
            order.inward_screen = stock_picking_ids

    @api.multi
    def repair_count(self):
        count_values = self.env['repair.order'].search_count([('pspr_repair_id', '=', self.id)])
        self.repair_count_id = count_values

    @api.multi
    def compute_purchase_tender_count(self):
        tender_count = self.env['purchase.agreement'].search_count([('purchase_tender_id', '=', self.id)])
        self.purchase_tender_count = tender_count

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('product.details.sequence'),
        })
        return super(ProductSendAndRequest, self).create(vals)

    @api.multi
    def action_to_part_request(self):
        self.part_request_date = datetime.today()
        print("self.part_request_date", self.part_request_date)
        from_state = self.state
        from_date = self.draft_in
        # if self.env.user.company_id.id == 7:
        # self.part_request_date = datetime.today()
        if self.state == 'draft':
            self.draft_out = datetime.today()
            if self.draft_in and self.draft_out:
                start = datetime.strftime(self.draft_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.draft_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                self.draft_days = (end_last - start_last)
                open_date = (end_last - start_last)
            # open_date = datetime.strftime(open_date, '%Y-%m-%d %H:%M:%S')
            # open_date = datetime.strptime(open_date, '%Y-%m-%d %H:%M:%S')
            date_to = self.draft_out
        self.part_request_in = datetime.today()
        self.state = 'part_request'
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or 0})]
                     })

    # @api.multi
    # def action_to_request_accept(self):
    #     self.state = 'request_accept'

    @api.multi
    def action_to_part_dispatched(self):
        self.part_dispatched_in = datetime.today()
        self.state = 'part_dispatched'

    @api.multi
    def action_to_part_reached(self):
        from_state = self.state
        from_date = False
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'part_dispatched':
            from_date = self.part_dispatched_in
            self.part_dispatched_out = datetime.today()
            if self.part_dispatched_in and self.part_dispatched_out:
                start = datetime.strftime(self.part_dispatched_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_dispatched_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                self.part_dispatched_days = (end_last - start_last)
                open_date = (end_last - start_last)
            date_to = self.part_dispatched_out
        self.part_reached_in = datetime.today()
        self.state = 'part_reached'
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    @api.multi
    def action_to_request_for_part_pickup(self):
        pspr_details = self.env['stock.picking']
        # if self.env.user.company_id.id == 1:
        #     vals = {
        #         'partner_id': self.customer_id.id,
        #         'location_dest_id': 11,
        #         'picking_type_id': 5,
        #         'picking_type_code': 'internal',
        #         'location_id': 11,
        #         'pspr_stock_id': self.id,
        #         'screen_type':'reverse',
        #         'move_ids_without_package': [(0, 0,{'product_id': product.product.id, 'product_uom_qty': product.part_rq_qty, 'name': "test", 'product_uom': 1, 'location_id': 11, 'location_dest_id': 11})for product in self.part_details_ids]
        #     }
        # if self.env.user.company_id.id == 2:
        #     vals = {
        #         'partner_id': self.customer_id.id,
        #         'location_id': 21,
        #         'location_dest_id': 21,
        #         'picking_type_id': 13,
        #         'picking_type_code': 'internal',
        #         'pspr_stock_id': self.id,
        #         'screen_type':'reverse',
        #         'move_ids_without_package': [(0, 0,{'product_id': product.product.id, 'product_uom_qty': product.part_rq_qty, 'name': "test", 'product_uom': 1, 'location_id': 21, 'location_dest_id': 21})for product in self.part_details_ids]
        #     }
        # if self.env.user.company_id.id == 7:
        if not self.part_pickup_source_location_id or not self.part_pickup_dest_location_id or not self.stock_picking_type_id:
            raise ValidationError("This form should have Part Pickup Source Location And Part Pickup Destination Location And picking Type")
        vals = {
            'partner_id': self.customer_id.id,
            'location_id': self.part_pickup_source_location_id.id,
            'location_dest_id': self.part_pickup_dest_location_id.id ,
            'picking_type_id': self.stock_picking_type_id.id,
            'picking_type_code': 'internal',
            'pspr_stock_id': self.id,
            'screen_type': 'forward',
            'move_ids_without_package': [(0, 0,
                                          {'product_id': product.product.id, 'product_uom_qty': product.part_rq_qty,
                                           'name': "test", 'product_uom': product.uom_id.id,
                                           'location_id': self.part_pickup_source_location_id.id or False,
                                           'location_dest_id': self.part_pickup_dest_location_id.id or False, }) for
                                         product in self.part_details_ids]
        }
        new_val = pspr_details.create(vals)
        from_state = self.state
        from_date = False
        open_date = 0
        if self.state == 'repaired':
            self.repaired_out = datetime.today()
            if self.repaired_in and self.repaired_out:
                from_date = self.repaired_in
                start = datetime.strftime(self.repaired_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repaired_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repaired_days = (end_last - start_last)
            date_to = self.repaired_out
        if self.state == 'part_reached':
            self.part_reached_out = datetime.today()
            from_date = self.part_reached_in
            if self.part_reached_in and self.part_reached_out:
                start = datetime.strftime(self.part_reached_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_reached_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_reached_days = (end_last - start_last)
            date_to = self.part_reached_out
            # self.part_reached_days = (self.part_reached_out - self.part_reached_in)
        if self.state == 'part_dispatched':
            self.part_dispatched_out = datetime.today()
            if self.part_dispatched_in and self.part_dispatched_out:
                from_date = self.part_dispatched_in
                start = datetime.strftime(self.part_dispatched_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_dispatched_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_dispatched_days = (end_last - start_last)
            date_to = self.part_dispatched_out
        if self.state == 'request_accept':
            self.request_accept_out = datetime.today()
            if self.request_accept_in and self.request_accept_out:
                from_date = self.request_accept_in
                start = datetime.strftime(self.request_accept_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_accept_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_accept_days = (end_last - start_last)
            date_to = self.request_accept_out
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
        if self.state == 'purchase_request':
            self.purchase_request_out = datetime.today()
            if self.purchase_request_in and self.purchase_request_out:
                from_date = self.purchase_request_in
                start = datetime.strftime(self.purchase_request_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.purchase_request_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.purchase_request_days = (end_last - start_last)
            date_to = self.purchase_request_out
            # self.purchase_request_days = (self.purchase_request_out - self.purchase_request_in)
        self.request_for_part_pickup_in = datetime.today()
        self.state = 'request_for_part_pickup'
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })
        self.is_part_pickup = True

        return new_val

    @api.multi
    def action_to_in_transit(self):
        from_state = self.state
        from_date = False
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'request_for_part_pickup':
            self.request_for_part_pickup_out = datetime.today()
            if self.request_for_part_pickup_in and self.request_for_part_pickup_out:
                from_date = self.request_for_part_pickup_in
                start = datetime.strftime(self.request_for_part_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_for_part_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_for_part_pickup_days = (end_last - start_last)
            date_to = self.request_for_part_pickup_out
        if self.state == 'repaired':
            self.repaired_out = datetime.today()
            if self.repaired_in and self.repaired_out:
                from_date = self.repaired_in
                start = datetime.strftime(self.repaired_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repaired_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repaired_days = (end_last - start_last)
            date_to = self.repaired_out

        if self.state == 'ready_for_pickup':
            self.ready_for_pickup_out = datetime.today()
            if self.ready_for_pickup_in and self.ready_for_pickup_out:
                from_date = self.ready_for_pickup_out
                start = datetime.strftime(self.ready_for_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.ready_for_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.ready_for_pickup_days = (end_last - start_last)
            date_to = self.ready_for_pickup_out

        self.in_transit_in = datetime.today()
        self.state = 'in_transit'
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    @api.multi
    def action_to_closed(self):
        from_state = self.state
        from_date = False
        self.closed_date = datetime.today()
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'in_transit':
            self.in_transit_out = datetime.today()
            if self.in_transit_in and self.in_transit_out:
                from_date = self.in_transit_in
                start = datetime.strftime(self.in_transit_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.in_transit_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.in_transit_days = (end_last - start_last)
            date_to = self.in_transit_out
        if self.state == 'return_received':
            self.return_received_out = datetime.today()
            if self.return_received_in and self.return_received_out:
                from_date = self.return_received_out
                start = datetime.strftime(self.return_received_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.return_received_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.return_receive_days = (end_last - start_last)
            date_to = self.return_received_out
            # self.in_transit_days = (self.in_transit_out - self.in_transit_in)
        self.closed_in = datetime.today()
        self.state = 'closed'

    # self.update({'detail_ids':[(0,0,{
    #     'from_stage': from_state,
    #     'to_stage': self.state,
    #     # 'in_date': from_date or False,
    #     # 'out_date': date_to,
    #     # 'open_days': open_date or False
    #     })]
    # })

    # @api.multi
    # def action_to_hold(self):
    #     self.state = 'hold'

    @api.multi
    def action_to_cancel(self):
        from_state = self.state
        from_date = False
        self.cancel_date = datetime.today()
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'repaired':
            self.repaired_out = datetime.today()
            from_date = self.repaired_in
            if self.repaired_in and self.repaired_out:
                start = datetime.strftime(self.repaired_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repaired_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repaired_days = (end_last - start_last)
                # self.repaired_days = (self.repaired_out - self.repaired_in)
            date_to = self.repaired_out
        if self.state == 'repair_started':
            self.repair_started_out = datetime.today()
            from_date = self.repair_started_in
            if self.repair_started_in and self.repair_started_out:
                start = datetime.strftime(self.repair_started_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repair_started_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repair_started_days = (end_last - start_last)
                # self.repair_started_days = (self.repair_started_out - self.repair_started_in)
            date_to = self.repair_started_out
        if self.state == 'request_accept':
            self.request_accept_out = datetime.today()
            from_date = self.request_accept_in
            if self.request_accept_in and self.request_accept_out:
                start = datetime.strftime(self.request_accept_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_accept_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_accept_days = (end_last - start_last)
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
            date_to = self.request_accept_out
        if self.state == 'part_request':
            self.part_request_out = datetime.today()
            from_date = self.part_request_in
            if self.part_request_in and self.part_request_out:
                start = datetime.strftime(self.part_request_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_request_days = (end_last - start_last)
            # self.part_request_days = (self.part_request_out - self.part_request_in)
            date_to = self.part_request_out
        if self.state == 'ready_for_pickup':
            self.ready_for_pickup_out = datetime.today()
            if self.ready_for_pickup_in and self.ready_for_pickup_out:
                from_date = self.ready_for_pickup_out
                start = datetime.strftime(self.ready_for_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.ready_for_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.ready_for_pickup_days = (end_last - start_last)
            date_to = self.ready_for_pickup_out
        if self.state == 'return_received':
            self.return_received_out = datetime.today()
            if self.return_received_in and self.return_received_out:
                from_date = self.return_received_out
                start = datetime.strftime(self.return_received_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.return_received_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.return_receive_days = (end_last - start_last)
            date_to = self.return_received_out
        if self.state == 'in_transit':
            self.in_transit_out = datetime.today()
            if self.in_transit_in and self.in_transit_out:
                from_date = self.in_transit_out
                start = datetime.strftime(self.in_transit_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.in_transit_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.in_transit_days = (end_last - start_last)
            date_to = self.in_transit_out
        self.cancel_in = datetime.today()
        self.state = 'cancel'
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    @api.multi
    def action_set_draft(self):
        from_state = self.state
        from_date = False
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'in_transit':
            self.in_transit_out = datetime.today()
            if self.in_transit_in and self.in_transit_out:
                from_date = self.in_transit_in
                start = datetime.strftime(self.in_transit_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.in_transit_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.in_transit_days = (end_last - start_last)
            date_to = self.in_transit_out
            # self.in_transit_days = (self.in_transit_out - self.in_transit_in)
        if self.state == 'request_for_part_pickup':
            self.request_for_part_pickup_out = datetime.today()
            if self.request_for_part_pickup_in and self.request_for_part_pickup_out:
                from_date = self.request_for_part_pickup_in
                start = datetime.strftime(self.request_for_part_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_for_part_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_for_part_pickup_days = (end_last - start_last)
            date_to = self.request_for_part_pickup_out
            # self.request_for_part_pickup_days = (self.request_for_part_pickup_out - self.request_for_part_pickup_in)
        if self.state == 'repaired':
            self.repaired_out = datetime.today()
            if self.repaired_in and self.repaired_out:
                from_date = self.repaired_in
                start = datetime.strftime(self.repaired_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repaired_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repaired_days = (end_last - start_last)
            date_to = self.repaired_out
            # self.repaired_days = (self.repaired_out - self.repaired_in)
        if self.state == 'repair_started':
            self.repair_started_out = datetime.today()
            from_date = self.repair_started_in
            if self.repair_started_in and self.repair_started_out:
                start = datetime.strftime(self.repair_started_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repair_started_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repair_started_days = (end_last - start_last)
            date_to = self.repair_started_out
            # self.repair_started_days = (self.repair_started_out - self.repair_started_in)
        if self.state == 'part_reached':
            self.part_reached_out = datetime.today()
            if self.part_reached_in and self.part_reached_out:
                from_date = self.part_reached_in
                start = datetime.strftime(self.part_reached_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_reached_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_reached_days = (end_last - start_last)
            date_to = self.part_reached_out
            # self.part_reached_days = (self.part_reached_out - self.part_reached_in)
        if self.state == 'part_dispatched':
            self.part_dispatched_out = datetime.today()
            if self.part_dispatched_in and self.part_dispatched_out:
                from_date = self.part_dispatched_in
                start = datetime.strftime(self.part_dispatched_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_dispatched_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_dispatched_days = (end_last - start_last)
            date_to = self.part_dispatched_out
            # self.part_dispatched_days = (self.part_dispatched_out - self.part_dispatched_in)
        if self.state == 'purchase_request':
            self.purchase_request_out = datetime.today()
            if self.purchase_request_in and self.purchase_request_out:
                from_date = self.purchase_request_in
                start = datetime.strftime(self.purchase_request_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.purchase_request_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.purchase_request_days = (end_last - start_last)
            date_to = self.purchase_request_out
            # self.purchase_request_days = (self.purchase_request_out - self.purchase_request_in)
        if self.state == 'request_accept':
            self.request_accept_out = datetime.today()
            if self.request_accept_in and self.request_accept_out:
                from_date = self.request_accept_in
                start = datetime.strftime(self.request_accept_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_accept_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_accept_days = (end_last - start_last)
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
            date_to = self.request_accept_out
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
        if self.state == 'part_request':
            self.part_request_out = datetime.today()
            if self.part_request_in and self.part_request_out:
                from_date = self.part_request_in
                start = datetime.strftime(self.part_request_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.part_request_days = (end_last - start_last)
            # self.part_request_days = (self.part_request_out - self.part_request_in)
            date_to = self.part_request_out
            # self.part_request_days = (self.part_request_out - self.part_request_in)
        if self.state == 'cancel':
            self.cancel_out = datetime.today()
            if self.cancel_in and self.cancel_out:
                from_date = self.cancel_in
                start = datetime.strftime(self.cancel_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.cancel_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.cancel_days = (end_last - start_last)
            date_to = self.cancel_out
        if self.state == 'ready_for_pickup':
            self.ready_for_pickup_out = datetime.today()
            if self.ready_for_pickup_in and self.ready_for_pickup_out:
                from_date = self.ready_for_pickup_out
                start = datetime.strftime(self.ready_for_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.ready_for_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.ready_for_pickup_days = (end_last - start_last)
            date_to = self.ready_for_pickup_out
            # self.cancel_days = (self.cancel_out - self.cancel_in)
        self.draft_in = datetime.today()
        self.write({'state': 'draft'})
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    # @api.multi
    # def action_to_purchase_request(self):
    #     # =======================Start=========================22-02-2023
    #     pur_tender = self.env['purchase.agreement']
    #     if self.env.user.company_id.id == 7:
    #         if self.part_details_ids:
    #             for line in self.part_details_ids:
    #                 if line.product:
    #                     vals = {
    #                         'purchase_tender_id': self.id,
    #                         'sh_source': self.name,
    #                         'sh_agreement_type': 1,
    #                         'sh_purchase_user_id': 24706,
    #                         'company_id': 2,
    #                         'sh_purchase_agreement_line_ids': [
    #                             (0, 0, {'sh_product_id': line.product.id, 'sh_qty': line.part_rq_qty})]
    #                     }
    #                     tender_val = pur_tender.create(vals)
    #         # ================================End================22-02-2023
    #
    #         from_state = self.state
    #         from_date = False
    #         open_date = 0
    #         if self.state == 'request_accept':
    #             self.request_accept_out = datetime.today()
    #             if self.request_accept_in and self.request_accept_out:
    #                 from_date = self.request_accept_in
    #                 start = datetime.strftime(self.request_accept_in, '%Y-%m-%d %H:%M:%S')
    #                 end = datetime.strftime(self.request_accept_out, '%Y-%m-%d %H:%M:%S')
    #                 start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    #                 end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    #                 open_date = (end_last - start_last)
    #                 self.request_accept_days = (end_last - start_last)
    #             # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
    #             date_to = self.request_accept_out
    #             # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
    #         self.purchase_request_in = datetime.today()
    #         self.write({'state': 'purchase_request'})
    #         self.update({'detail_ids': [(0, 0, {
    #             'from_stage': from_state,
    #             'to_stage': self.state,
    #             'in_date': from_date or False,
    #             'out_date': date_to,
    #             'open_days': open_date or False})]
    #                      })
    #         return tender_val

    # @api.multi
    # def action_to_received_material(self):
    #     self.write({'state': 'received_material'})

    @api.multi
    def action_to_partsend(self):
        from_state = self.state
        from_date = False
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'request_for_part_pickup':
            self.request_for_part_pickup_out = datetime.today()
            if self.request_for_part_pickup_in and self.request_for_part_pickup_out:
                from_date = self.request_for_part_pickup_in
                start = datetime.strftime(self.request_for_part_pickup_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_for_part_pickup_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_for_part_pickup_days = (end_last - start_last)
            date_to = self.request_for_part_pickup_out
            # self.request_for_part_pickup_days = (self.request_for_part_pickup_out - self.request_for_part_pickup_in)
        if self.state == 'request_accept':
            self.request_accept_out = datetime.today()
            if self.request_accept_in and self.request_accept_out:
                from_date = self.request_accept_in
                start = datetime.strftime(self.request_accept_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.request_accept_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.request_accept_days = (end_last - start_last)
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
            date_to = self.request_accept_out
            # self.request_accept_days = (self.request_accept_out - self.request_accept_in)
        if self.state == 'purchase_request':
            self.purchase_request_out = datetime.today()
            if self.purchase_request_out and self.purchase_request_in:
                from_date = self.purchase_request_in
                start = datetime.strftime(self.purchase_request_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.purchase_request_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.purchase_request_days = (end_last - start_last)
            date_to = self.purchase_request_out
            # self.purchase_request_days = (self.purchase_request_out - self.purchase_request_in)
        self.part_dispatched_in = datetime.today()
        self.write({'state': 'part_dispatched'})
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    @api.multi
    def action_to_repaired(self):
        from_state = self.state
        from_date = False
        open_date = 0
        # if self.env.user.company_id.id == 7:
        if self.state == 'repair_started':
            self.repair_started_out = datetime.today()
            if self.repair_started_in and self.repair_started_out:
                from_date = self.repair_started_in
                start = datetime.strftime(self.repair_started_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(self.repair_started_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                self.repair_started_days = (end_last - start_last)
            date_to = self.repair_started_out
            # self.repair_started_days = (self.repair_started_out - self.repair_started_in)
        self.repaired_in = datetime.today()
        self.write({'state': 'repaired'})
        self.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': self.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })

    def open_inward_screen(self):
        self.ensure_one()
        val = dict(
            default_pspr_stock_id=self.id,
        )
        return {
            'name': 'Internal screen',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('pspr_stock_id', '=', self.id)],
            'context': val,
        }

    def open_repair_screen(self):
        self.ensure_one()
        val = dict(
            default_pspr_repair_id=self.id,
        )
        return {
            'name': 'Repair Screen',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'domain': [('invoice_method', 'ilike', 'none'), ('pspr_repair_id', '=', self.id)],
            'context': val,
        }

    # Purchase Request 20-Feb-2023================ Dayan=================
    def open_purchase_tender(self):
        val = dict(
            default_purchase_tender_id=self.id,
            default_sh_source=self.name,
            default_sh_agreement_type=1,
            default_sh_purchase_user_id=3729,
        )
        return {
            'name': 'Purchase Tender',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.agreement',
            'domain': [('sh_source', '=', self.name)],
            'context': val,
        }

    @api.multi
    def action_to_request_accept(self, vals):
        pspr_details = self.env['stock.picking']

        if self.part_details_ids:
            for product in self.part_details_ids:
                if product.product:
                    # if self.env.user.company_id.id == 1:
                    #     vals = {
                    #         'partner_id': self.customer_id.id,
                    #         'location_id': 11,
                    #         'location_dest_id': 11,
                    #         'picking_type_id': 5,
                    #         'picking_type_code': 'internal',
                    #         'pspr_stock_id': self.id,
                    #         'screen_type':'forward',
                    #         'move_ids_without_package':[(0,0, {'product_id':product.product.id,'product_uom_qty':product.part_rq_qty,'name':"test",'product_uom':1,'location_id':11,'location_dest_id':11})]
                    #     }
                    # if self.env.user.company_id.id == 2:
                    #     vals = {
                    #         'partner_id': self.customer_id.id,
                    #         'location_id': 21,
                    #         'location_dest_id': 21,
                    #         'picking_type_id': 13,
                    #         'picking_type_code': 'internal',
                    #         'pspr_stock_id': self.id,
                    #         'screen_type':'forward',
                    #         'move_ids_without_package':[(0,0, {'product_id':product.product.id,'product_uom_qty':product.part_rq_qty,'name':"test",'product_uom':1,'location_id':21,'location_dest_id':21})]
                    #     }
                    # if self.env.user.company_id.id == 7:
                    if not self.location_id or not self.dest_location_id or not self.stock_picking_type_id:
                        raise ValidationError("This form should have Source Location And Destination Location And picking Type")
                    vals = {
                        'partner_id': self.customer_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.dest_location_id.id,
                        'company_id': self.company_id.id,
                        'picking_type_id': self.stock_picking_type_id.id,
                        'picking_type_code': 'internal',
                        'pspr_stock_id': self.id,
                        'screen_type': 'forward',
                        'move_ids_without_package': [(0, 0, {'product_id': product.product.id,
                                                             'product_uom_qty': product.part_rq_qty, 'name': "test",
                                                             'product_uom': product.uom_id.id,
                                                             'location_id': self.location_id.id,
                                                             'location_dest_id': self.dest_location_id.id})]
                    }

                    new_val = pspr_details.create(vals)
                    from_state = self.state
                    from_date = False
                    open_date = 0
                    if self.state == 'part_request':
                        self.part_request_out = datetime.today()
                        from_date = self.part_request_in
                        if self.part_request_in and self.part_request_out:
                            start = datetime.strftime(self.part_request_in, '%Y-%m-%d %H:%M:%S')
                            end = datetime.strftime(self.part_request_out, '%Y-%m-%d %H:%M:%S')
                            start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                            end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                            open_date = (end_last - start_last)
                            self.part_request_days = (end_last - start_last)
                            # self.part_request_days = (self.part_request_out - self.part_request_in)
                        date_to = self.part_request_out
                        # self.part_request_days = (self.part_request_out - self.part_request_in)
                    self.request_accept_in = datetime.today()
                    self.state = 'request_accept'
                    self.update({'detail_ids': [(0, 0, {
                        'from_stage': from_state,
                        'to_stage': self.state,
                        'in_date': from_date or False,
                        'out_date': date_to,
                        'open_days': open_date or False})]
                                 })
                    self.is_accept = True
                    return new_val
                else:
                    raise ValidationError("This form should have product for this move")
        else:
            raise ValidationError("There is no part details.....!")

    @api.multi
    def action_to_repair_request(self, vals):
        if self.helpdesk_product:
            pspr_repair_details = self.env['repair.order']
            if not self.repair_location_id:
                raise ValidationError("Please Add Repair Location!")
            vals = {
                'product_id': self.helpdesk_product.id or False,
                'product_qty': 1,
                # 'product_uom': 1,
                'product_uom': self.helpdesk_product.uom_id.id or False,
                'lot_id': self.helpdesk_lot_id.id,
                'location_id': self.repair_location_id.id,
                'invoice_method': 'none',
                'pspr_repair_id': self.id,
            }
            updated_val = pspr_repair_details.create(vals)
            from_state = self.state
            from_date = False
            open_date = 0
            if self.state == 'part_reached':
                self.part_reached_out = datetime.today()
                if self.part_reached_in and self.part_reached_out:
                    from_date = self.part_reached_in
                    start = datetime.strftime(self.part_reached_in, '%Y-%m-%d %H:%M:%S')
                    end = datetime.strftime(self.part_reached_out, '%Y-%m-%d %H:%M:%S')
                    start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                    end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                    open_date = (end_last - start_last)
                    self.part_reached_days = (end_last - start_last)
                date_to = self.part_reached_out
            # if self.state == 'return_recieved':
            #     self.return_recieved_out = datetime.today()
            #     if self.return_recieved_in and self.return_recieved_out:
            #         from_date=self.return_recieved_in
            #         start = datetime.strftime(self.return_recieved_in, '%Y-%m-%d %H:%M:%S')
            #         end = datetime.strftime(self.return_recieved_out, '%Y-%m-%d %H:%M:%S')
            #         start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            #         end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            #         open_date = (end_last - start_last)
            #         self.part_reached_days = (end_last - start_last)
            #     date_to=self.return_recieved_out
            # self.part_reached_days = (self.part_reached_out - self.part_reached_in)
            self.repair_started_in = datetime.today()
            self.state = 'repair_started'
            self.update({'detail_ids': [(0, 0, {
                'from_stage': from_state,
                'to_stage': self.state,
                # 'in_date': from_date or False,
                # 'out_date': date_to,
                'open_days': open_date or False})]
                         })
            self.is_repair = True
        else:
            raise ValidationError("Product is required for this move ")

    @api.multi
    def action_to_ready_for_pickup(self):
        # if self.env.user.company_id.id == 7:
        for rec in self:
            rec.ready_for_pickup_in = datetime.today()
            rec.state = 'ready_for_pickup'

    @api.multi
    def action_to_return_received(self):
        # if self.env.user.company_id.id == 7:
        for rec in self:
            rec.return_received_in = datetime.today()
            rec.state = 'return_received'

    @api.multi
    def action_to_sent_to_rma_tech(self):
        pspr_dts = self.env['stock.picking']
        if self.part_details_ids:
            for product in self.part_details_ids:
                if product.product:
                    # if self.env.user.company_id.id == 1:
                    #     vals = {
                    #         'partner_id': self.customer_id.id,
                    #         'location_id': 11,
                    #         'location_dest_id': 11,
                    #         'picking_type_id': 5,
                    #         'picking_type_code': 'internal',
                    #         'pspr_stock_id': self.id,
                    #         'screen_type':'internal',
                    #         'move_ids_without_package':[(0,0, {'product_id':product.product.id,'product_uom_qty':product.part_rq_qty,'name':"test",'product_uom':1,'location_id':11,'location_dest_id':11})]
                    #     }
                    # if self.env.user.company_id.id == 2:
                    #     vals = {
                    #         'partner_id': self.customer_id.id,
                    #         'location_id': 21,
                    #         'location_dest_id': 21,
                    #         'picking_type_id': 13,
                    #         'picking_type_code': 'internal',
                    #         'pspr_stock_id': self.id,
                    #         'screen_type':'internal',
                    #         'move_ids_without_package':[(0,0, {'product_id':product.product.id,'product_uom_qty':product.part_rq_qty,'name':"test",'product_uom':1,'location_id':21,'location_dest_id':21})]
                    #     }
                    # if self.env.user.company_id.id == 7:
                    if not self.rma_source_location_id or not self.rma_dest_location_id or not self.stock_picking_type_id:
                        raise ValidationError(
                            "This form should have RMA Source Location And RMA Destination Location And picking Type")
                    vals = {
                        'partner_id': self.customer_id.id,
                        'location_id': self.rma_source_location_id.id,
                        'location_dest_id': self.rma_dest_location_id.id,
                        'picking_type_id': self.stock_picking_type_id.id,
                        'picking_type_code': 'internal',
                        'pspr_stock_id': self.id,
                        'screen_type': 'internal',
                        'move_ids_without_package': [(0, 0, {'product_id': product.product.id,
                                                             'product_uom_qty': product.part_rq_qty, 'name': "test",
                                                             'product_uom': self.helpdesk_product.uom_id.id or False,
                                                             'location_id': self.rma_source_location_id.id or False,
                                                             'location_dest_id': self.rma_dest_location_id.id or False, })]
                    }

                    new_val = pspr_dts.create(vals)
                    self.write({'state': 'sent_to_rma_tech'})
                    self.is_rma_tech = True
                    return new_val
                else:
                    raise ValidationError("This form should have product for this move")
        else:
            raise ValidationError("There is no part details.....!")

        # return updated_val


# ===========================30.Oct.2022==================End========================================Dayan======================================

class PartDetails(models.Model):
    _name = "part.details"
    _description = "Part Details"

    pspr_reference_id = fields.Many2one('product.details', 'PR Reference')
    part_name = fields.Many2one('pspr_part.name', string="Part Name")
    part_desc = fields.Text(string="Part Description")
    part_rq_qty = fields.Integer(string="Request QTY")
    part_sent_qty = fields.Integer(string="Sent QTY")
    part_rv_qty = fields.Integer(string="Received QTY")
    product = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.onchange('product')
    def on_change_product(self):
        for rec in self:
            rec.uom_id = rec.product.uom_id


class PSPRPartDetails(models.Model):
    _name = "pspr_part.name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PSPR Part Details"

    name = fields.Char(string="Name", track_visibility='always')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pspr_stock_id = fields.Many2one('product.details', string="PSPR")
    screen_type = fields.Selection([
        ('forward', 'Forward'),
        ('reverse', 'Reverse'),
        ('internal', 'Internal')

    ], string='Screen Type', track_visibility='always')
    material_value = fields.Float('Material Value', track_visibility='always')


class RepairCountValues(models.Model):
    _inherit = "repair.order"

    pspr_repair_id = fields.Many2one('product.details', string="PSPR Repair")

    #  ==Dayan================Repair Order Source Document ===========Dayan========04.11.2022========================================================
    source_document = fields.Char(string="Source Document", related='pspr_repair_id.name')


class ShPurchaseAgreement(models.Model):
    _inherit = "purchase.agreement"

    purchase_tender_id = fields.Many2one('product.details', 'Purchase Tender')


class PSPRTags(models.Model):
    _name = "pspr.tags"

    _description = "PSPR Tags"

    name = fields.Char('Name')


class PSPRCategory(models.Model):
    _name = "pspr.category"

    _description = "PSPR Category"

    name = fields.Char(string="Name")


class PSPRSubCategory(models.Model):
    _name = "pspr.sub.category"

    _description = "PSPR Sub Category"

    name = fields.Char(string="Name")


class PSPRHelpdesk(models.Model):
    _inherit = "helpdesk.ticket"

    pspr_id = fields.Many2one('product.details', 'PSPR ID', compute="compute_pspr_id")
    pspr_state = fields.Selection('PSPR Status', related='pspr_id.state')

    @api.depends('pspr_id.state')
    @api.multi
    def compute_pspr_id(self):
        for rec in self:
            psr_id = rec.env['product.details'].search([('helpdesk_ticket_id', '=', rec.id)])
            for psid in psr_id:
                rec.pspr_id = psid
                # rec.pspr_state = psid.state  


class PSPRPartVlaue(models.Model):
    _name = "pspr.part.value"

    _description = "PSPR Part Value"

    name = fields.Char(string="Name")


class PSPRNoDamage(models.Model):
    _name = "pspr.no.damage"

    _description = "PSPR NoDamage"

    name = fields.Char(string="Name")


class PSPRDamageCategory(models.Model):
    _name = "pspr.damage.category"

    _description = "PSPR Damage Category"

    name = fields.Char(string="Name")
