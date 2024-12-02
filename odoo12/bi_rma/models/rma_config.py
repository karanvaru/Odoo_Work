# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError,Warning

	
class ResConfigSettings_Inherit(models.TransientModel):
	_inherit = 'res.config.settings'

	b2b_source_picking_type_id = fields.Many2one('stock.picking.type',string="Source Picking Type",related='company_id.b2b_source_picking_type_id',readonly=False)
	b2b_destination_picking_type_id = fields.Many2one('stock.picking.type',string="Destination Picking Type",related='company_id.b2b_destination_picking_type_id',readonly=False)


	@api.model
	def get_values(self):
		res = super(ResConfigSettings_Inherit, self).get_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		b2b_source_picking_type_id = ICPSudo.get_param('bi_rma.b2b_source_picking_type_id')
		b2b_destination_picking_type_id = ICPSudo.get_param('bi_rma.b2b_destination_picking_type_id')

		res.update(
			b2b_source_picking_type_id=int(b2b_source_picking_type_id),
			b2b_destination_picking_type_id=int(b2b_destination_picking_type_id))
			
		return res

	def set_values(self):
		super(ResConfigSettings_Inherit, self).set_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		
		ICPSudo.set_param('bi_rma.b2b_source_picking_type_id',self.b2b_source_picking_type_id.id)
		ICPSudo.set_param('bi_rma.b2b_destination_picking_type_id',self.b2b_destination_picking_type_id.id)

class ResCompany(models.Model):
	_inherit = 'res.company'

	b2b_source_picking_type_id = fields.Many2one('stock.picking.type',)
	b2b_destination_picking_type_id = fields.Many2one('stock.picking.type',)
