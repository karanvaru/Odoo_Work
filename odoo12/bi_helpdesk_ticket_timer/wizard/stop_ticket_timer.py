# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta, date
from odoo.exceptions import Warning ,ValidationError
class StopTicketTimer(models.TransientModel):
	_name = "stop.ticket.timer"
	_description = 'Stop Ticket Timer'

	name = fields.Char(string="Description",required=True)

	def stop_timer(self):
		value = []
		helpdesk_ticket_obj = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
		helpdesk_ticket_obj.write({'run_timer':False, 'is_play':False,'is_start':False, 'ticket_timer': False, 'is_stop':False})
		account_id = False
		if helpdesk_ticket_obj.partner_id:
			account_id = self.env['account.analytic.account'].search([('partner_id','=',helpdesk_ticket_obj.partner_id.id)], limit= 1)
		if not account_id:
			account_id = 128
			# raise ValidationError(_("Please configure analytic account!"))
		ticket_timer_ids = self.env['ticket.timer'].search([('helpdesk_ticket_id','=',helpdesk_ticket_obj.id)])
		helpdesk_ticket_obj.timesheet_ids.create({
				'date' : fields.date.today(),
				'name' : self.name,
				'task_id' : helpdesk_ticket_obj.task_id.id,
				'project_id' : helpdesk_ticket_obj.task_id.project_id.id,
				'unit_amount': helpdesk_ticket_obj.stop_timer,  
				'account_id' :account_id,
			    # 'account_id': 128,
				'helpdesk_ticket_id' : helpdesk_ticket_obj.id
				})
		ticket_timer_ids.unlink()
		
class StartTicketTimer(models.TransientModel):
	_name = "start.ticket.timer"
	_description = 'Start Ticket Timer'

	def pause_timer(self):
		tickets_obj = self.env['helpdesk.ticket'].search([('is_pause','=',False)])
		helpdesk_ticket_obj = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
		
		for tickets in tickets_obj:
			tickets.write({'run_timer':False, 'is_pause':True,'is_stop':True})
			tickets.pause_ticket_button()

		helpdesk_ticket_obj.write({'is_start':True,'is_pause':False,'is_play':True,'run_timer':True,'is_stop':True})
		self.env['ticket.timer'].create({
									'play_time': datetime.now(),
									'helpdesk_ticket_id': helpdesk_ticket_obj.id,
									'user_id' : self.env.user.id})
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
