# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta, date

class Helpdesk(models.Model):
	_inherit = 'helpdesk.ticket'

	is_start = fields.Boolean('Start')
	is_stop = fields.Boolean('Stop')
	is_play = fields.Boolean('Play')
	is_pause = fields.Boolean('Pause')
	run_timer = fields.Boolean("Run Timer")
	ticket_timer = fields.Float('Timer')
	stop_timer = fields.Float('Stop Timer', store=True)
	duration_ids = fields.One2many('ticket.timer','helpdesk_ticket_id',string="Duration")
	
	def play_ticket_button(self):
		tickets_obj = self.env['helpdesk.ticket'].search([('is_start','=',True),('user_id','=', self.user_id.id)])
		if tickets_obj:
			return {
				'name': 'Start Ticket Timer',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'start.ticket.timer',
				'target': 'new',
			}
		else:
			self.is_start = True
			self.is_pause = False
			self.is_play = True
			self.run_timer = True
			self.is_stop = True
			self.env['ticket.timer'].create({
									'play_time': datetime.now(),
									'helpdesk_ticket_id': self.id,
									'user_id' : self.env.user.id})
	
	def pause_ticket_button(self):
		self.is_start =False
		self.is_pause = True
		self.run_timer = False
		self.is_play = True
		self.is_stop = True
		self.update_current_time()

	def unpause_ticket_button(self):
		tickets_obj = self.env['helpdesk.ticket'].search([('is_start','=',True)])
		if tickets_obj:
			return {
				'name': 'Start Ticket Timer',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'start.ticket.timer',
				'target': 'new',
			}
		else:
			self.is_start = True
			self.is_pause = False
			self.run_timer = True
			self.is_stop = True
			self.env['ticket.timer'].create({
										'play_time': datetime.now(),
										'helpdesk_ticket_id': self.id,
										'user_id': self.env.user.id})
			
	def stop_ticket_timer(self):
		self.update_current_time()
		self.stop_timer = sum(self.duration_ids.mapped('duration'))
		return {
			'name': 'Stop Ticket Timer',
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'stop.ticket.timer',
			'target': 'new',
		}


	@api.multi
	def update_current_time(self, doall=False):
		ticket_timer = self.env['ticket.timer']
		domain = [('helpdesk_ticket_id', 'in', self.ids), ('pause_time', '=', False)]
		if not doall:
			domain.append(('user_id', '=', self.env.user.id))

		not_calculate_timelines = ticket_timer.browse()
		for time_dis in ticket_timer.search(domain, limit=None if doall else 1):
			not_calculate_timelines += time_dis
			time_dis.write({'pause_time': fields.Datetime.now()})
		return True
class TicketTimer(models.Model):
	_name = "ticket.timer"
	_description = 'Ticket Timer'

	helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
	play_time = fields.Datetime('Play Time', default=fields.Datetime.now , required=True)
	pause_time = fields.Datetime('Pause Time')
	duration = fields.Float('Duration', compute='_compute_time_gap', store=True)
	user_id = fields.Many2one('res.users', "User",default=lambda self: self.env.uid)


	@api.depends('play_time', 'pause_time')
	def _compute_time_gap(self):
		for running in self:
			if running.pause_time:
				d1 = fields.Datetime.from_string(running.play_time)
				d2 = fields.Datetime.from_string(running.pause_time)
				diff = d2 - d1
				minutes = round(diff.total_seconds() / 60.0, 2) + 0.01
				running.duration = round(minutes/60 ,2)
			else:
				running.duration = 0.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: