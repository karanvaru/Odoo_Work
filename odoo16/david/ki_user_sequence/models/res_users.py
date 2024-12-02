# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file
# for full copyright and licensing details.

from odoo import models, fields, api


class ResUsers(models.Model):
	_inherit = 'res.users'

	seq_number = fields.Char(
		string="User ID",
		copy=False,
		readonly=True
	)

	@api.model
	def create(self, vals):
		print(vals)
		seq_obj = self.env['ir.sequence']
		if 'company_id' in vals:
			vals['seq_number'] = seq_obj.with_context(
				force_company=vals['company_id']
			).next_by_code('res.users.sequence')
		else:
			vals['seq_number'] = seq_obj.next_by_code('res.users.sequence')
		return super(ResUsers, self).create(vals)

	@api.model
	def _name_search(self, name,
			args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		user_ids = []
		if name:
			user_ids = self._search([
				'|', ('name', operator, name),
				('seq_number', operator, name)] + args,
				limit=limit, access_rights_uid=name_get_uid
			)
		return user_ids