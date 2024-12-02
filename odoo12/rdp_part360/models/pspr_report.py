from time import strptime
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError


class PsprStageHistory(models.Model):
    _name = 'pspr.stage.history'

    detail_id = fields.Many2one('product.details', string="Detail Id")
    from_stage = fields.Selection([ 
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
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),
    ], string='From Stage', readonly=True)
    to_stage = fields.Selection([ 
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
        ('closed', 'CLOSED'),
        ('cancel', 'CANCELLED'),
    ], string='To Stage', readonly=True)
    in_date = fields.Datetime(string="Start Date")
    out_date = fields.Datetime(string="End Date")
    open_days = fields.Char(string="Open Days")


class PsprReport(models.Model):
    _inherit = 'product.details'

    detail_ids = fields.One2many('pspr.stage.history', 'detail_id', string="Stage Details")

