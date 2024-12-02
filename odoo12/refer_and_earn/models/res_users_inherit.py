# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
from ast import literal_eval

class ResUserInherit(models.Model):

	_inherit = 'res.users'
	_inherits = {'res.partner': 'partner_id'}

	referral_code = fields.Char(related='partner_id.referral_code',string='Partner Referral Code', inherited=True)
	