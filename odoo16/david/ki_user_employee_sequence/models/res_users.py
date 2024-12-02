# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file
# for full copyright and licensing details.

from odoo import models, fields, api


class ResUsers(models.Model):
	_inherit = 'res.users'

	def name_get(self):
		super(ResUsers, self).name_get()
		result = []
		for rec in self:
			name = rec.name
			if rec.seq_number:
				name = rec.name + '(' + rec.seq_number + ')'
			result.append((rec.id, name))
		return result
