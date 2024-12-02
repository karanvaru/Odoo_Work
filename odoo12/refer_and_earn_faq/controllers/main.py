# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from odoo.addons.refer_and_earn.controllers.main import website_refer_and_earn


class website_refer_and_earn_faq(website_refer_and_earn):

	@http.route('/refer_earn/', auth='public',type='http', website=True)
	def homepage(self, **kw):
		result = super(website_refer_and_earn_faq,self).homepage(**kw)
		_logger.info("----------inherit refer and eran home page---%r--",result.qcontext)
		faq = request.env['refer.and.earn.faq'].sudo().search([])
		_logger.info("--------faq---%r--",faq)

		result.qcontext.update({
			'faq':faq
			})
		return result
