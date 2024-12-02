# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MultiApproval(models.Model):
	_name = 'multi.approval'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Multi Aproval'

	code = fields.Char(default=_('New'))
	name = fields.Char(string='Title', required=True)
	user_id = fields.Many2one(
		string='Request by', comodel_name="res.users",
		required=True, default=lambda self: self.env.uid)
	priority = fields.Selection(
		[('0', 'Normal'),
		('1', 'Medium'),
		('2', 'High'),
		('3', 'Very High')], string='Priority', default='0')
	request_date = fields.Datetime(
		string='Request Date', default=fields.Datetime.now)
	complete_date = fields.Datetime()
	type_id = fields.Many2one(
		string="Type", comodel_name="multi.approval.type", required=True)
	image = fields.Binary(related="type_id.image")
	description = fields.Html('Description')
	state = fields.Selection(
		[('Draft', 'Draft'),
		 ('Submitted', 'Submitted'),
		 ('Approved', 'Approved'),
		 ('Refused', 'Refused'),
		 ('Cancel', 'Cancel')], default='Draft', tracking=True)

	document_opt = fields.Selection(
		string="Document opt",
		readonly=True, related='type_id.document_opt')
	attachment_ids = fields.Many2many('ir.attachment', string='Documents')

	contact_opt = fields.Selection(
		string="Contact opt",
		readonly=True, related='type_id.contact_opt')
	contact_id = fields.Many2one('res.partner', string='Contact')

	date_opt = fields.Selection(
		string="Date opt",
		readonly=True, related='type_id.date_opt')
	date = fields.Date('Date')

	period_opt = fields.Selection(
		string="Period opt",
		readonly=True, related='type_id.period_opt')
	date_start = fields.Date('Start Date')
	date_end = fields.Date('End Date')

	item_opt = fields.Selection(
		string="Item opt",
		related='type_id.item_opt')
	item_id = fields.Many2one('product.product', string='Item')

	multi_items_opt = fields.Selection(
		string="Multi Items opt",
		readonly=True, related='type_id.multi_items_opt')
	item_ids = fields.Many2many('product.product', string='Items')


	quantity_opt = fields.Selection(
		string="Quantity opt",
		readonly=True, related='type_id.quantity_opt')
	quantity = fields.Float('Quantity')

	amount_opt = fields.Selection(
		string="Amount opt",
		readonly=True, related='type_id.amount_opt')
	amount = fields.Float('Amount')

	payment_opt = fields.Selection(
		string="Payment opt",
		readonly=True, related='type_id.payment_opt')
	payment = fields.Float('Payment')

	reference_opt = fields.Selection(
		string="Reference opt",
		readonly=True, related='type_id.reference_opt')
	reference = fields.Char('Reference')

	location_opt = fields.Selection(
		string="Location opt",
		readonly=True, related='type_id.location_opt')
	location = fields.Char('Location')
	line_ids = fields.One2many('multi.approval.line', 'approval_id',
							   string="Lines")
	line_id = fields.Many2many('multi.approval.line', string="Line", copy=False)
	deadline = fields.Date(string='Deadline', related='line_id.deadline')
	pic_ids = fields.Many2many(
		'res.users', string='Approver')
	is_pic = fields.Boolean(compute='_check_pic')
	follower = fields.Text('Following Users', default='[]', copy=False)

	# copy the idea of hr_expense
	attachment_number = fields.Integer(
		'Number of Attachments', compute='_compute_attachment_number')

	@api.depends_context("uid")
	def _check_pic(self):
		for r in self:
			val = [c.id for c in r.pic_ids if self.env.uid == c.id]
			if val:
				r.is_pic = True
			else:
				r.is_pic = False

	def _compute_attachment_number(self):
		attachment_data = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'multi.approval'), ('res_id', 'in', self.ids)],
			['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count'])
						  for data in attachment_data)
		for r in self:
			r.attachment_number = attachment.get(r.id, 0)

	def action_cancel(self):
		recs = self.filtered(lambda x: x.state == 'Draft')
		recs.write({'state': 'Cancel'})

	def action_submit(self):
		recs = self.filtered(lambda x: x.state == 'Draft')
		for r in recs:
			# Check if document is required
			if r.document_opt == 'Required' and r.attachment_number < 1:
				raise UserError(_('Document is required !'))
			if not r.type_id.line_ids:
				raise UserError(_(
					'There is no approver of the type "{}" !'.format(
						r.type_id.name)))
			r.state = 'Submitted'
		recs._create_approval_lines()
		recs.send_request_mail()
		recs.send_activity_notification()

	@api.model
	def get_follow_key(self, user_id=None):
		if not user_id:
			user_id = self.env.uid
		k = '[res.users:{}]'.format(user_id)
		return k

	def update_follower(self, user_id):
		self.ensure_one()
		k = self.get_follow_key(user_id)
		follower = self.follower
		if k not in follower:
			self.follower = follower + k

	# 13.0.1.1
	def set_approved(self):
		self.ensure_one()
		self.state = 'Approved'
		self.complete_date = fields.Datetime.now()
		self.send_approved_mail()

	def set_refused(self, reason=''):
		self.ensure_one()
		self.state = 'Refused'
		self.complete_date = fields.Datetime.now()
		self.send_refused_mail()

	def action_approve(self):
		ret_act = None
		recs = self.filtered(lambda x: x.state == 'Submitted')
		for rec in recs:
			_logger.error(f"rec: {rec}")
			if not rec.is_pic:
				msg = _('{} do not have the authority to approve this request !'.format(rec.env.user.name))
				self.sudo().message_post(body=msg)
				return False
			lines = rec.line_id
			for line in lines:
				if not line or line.state != 'Waiting for Approval':
					# Something goes wrong!
					self.message_post(body=_('Something goes wrong!'))
					return False

				# Update follower
				rec.update_follower(self.env.uid)

				# check if this line is required
				other_lines = rec.line_ids.filtered(
					lambda x: x.sequence >= line.sequence and x.state == 'Draft')
				_logger.error(f"other lines: {other_lines}")
				if not other_lines:
					or_lines = rec.line_ids.filtered(
							lambda r: r.require_opt in ['or', 'Optional'] and r.state == 'Waiting for Approval')	
					_logger.error(f"or lines: {or_lines}")
					if or_lines:
						rec.pic_ids = None
						rec.line_id = None
						for option in or_lines:
							option.set_approved()
					
					ret_act = rec.set_approved()
				else:
					required_vals = other_lines.filtered(
						lambda r: r.require_opt in ['Required'] and r.state == 'Draft')
					if required_vals:
						optional_vals = other_lines.filtered(
						lambda r: r.require_opt in ['Optional'] and r.state == 'Draft')
						next_line = required_vals.sorted('sequence')[0]
						next_line.write({
							'state': 'Waiting for Approval',
						})

						rec.line_id = next_line
						rec.pic_ids = rec.line_id.user_id
						if optional_vals:
							for option in option_vals:
								rec.pic_ids += option.user_id
						rec.send_request_mail()
						recs.send_activity_notification()
					else:
						or_lines = other_lines.filtered(
							lambda r: r.require_opt in ['or', 'Optional'] and r.state == 'Waiting for Approval')

						_logger.error(f"or lines: {or_lines}")
						
						if or_lines:
							optional_vals = other_lines.filtered(
							lambda r: r.require_opt in ['Optional'] and r.state == 'Draft')
							rec.pic_ids = None
							rec.line_id = None
							for option in or_lines:
								option.write({
									'state': 'Approved'
									})	
								rec.line_id += option
								rec.pic_ids += option.user_id

								option.set_approved()
								
								
							if optional_vals:
								for option in option_vals:
									rec.pic_ids += option.user_id
							
							rec.send_request_mail()
							recs.send_activity_notification()
				line.set_approved()
				break
			msg = _('I approved')
			rec.finalize_activity_or_message('approved', msg)
		if ret_act:
			return ret_act
		return True

	def action_refuse(self, reason=''):
		ret_act = None
		recs = self.filtered(lambda x: x.state == 'Submitted')
		for rec in recs:
			if not rec.is_pic:
				msg = _('{} do not have the authority to approve this request !'.format(rec.env.user.name))
				self.sudo().message_post(body=msg)
				return False
			lines = rec.line_id
			for line in lines:
				if not line or line.state != 'Waiting for Approval':
					# Something goes wrong!
					self.message_post(body=_('Something goes wrong!'))
					return False

				# Update follower
				rec.update_follower(self.env.uid)

				# check if this line is required
				if line.require_opt in ['Required']:
					ret_act = rec.set_refused(reason)
					draft_lines = rec.line_ids.filtered(lambda x: x.state == 'Draft')
					if draft_lines:
						draft_lines.state = 'Cancel'
				else:  # optional
					other_lines = rec.line_ids.filtered(
						lambda x: x.sequence >= line.sequence and x.state == 'Draft')

					# current lines
					current_lines = rec.line_ids.filtered(
						lambda x: x.sequence >= line.sequence and x.state == 'Waiting for Approval')

					if other_lines:
						for other_line in other_lines:
							other_line.set_refused()

					if current_lines:
						for current_line in current_lines:
							current_line.set_refused()
						
				line.set_refused(reason)
				break
			msg = _('I refused due to this reason: {}'.format(reason))
			rec.finalize_activity_or_message('refused', msg)
		if ret_act:
			return ret_act

	def finalize_activity_or_message(self, action, msg):
		requests = self.filtered(
			lambda r: r.type_id.activity_notification
		)
		notify_type = self.env.ref("mail.mail_activity_data_todo", False)
		if requests and notify_type: 
			activities = requests.mapped("activity_ids").filtered(
				lambda a: a.activity_type_id == notify_type and a.user_id == self.env.user)
			activities._action_done(msg)

			or_activities = requests.mapped("activity_ids").filtered(
				lambda a: a.activity_type_id == notify_type)
			or_msg = _(f"{self.env.user.name} {action}")
			or_activities._action_done(or_msg)

		requests2 = self - requests
		if requests2:
			requests2.message_post(body=msg)

	def _create_approval_lines(self):
		ApprovalLine = self.env['multi.approval.line']
		for r in self:
			lines = r.type_id.line_ids.sorted('sequence')
			last_seq = 0
			first_approver_id = 0
			r.line_id = None
			r.pic_ids = None
			for l in lines:
				line_seq = l.sequence
				if not line_seq or line_seq <= last_seq:
					line_seq = last_seq + 1
				last_seq = line_seq
				vals = {
					'name': l.name,
					'user_id': l.get_user(),
					'sequence': line_seq,
					'require_opt': l.require_opt,
					'approval_id': r.id
				}
				if l == lines[0]:
					if l.require_opt == 'Required':
						vals.update({'state': 'Waiting for Approval'})
						r.pic_ids = l.user_id
						
				
				if l.require_opt in ['Optional', 'or'] and lines[0].require_opt in ['or', 'Optional']:
					r.pic_ids += l.user_id
					vals.update({'state': 'Waiting for Approval'})


				approval = ApprovalLine.create(vals)
				if lines[0].require_opt == 'Required' and l == lines[0]:
					r.line_id = approval
				elif lines[0].require_opt == 'or':
					if l.require_opt == 'or':
						r.line_id += approval
				else:
						r.line_id += approval

			
				#Get the first approver id
				if first_approver_id == 0:
					first_approver_id = l.get_user()


	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			seq_date = vals.get('request_date', fields.Datetime.now())
			vals['code'] = self.env['ir.sequence'].next_by_code(
				'multi.approval', sequence_date=seq_date) or _('New')
		result = super(MultiApproval, self).create(vals_list)
		return result

	# 12.0.1.3
	def send_request_mail(self):
		requests = self.filtered(
			lambda r: r.type_id.mail_notification and r.pic_ids and
				r.state == 'Submitted'
		)
		for req in requests:
			if req.type_id.mail_template_id:
				req.type_id.mail_template_id.send_mail(req.id)
			else:
				message = self.env['mail.message'].create({
					'subject': _('Request the approval for: {request_name}').format(
						request_name=req.display_name
					),
					'model': req._name,
					'res_id': req.id,
					'body': self.description,
				})
				
				email = ",".join(pic.email for pic in req.pic_ids)

				self.env['mail.mail'].sudo().create({
					'mail_message_id': message.id,
					'body_html': self.description,
					'email_to':	email,
					'email_cc': req.user_id.email,
					'email_from': req.user_id.email,
					'auto_delete': False,
					'state': 'outgoing',

				})

	def send_approved_mail(self):
		requests = self.filtered(
			lambda r: r.type_id.approve_mail_template_id and
				r.state == 'Approved'
		)
		for req in requests:
			req.type_id.approve_mail_template_id.send_mail(req.id)

	def send_refused_mail(self):
		requests = self.filtered(
			lambda r: r.type_id.refuse_mail_template_id and
				r.state == 'Refused'
		)
		for req in requests:
			req.type_id.refuse_mail_template_id.send_mail(req.id)

	def send_activity_notification(self):
		requests = self.filtered(
			lambda r: r.type_id.activity_notification and r.pic_ids and
				r.state == 'Submitted'
		)
		notify_type = self.env.ref("mail.mail_activity_data_todo", False)
		if not notify_type:
			return
		for req in requests:
			summary = _("The request {code} need to be reviewed").format(
				code=req.code
			)
			for pic_id in req.pic_ids:
				self.env['mail.activity'].create({
					'res_id': req.id,
					'res_model_id': self.env['ir.model']._get(req._name).id,
					'activity_type_id': notify_type.id,
					'summary': summary,
					'user_id': pic_id.id,
				})
