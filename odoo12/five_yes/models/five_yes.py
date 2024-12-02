# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class FiveYes(models.Model):
    _name = "five.yes"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Five Yes'

    name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')

    location = fields.Selection([
        ('atp_c1', 'ATP-C1'),
        ('atp_c2', 'ATP-C2'),
        ('atp_c3', 'ATP-C3'),
        ('atp_2f', 'ATP-2F'),
    ], string='Location')
    room_number = fields.Many2one('room.numbers', string='Room Number', track_visibility='onchange')
    rack_number_from = fields.Many2one('racknumbers.from', string='Rack Numbers From', track_visibility='onchange')
    rack_number_to = fields.Many2one('racknumbers.to', string='Rack Numbers to', track_visibility='onchange')
    shelf_no_from = fields.Many2one('shelfno.from', string='Shelf Numbers From', track_visibility='onchange')
    shelf_no_to = fields.Many2one('shelfno.to', string='Shelf Numbers To', track_visibility='onchange')
    bin_no_from = fields.Many2one('binno.from', string='Bin Numbers From', track_visibility='onchange')
    bin_no_to = fields.Many2one('binno.to', string='Bin Numbers To', track_visibility='onchange')
    reserved_for = fields.Many2many('reserved.for', string='Reserved For', track_visibility='onchange')

    @api.model
    def create(self,vals):
        vals.update({
			'name': self.env['ir.sequence'].next_by_code('five.yes.sequence'),
		})
        return super(FiveYes, self).create(vals)


class RoomNumbers(models.Model):
    _name = 'room.numbers'
    name = fields.Char(required=True)

class RackNumbersFrom(models.Model):
    _name = 'racknumbers.from'
    name = fields.Char(required=True)

class RackNumbersTo(models.Model):
    _name = 'racknumbers.to'
    name = fields.Char(required=True)

class ShelfNumbersFrom(models.Model):
    _name = 'shelfno.from'
    name = fields.Char(required=True)

class ShelfNumbersTo(models.Model):
    _name = 'shelfno.to'
    name = fields.Char(required=True)
class BinNumbersFrom(models.Model):
    _name = 'binno.from'
    name = fields.Char(required=True)

class BinNumbersTo(models.Model):
    _name = 'binno.to'
    name = fields.Char(required=True)

class ReservedFor(models.Model):
    _name = 'reserved.for'
    name = fields.Char(required=True)


