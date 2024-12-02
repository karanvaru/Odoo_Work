# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError,Warning


class ResCompany_Inherit(models.Model):
	_inherit = 'res.company'

	supplier_source_picking_type_id = fields.Many2one('stock.picking.type',)
	supplier_destination_picking_type_id = fields.Many2one('stock.picking.type',)
	email_user_ids = fields.Many2many('res.users',string='Email Users')

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	supplier_source_picking_type_id = fields.Many2one('stock.picking.type',string="Source Picking Type",related='company_id.supplier_source_picking_type_id',readonly=False)
	supplier_destination_picking_type_id = fields.Many2one('stock.picking.type',string="Destination Picking Type",related='company_id.supplier_destination_picking_type_id',readonly=False)
	email_user_ids = fields.Many2many('res.users',string='Email Users',related='company_id.email_user_ids',readonly=False)

	# @api.model
	# def get_values(self):
	# 	res = super(ResConfigSettings, self).get_values()
	# 	ICPSudo = self.env['ir.config_parameter'].sudo()
	# 	supplier_source_picking_type_id = ICPSudo.get_param('bi_customer_supplier_rma.supplier_source_picking_type_id')
	# 	supplier_destination_picking_type_id = ICPSudo.get_param('bi_customer_supplier_rma.supplier_destination_picking_type_id')
	# 	email_user_ids = ICPSudo.get_param('bi_customer_supplier_rma.email_user_ids')

	# 	res.update(
	# 		supplier_source_picking_type_id=int(supplier_source_picking_type_id),
	# 		supplier_destination_picking_type_id=int(supplier_destination_picking_type_id),
	# 		email_user_ids=email_user_ids.ids)
			
	# 	return res

	# def set_values(self):
	# 	super(ResConfigSettings, self).set_values()
	# 	ICPSudo = self.env['ir.config_parameter'].sudo()
		
	# 	ICPSudo.set_param('bi_customer_supplier_rma.supplier_source_picking_type_id',self.supplier_source_picking_type_id.id)
	# 	ICPSudo.set_param('bi_customer_supplier_rma.supplier_destination_picking_type_id',self.supplier_destination_picking_type_id.id)
	# 	ICPSudo.set_param('bi_customer_supplier_rma.email_user_ids',self.email_user_ids.ids)

