# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import models,fields,api,_


class ReferAndEarnFaq(models.Model):
	_name = "refer.and.earn.faq"
	
	name = fields.Char(string="Name")
	faq_question = fields.Char(string="Question" ,required=True)
	faq_answer = fields.Html('Answer',required=True)
	active = fields.Boolean(String="Active",default=True)
	

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('refer.and.earn.faq')
		new =  super(ReferAndEarnFaq,self).create(vals)
		return new