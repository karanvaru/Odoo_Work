# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import datetime
import base64
from odoo.exceptions import UserError,Warning

class ExportCustomerPricelistReport(models.AbstractModel):
	_name = 'report.bi_customer_supplier_rma.rma_supplier_report_template1' 
	_description = 'Customer Pricelist Report'


	@api.model
	def _get_report_values(self, docids, data=None):
		from_date = data['form']['from_date']
		to_date = data['form']['to_date']
		state = data['form']['state']
		# partner_ids = self.env['res.partner'].browse(data['form']['partner_ids'])
		if state:
			active_ids = self.env['rma.supplier'].sudo().search([('date','>=',from_date),('date','<=',to_date),('state','=',state)])
		else:
			active_ids = self.env['rma.supplier'].sudo().search([('date','>=',from_date),('date','<=',to_date)])
		docargs = {
				   'doc_model': 'rma.supplier',
				   'data': data,
				   'docs': active_ids,
				   }
		return docargs

class RmaSupplierwizard(models.TransientModel):
	_name = 'rma.supplier.wizard'
	_description = "RMA Supplier Wizard"


	from_date = fields.Date('From Date', required = '1')
	to_date = fields.Date('To Date', required = '1')
	state = fields.Selection([
		('draft', 'DRAFT'),
		('approved_processing', 'APPROVED PROCESSING'),
		('send_to_vendor', 'Dispatched to Vendor'),
		('inwards', 'INWARDS'),
		('inwarded_material', 'INWARDED MATERIAL'),
		('close', 'CLOSED'),
		('reject','REJECTED')], string='Status', default='draft')

	@api.multi
	def print_report(self):
		active_ids = self.env['rma.supplier'].search([('date','>',self.from_date),('date','<',self.to_date),('state','=',self.state)])
		[data] = self.read()
		datas = {
		'ids': [1],
		'model': 'rma.supplier',
		'form': data
		}
		return self.env.ref('bi_customer_supplier_rma.rma_supplier_report1').report_action([], data=datas)


class RmaSupplier(models.Model):
	_name = 'rma.supplier'
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
	_description = "RMA Supplier"
	_order = "id desc"

	name = fields.Char('Name',default=lambda self: _('New'),store=True,track_visibility='onchange')
	# po_inventory_select = fields.Selection([('PO','Purchase Order'),('IA','Inventory Adjustment')], string = "RMA Selection" , default = "PO")
	# serial_no = fields.Char(string = 'Serial Number')
	is_validate = fields.Boolean("Validated",copy=False)
	purchase_order = fields.Many2one('purchase.order','Purchase Order', domain="[('state','=','purchase')]",track_visibility='onchange')
	# inventory_adj = fields.Many2one('stock.inventory','Inventory Adjustment', domain="[('state','=','done')]")
	subject = fields.Text('Problem Description',track_visibility='onchange')
	date = fields.Date('Date',default=fields.Date.context_today ,required=True,track_visibility='onchange')
	deadline = fields.Date('Deadline',track_visibility='onchange')
	rec_by_vendor = fields.Date('Vendor Received Date', track_visibility='onchange')
	rma_note = fields.Text('RMA Note',track_visibility='onchange')
	priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High'),('3','Very High')], 'Priority',track_visibility='onchange')
	delivery_order = fields.Many2one('stock.picking','Delivery Order',store=True,track_visibility='onchange')
	email = fields.Char('Email', store=True,track_visibility='onchange')
	partner = fields.Many2one('res.partner','Partner', store=True,track_visibility='onchange')
	phone = fields.Char('Phone', store=True,track_visibility='onchange')
	rma_line_ids = fields.One2many('rma.supplier.lines','rma_supplier_id','RMA Lines',store=True)
	reject_reason = fields.Char('Reject Reason')

	# picking_ids = fields.One2many(
	#     'stock.picking',
	#     'rma_supplier_id',
	#     string='RMA picking',
	#     copy = False
	# )
	in_delivery_count = fields.Integer(string='Incoming Orders', compute='_compute_incoming_picking_ids')
	out_delivery_count = fields.Integer(string='Outgoing Orders', compute='_compute_outgoing_picking_ids')
	refund_inv_count = fields.Integer(string='Refund Invoice', compute='_compute_refund_inv_ids')
	purchase_order_count = fields.Integer(string='Purchase Orders',compute='_compute_purchase_order_ids')
	# demo_compute = fields.Boolean(
	#     string='test data',
	#     compute="check_picking_ids"
	# )
	company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id,track_visibility='onchange')
	repair_count = fields.Integer(
		string='Repair Details',
		compute='_compute_repair_order_ids'
	)
	replace_count = fields.Integer(
		string='Repair Details',
		compute='_compute_replace_order_ids'
	)
	refund_count = fields.Integer(
		string='Refund Details',
		compute='_compute_refund_order_ids'
	)
	overdue_date = fields.Date(
		string='RMA Overdue Date'
	)
	overdue_string = fields.Char(
		string='Overdue',
		compute = "_find_overdue_details"
	)
	# state = fields.Selection([
	# 	('draft', 'DRAFT'),
	# 	('approved_processing', 'APPROVED PROCESSING'),
	# 	('send_to_vendor', 'Dispatched to Vendor'),
	# 	# ('inwards', 'INWARDS'),
	# 	('received_by_vendor', 'Received By Vendor'),
	# 	# ('sent_back_by_vendor', 'Sent Back By Vendor'),
	# 	('inwarded_material', 'Sent Back By Vendor'),
	# 	('second_approve', 'RDP Received'),
	# 	# ('done', 'Done'),
	# 	('close', 'CLOSED'),
	# 	('reject','REJECTED'),
	# 	('scrap', 'SCRAPED'),
	# 	], string='Status', default='draft',track_visibility='onchange')

	##########################pavan################
	state = fields.Selection([
		('draft', 'DRAFT'),
		('approved_processing', 'READY TO DISPATCH'),
		('send_to_vendor', 'DISPATCHED'),
		# ('inwards', 'INWARDS'),
		('received_by_vendor', 'REACHED TO VENDOR'),
		# ('sent_back_by_vendor', 'Sent Back By Vendor'),
		('inwarded_material', 'READY FOR PICKUP'),
		('courier_picked', 'COURIER PICKED'),
		('part_in_transit', 'PART IN TRANSIT'),
		('second_approve', 'PART RECEIVED'),
		# ('done', 'Done'),
		('close', 'CLOSED'),
		('reject', 'CANCELLED'),
		('scrap', 'SCRAPED'),
	], string='Status', default='draft', track_visibility='onchange')
	
	###################date 10-5-2023#####sabitha######## for the customization im adding extra fields##############
	sending_type_id = fields.Many2one('rma.supplier.sending.type','Sending To',track_visibility="onchange")
	type_id = fields.Many2one('rma.supplier.type','Type',track_visibility="onchange")

	###################complete cycle open days####################

	approved_in = fields.Datetime('Ready To Dispatch In')
	received_by_vendor_in = fields.Datetime('Reached To Vendor In')
	inwarded_material_in = fields.Datetime('Ready For Pickup In')
	# closed_in = fields.Datetime('Closed In')
	scrap_in = fields.Datetime('Scrap In')
	reject_date_in = fields.Datetime('Cancelled In')
	send_to_vendor_in = fields.Datetime('Dispatched In')
	second_approve_in = fields.Datetime('Part Received In')
	part_in_transit_in = fields.Datetime('Part In Transit In')
	courier_picked_in = fields.Datetime('Courier Picked In')

	
	


	@api.multi
	def get_groups_usesr_email(self):
		emails = []
		config_ids = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
		if config_ids.email_user_ids.ids:
			for partner in config_ids.email_user_ids:
				if partner.partner_id.email:
					emails.append(partner.partner_id.email)
		return emails

	def check_picking_ids(self):
		for srma in self:
			out_stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',srma.id),('picking_type_code','=','outgoing')]) 
			in_stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',srma.id),('picking_type_code','=','incoming')]) 
			if srma.state=="approved_processing" and out_stock_picking_ids:
				if all(line.state == 'done' for line in out_stock_picking_ids):
					srma.write({
						'state' : 'send_to_vendor',
						'send_to_vendor_in': datetime.datetime.now(),
						})
			# if srma.state == "inwarded_material" and in_stock_picking_ids:
			if srma.state == "inwarded_material" or srma.state == "courier_picked" or srma.state == "part_in_transit" and in_stock_picking_ids:
				if all(line.state == 'done' for line in in_stock_picking_ids):
					srma.write({
						'state' : 'second_approve',
						'second_approve_in': datetime.datetime.now(),
						})
			# stock_picking_ids = out_stock_picking_ids.filtered(lambda inv: inv.state != 'done')

	@api.multi
	def send_by_mail_customer_pricelist(self):
		today = datetime.datetime.utcnow().date()
		yesterday = today - datetime.timedelta(days=1)
		# [data] = self.read()
		data= {}
		data['from_date'] = str(yesterday.year)+'-'+str(yesterday.month)+'-'+str(yesterday.day)
		data['to_date'] =  str(today.year)+'-'+str(today.month)+'-'+str(today.day)
		data['state'] = False
		datas = {
				 'ids': [1],
				 'model': 'rma.supplier',
				 'form': data
		}
		template_id = self.env['ir.model.data'].get_object_reference('bi_customer_supplier_rma','email_template_rma_supplier')[1]
		email_template_obj = self.env['mail.template'].browse(template_id)
		emails = []
		config_ids = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
		if config_ids.email_user_ids.ids:
			for partner in config_ids.email_user_ids:
				if partner.partner_id.email:
					emails.append(partner.partner_id.id)
		if template_id:
			values = email_template_obj.generate_email(self.id, fields=None)
			values['name'] = 'RMA Supplier Reports'
			values['email_from'] = self.env.user.email
			# values['email_to'] = partner_email
			values['recipient_ids'] = [(4, pid) for pid in emails]
			values['author_id'] = self.env.user.partner_id.id
			values['res_id'] = False
			pdf = self.env.ref('bi_customer_supplier_rma.rma_supplier_report1').render_qweb_pdf([],data=datas)[0]
			values['attachment_ids'] = [(0,0,{
				'name': 'RMA_Supplier_Report.pdf',
				'datas': base64.encodebytes(pdf),
				'datas_fname' : 'RMA Supplier Report',
				'res_model': 'rms.supplier',
				'res_id': self.id,
				'mimetype': 'application/pdf',
				'type': 'binary',
				})]
			mail_mail_obj = self.env['mail.mail']
			msg_id = mail_mail_obj.sudo().create(values)
			if msg_id:
				msg_id.sudo().send()


	@api.depends('overdue_date')
	def _find_overdue_details(self):
		today = datetime.datetime.utcnow().date()
		for rma_s in self:
			if rma_s.overdue_date:
				someday = rma_s.overdue_date
				diff = someday - today
				if diff.days > 0:
					rma_s.overdue_string = str(diff.days)+' days to go'
				else:
					rma_s.overdue_string = str(abs(diff.days))+' overdue days'
			else:
				rma_s.overdue_string = ''



	@api.model
	def create(self,vals):
		vals.update({
			'name': self.env['ir.sequence'].next_by_code('rma.supplier.order'),
		})
		return super(RmaSupplier, self).create(vals)

	@api.multi
	def _compute_incoming_picking_ids(self):
		for order in self:
			stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',order.id)]) #,('picking_type_code','=','incoming')
			order.in_delivery_count = len(stock_picking_ids)

	@api.multi
	def _compute_outgoing_picking_ids(self):
		for order in self:
			stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',order.id)])
			order.out_delivery_count = len(stock_picking_ids)

	@api.multi
	def _compute_refund_inv_ids(self):
		for inv in self:
			refund_inv_ids = self.env['account.invoice'].search([('rma_supplier_id','=',inv.id)])
			inv.refund_inv_count = len(refund_inv_ids)

	@api.multi        
	def _compute_purchase_order_ids(self): 
		for order in self:
			purchase_order_ids = self.env['purchase.order'].search([('rma_supplier_id','=',order.id)])
			order.purchase_order_count = len(purchase_order_ids)

	@api.multi        
	def _compute_repair_order_ids(self): 
		for order in self:
			repair_order_ids = self.env['rma.repair.product'].search([('rma_supplier_id','=',order.id)])
			order.repair_count = len(repair_order_ids)

	@api.multi        
	def _compute_refund_order_ids(self): 
		for order in self:
			refund_order_ids = self.env['rma.refund.product'].search([('rma_supplier_id','=',order.id)])
			order.refund_count = len(refund_order_ids)

	@api.multi        
	def _compute_replace_order_ids(self): 
		for order in self:
			repair_order_ids = self.env['rma.replace.product'].search([('rma_supplier_id','=',order.id)])
			order.replace_count = len(repair_order_ids)

	@api.onchange('po_inventory_select')
	def onchange_selection(self):
		self.purchase_order = False
		self.inventory_adj = False
		self.serial_no = False

	@api.onchange('serial_no')
	def onchange_basket(self):

		if self.serial_no != '' and self.serial_no != False:
			serial_no = self.env['stock.production.lot'].search([('name','=',self.serial_no)])
			stock_inv_line = self.env['stock.inventory.line'].search([('prod_lot_id','=',serial_no.id)])
			mv_line_id = self.env['stock.move.line'].search([('lot_id','=',serial_no.id)])
			stkl = []
			for invline in stock_inv_line:
				if invline.inventory_id.id not in stkl:
					stkl.append(invline.inventory_id.id)
			mv_origin = []
			for mvl in mv_line_id:
				mv_origin.append(mvl.reference)
			picking_id = self.env['stock.picking'].search([('name','in',mv_origin),('picking_type_code','=','incoming'),('state','=','done')])
			pick_origin = []
			for pko in picking_id:
				pick_origin.append(pko.origin)
			purchase_id = self.env['purchase.order'].search([('name','in',pick_origin),('state','=','purchase')])
			res = {
			'domain' : {
				'purchase_order' : [('id', 'in', purchase_id.ids)],
				'inventory_adj': [('id', 'in', stkl)],
				}
			}
		else:
			res = {
			'domain' : {
				'purchase_order' : [('id', 'in', [])],
				'inventory_adj': [('id', 'in', [])],
				}
			}
		return res


	@api.onchange('purchase_order','inventory_adj')
	def set_purchase_details(self):

		purchase_order_obj = self.env['purchase.order'].search([('id','=',self.purchase_order.id)])
		self.partner = purchase_order_obj.partner_id.id
		self.phone = purchase_order_obj.partner_id.phone
		self.email = purchase_order_obj.partner_id.email

		for delivery_ord in purchase_order_obj.picking_ids:
			if delivery_ord.state == 'done':
				self.delivery_order = delivery_ord.id

		order_line_dict = {}
		order_line_list = []

		for line in self.rma_line_ids:
			self.rma_line_ids = [(2,line.id,0)]
			self.delivery_order = False

		for i in purchase_order_obj.order_line:
			order_line_dict = {
				'product_id': i.product_id.id,
				'delivery_qty': i.product_qty,
				'price_unit': i.price_unit,
			}
			order_line_list.append((0,0, order_line_dict))

		self.rma_line_ids = order_line_list


	def generate_invent_detail(self):
		order_line_dict = {}
		order_line_list = []
		if self.po_inventory_select == "PO":
			purchase_order_obj = self.env['purchase.order'].search([('id','=',self.purchase_order.id)])
			stock_move_lines = self.env['stock.move.line'].search([('reference','=',self.delivery_order.name),('state','=','done')])
			count_qty = 0
			for i in purchase_order_obj.order_line:
				for mvl in stock_move_lines:
					if i.product_id.id == mvl.product_id.id:
						order_line_dict = {
							'product_id': i.product_id.id,
							'qty' : mvl.qty_done,
							'lot_id' : mvl.lot_id.id,
							'price_unit' : i.price_unit

						}
						order_line_list.append((0,0, order_line_dict))
			export_id = self.env['serial.picking.details'].create({'inventory_details': order_line_list,'rma_id':self.id})
			res = {
				'view_mode': 'form',
				'res_id': export_id.id,
				'res_model': 'serial.picking.details',
				'view_type': 'form',
				'type': 'ir.actions.act_window',
				'target':'new'
			}
			return res
		else:
			inv_obj = self.env['stock.inventory'].search([('id','=',self.inventory_adj.id)])
			# stock_move_lines = self.env['stock.inventory.line'].search([('reference','=',self.delivery_order.name),('state','=','done')])
			count_qty = 0
			for i in inv_obj.line_ids:
				order_line_dict = {
					'product_id': i.product_id.id,
					'qty' : i.product_qty,
					'lot_id' : i.prod_lot_id.id,
					'price_unit' : i.product_id.lst_price

				}
				order_line_list.append((0,0, order_line_dict))
			export_id = self.env['serial.picking.details'].create({'inventory_details': order_line_list,'rma_id':self.id})
			res = {
				'view_mode': 'form',
				'res_id': export_id.id,
				'res_model': 'serial.picking.details',
				'view_type': 'form',
				'type': 'ir.actions.act_window',
				'target':'new'
			}
			return res

	@api.multi
	def rma_line_btn(self):

		self.ensure_one()
		return { 
			'name': 'Product', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'product.product', 
			'domain': [('rma_supplier_id','=',self.id)],
		}

	@api.onchange('deadline','date')
	def _onchange_deadline(self):

		if self.deadline and self.date:
			if self.date > self.deadline:
				raise Warning(_("Please select a proper date."))

	@api.multi
	def action_send_rma(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('bi_customer_supplier_rma', 'email_template_edi_rma_supplier')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model': 'rma.supplier',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'force_email': True
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	@api.multi
	def action_approve(self):
		self.approved_in = datetime.datetime.now()
		stock_picking_obj = self.env['stock.picking']
		flag = False
		for r in self.rma_line_ids:
			if(r.action == 'replace'):
				r.show_prod_setting = True
			
			if(r.action in ['replace','repair']):
				flag = True
		if self.purchase_order and not self.delivery_order:
			raise Warning(_('Please confirm the purchase order first.'))
		else:
			res_company = self.env.user.company_id
			# if not flag:			
			stock_move_obj = self.env['stock.move']
			count = 0
			stock_picking = False
			for product in self.rma_line_ids:
				if not flag:
					if count ==0:
						vals= {
							'rma_supplier_id' : self.id,
							'partner_id' : self.partner.id,
							'location_id' :  res_company.supplier_source_picking_type_id.default_location_src_id.id,
							'location_dest_id' : res_company.supplier_source_picking_type_id.default_location_dest_id.id,
							'origin' : self.purchase_order.name,
							# 'scheduled_date' : self.date,
							'picking_type_code' : 'outgoing',
							'picking_type_id' : res_company.supplier_source_picking_type_id.id,
							}
						
						stock_picking = stock_picking_obj.create(vals)
						product_vals = {
										'name' : product.product_id.name,
										'product_id' : product.product_id.id,
										'product_uom_qty' : float(product.return_qty),
										'product_uom' : product.product_id.uom_id.id,
										'picking_id' : stock_picking.id,
										'location_id' : res_company.supplier_source_picking_type_id.default_location_src_id.id,
										'location_dest_id' : res_company.supplier_source_picking_type_id.default_location_dest_id.id,
										'picking_type_id' : res_company.supplier_source_picking_type_id.id,
										}
						stock_move_obj.create(product_vals)
					else:
						product_vals = {
										'name' : product.product_id.name,
										'product_id' : product.product_id.id,
										'product_uom_qty' : float(product.return_qty),
										'product_uom' : product.product_id.uom_id.id,
										'picking_id' : stock_picking.id,
										'location_id' : res_company.supplier_source_picking_type_id.default_location_src_id.id,
										'location_dest_id' : res_company.supplier_source_picking_type_id.default_location_dest_id.id,
										'picking_type_id' : res_company.supplier_source_picking_type_id.id,
										}
						stock_move_obj.create(product_vals)
				else:
					destination_id = res_company.supplier_source_picking_type_id.default_location_dest_id.id
					if product.vendor_id.id:
						destination_id = product.vendor_id.property_stock_supplier.id
					if count ==0:
						vals = {
							'rma_supplier_id' : self.id,
							'partner_id' : product.vendor_id.id or self.partner.id,
							'location_id' : res_company.supplier_source_picking_type_id.default_location_src_id.id,
							'location_dest_id' : destination_id ,
							'origin' : self.purchase_order.name,
							# 'scheduled_date' : self.date,
							'picking_type_code' : 'outgoing',
							'picking_type_id' : res_company.supplier_source_picking_type_id.id,
							}
						
						stock_picking = stock_picking_obj.create(vals)
						product_vals = {
										'name' : product.product_id.name,
										'product_id' : product.product_id.id,
										'product_uom_qty' : float(product.return_qty),
										'product_uom' : product.product_id.uom_id.id,
										'picking_id' : stock_picking.id,
										'location_id' : res_company.supplier_source_picking_type_id.default_location_src_id.id,
										'location_dest_id' :destination_id,
										'picking_type_id' : res_company.supplier_source_picking_type_id.id,
										}
						stock_move_obj.create(product_vals)
					else:
						product_vals = {
										'name' : product.product_id.name,
										'product_id' : product.product_id.id,
										'product_uom_qty' : float(product.return_qty),
										'product_uom' : product.product_id.uom_id.id,
										'picking_id' : stock_picking.id,
										'location_id' : res_company.supplier_source_picking_type_id.default_location_src_id.id,
										'location_dest_id' : destination_id,
										'picking_type_id' : res_company.supplier_source_picking_type_id.id,
										}
						stock_move_obj.create(product_vals)
				# else:
				if product.action == 'repair':
					repair_id = self.env['rma.repair.product'].search([('rma_supplier_id','=',product.rma_supplier_id.id)])
					if not repair_id.id:
						repair_id = self.env['rma.repair.product'].create({
								'rma_supplier_id' : product.rma_supplier_id.id,
								'partner' : product.vendor_id.id or self.partner.id,
							})
					product.rma_repair_id = repair_id.id
					repair_id.state = "progress"

				if product.action == 'replace':
					replace_id = self.env['rma.replace.product'].search([('rma_supplier_id','=',product.rma_supplier_id.id)])
					if not replace_id.id:
						replace_id = self.env['rma.replace.product'].create({
								'rma_supplier_id' : product.rma_supplier_id.id,
								'partner' : product.vendor_id.id or self.partner.id,
							})
					product.rma_replace_id = replace_id.id
					replace_id.state = "progress"

				if product.action == 'refund':
					refund_id = self.env['rma.refund.product'].search([('rma_supplier_id','=',product.rma_supplier_id.id)])
					if not refund_id.id:
						refund_id = self.env['rma.refund.product'].create({
								'rma_supplier_id' : product.rma_supplier_id.id,
								'partner' : product.vendor_id.id or self.partner.id,
							})
					product.rma_refund_id = refund_id.id
					refund_id.state = "progress"

			self.write({'state':'approved_processing'})
			if stock_picking:
				stock_picking.action_confirm()
				for rml in self.rma_line_ids:
					for mv in stock_picking.move_ids_without_package:
						if rml.product_id.id == mv.product_id.id:
							smv_line = self.env['stock.move.line'].search([('move_id','=',mv.id), ('lot_id' ,'=', False)])
							if smv_line:
								smv_line.write({
									'lot_id' : rml.lot_id.id,
									'qty_done' : mv.product_uom_qty,
									})
							else:
							
								self.env['stock.move.line'].create({
									'move_id':mv.id,
									'lot_id' : rml.lot_id.id,
									'product_uom_id':rml.product_id.uom_po_id.id,
									'location_id' : stock_picking.location_id.id,
									'location_dest_id' :stock_picking.location_dest_id.id,
									'product_id' : rml.product_id.id,
									'qty_done' : mv.product_uom_qty,
									'picking_id' : stock_picking.id
									})
			return

	@api.multi 
	def action_view_receipt(self): 
		self.ensure_one()
		return { 
			'name': 'Picking', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'stock.picking', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	# @api.multi 
	# def action_view_deliveries(self): 
	# 	self.ensure_one()
	# 	return { 
	# 		'name': 'Picking', 
	# 		'type': 'ir.actions.act_window', 
	# 		'view_mode': 'tree,form', 
	# 		'res_model': 'stock.picking', 
	# 		'domain': [('rma_supplier_id','=',self.id)], 
	# 	}

	@api.multi 
	def action_view_refund_invoice(self): 
		self.ensure_one()
		return { 
			'name': 'Refund Invoice', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'account.invoice', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	@api.multi 
	def action_view_purchase_order(self): 
		return { 
			'name': 'Purchase Order', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'purchase.order', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	@api.multi 
	def action_view_repair_order(self): 
		return { 
			'name': 'Repair Order', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'rma.repair.product', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	@api.multi 
	def action_view_refund_order(self): 
		return { 
			'name': 'Refund Order', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'rma.refund.product', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	@api.multi 
	def action_view_replace_order(self): 
		return { 
			'name': 'Replace Order', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'rma.replace.product', 
			'domain': [('rma_supplier_id','=',self.id)], 
		}

	@api.multi
	def action_move_to_draft(self):
		self.write({'state':'draft'})
		return


	@api.multi
	def action_move_to_scrap(self):
		self.write({'state': 'scrap'})
		self.scrap_in = datetime.datetime.now()
		return

	@api.multi
	def action_close(self):
		self.write({'state':'close'})
		return

	@api.multi
	def action_received_by_vendor(self):
		self.write({'state': 'received_by_vendor'})
		self.write({'rec_by_vendor': datetime.datetime.utcnow().date()})
		self.received_by_vendor_in = datetime.datetime.now()
		return

	@api.multi
	def action_move_to_courier_picked(self):
		self.write({'state': 'courier_picked'})
		self.courier_picked_in = datetime.datetime.now()
		return

	@api.multi
	def action_move_to_part_in_transit(self):
		self.write({'state': 'part_in_transit'})
		self.part_in_transit_in = datetime.datetime.now()
		return

	# @api.multi
	# def action_sent_back_by_vendor(self):
	# 	self.write({'state': 'sent_back_by_vendor'})
	# 	return

	@api.multi
	def action_done(self):
		self.write({'state':'done'})
		return
	

	@api.model
	def create_supplier_delivery(self,value):

		stock_picking_obj = self.env['stock.picking']
		stock_move_obj = self.env['stock.move']
		res_company = self.env.user.company_id
		partner_id = self.partner.id
		vendor_id = self.env['res.partner'].browse(value.get('vendor_id', False))
		Location_id = res_company.supplier_destination_picking_type_id.default_location_src_id.id
		if vendor_id:
			partner_id = vendor_id.id	
			Location_id = vendor_id.property_stock_supplier.id
		vals= {
			'rma_supplier_id' : self.id,
			'partner_id' : partner_id,
			'location_id' : Location_id,
			'location_dest_id' : res_company.supplier_destination_picking_type_id.default_location_dest_id.id,			
			'picking_type_code' : 'outgoing',
			'picking_type_id' : res_company.supplier_destination_picking_type_id.id,
			'state': 'done',
		}

		stock_picking = stock_picking_obj.create(vals)

		if stock_picking:
			stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',self.id)])
			self.out_delivery_count = len(stock_picking_ids)

		if value.get('replaced_qty'): 
			r_qty = value['replaced_qty']
		else:
			r_qty = 1

		stock_move_lines = stock_move_obj.create({
			'name': value['product_id'].name,
			'product_uom': value['product_id'].uom_id.id,
			'product_id' : value['product_id'].id,
			'product_uom_qty': r_qty,
			'quantity_done': r_qty,
			'picking_id': stock_picking.id,
			'location_id' : Location_id,
			'location_dest_id' : res_company.supplier_destination_picking_type_id.default_location_dest_id.id,
			'picking_type_id' : res_company.supplier_destination_picking_type_id.id,
		})

	@api.multi
	def create_replaced_product_purchase_order(self,values):
		purchase_obj = self.env['purchase.order']
		purchase_ord_line_obj = self.env['purchase.order.line']

		replaced_purchase_order = purchase_obj.create({
			'rma_supplier_id': self.id,
			'name': self.env['ir.sequence'].next_by_code('purchase.order'),
			'partner_id': self.purchase_order.partner_id.id,
			'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			'date_planned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		})

		purchase_ord_lines = purchase_ord_line_obj.create({
			'product_id' : values['product_id'].id,
			'name':values['product_id'].name,
			'product_qty': values['replaced_qty'],
			'price_unit': values['price_unit'],
			'order_id': replaced_purchase_order.id,
			'product_uom' : values['product_id'].uom_po_id.id,
			'date_planned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		})

		purchase_ord_count = self.purchase_order_count + 1

		self.update({
			'purchase_order_count': purchase_ord_count,
		})

	@api.multi
	def create_supplier_credit_note_for_refundable_product(self,values):

		acc_invoice_obj = self.env['account.invoice']
		acc_inv_line_obj = self.env['account.invoice.line']
		product_obj = self.env['product.product']     
		rma_supplier = self.env['rma.supplier'].search([('id','=',values['rma_supplier_id'].id)])

		find_curr_prod = product_obj.search([('id','=',values['product_id'].id)])

		replaced_product_id = find_curr_prod.id
		replaced_prod_desc = find_curr_prod.name
		replaced_product_qty = values['replaced_qty']
		replaced_prod_price = find_curr_prod.lst_price

		invoice_for_rma_supplier = self.env['account.invoice'].search([('rma_supplier_id','=',rma_supplier.id)])
		if invoice_for_rma_supplier:
			acc_invoice = invoice_for_rma_supplier
		else:
			acc_invoice = acc_invoice_obj.create({
				'rma_supplier_id' : rma_supplier.id,
				'partner_id' : rma_supplier.purchase_order.partner_id.id,
				'type' : 'in_refund',
			})

		account = find_curr_prod.property_account_income_id or find_curr_prod.categ_id.property_account_income_categ_id
		
		if not account:
			raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
				(find_curr_prod.name, find_curr_prod.id, find_curr_prod.categ_id.name))
		
		prepare_inv_line = {
			'product_id' : replaced_product_id,
			'name' : replaced_prod_desc,
			'quantity' : replaced_product_qty,
			'price_unit' : replaced_prod_price,
			'invoice_id' : acc_invoice.id,
			'account_id' : account.id,
		}
		acc_inv_line_obj.create(prepare_inv_line)

	@api.multi
	def action_validate(self):
		rma_line_list = []
		move_line_list = []
		self.inwarded_material_in = datetime.datetime.now()

		related_picking_rma = self.env['rma.supplier'].search([('id','=',self.id)])
		stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',self.id)])
		replace_ids = related_picking_rma.rma_line_ids.filtered(lambda inv: inv.action == 'replace')
		is_replace = replace_ids.filtered(lambda inv: not inv.replaced_with.id )
		if is_replace:
			raise Warning(_("Please Select Replace Product first."))
		
		for r in related_picking_rma.rma_line_ids:
			if(r.action == 'replace'):
				if r.replaced_with.id:
					if r.product_id.id == r.replaced_with.id:
						
						delivery_vals = {
							'rma_supplier_id': self,
							'product_id': r.replaced_with,
							'replaced_qty': r.return_qty,
							'vendor_id' : r.vendor_id.id,
						}
						self.create_supplier_delivery(delivery_vals)
						repair_id = self.env['rma.repair.product'].search([('rma_supplier_id','=',self.id)])
						if repair_id.id:
							repair_id.state = 'replace'
						replace_id = self.env['rma.replace.product'].search([('rma_supplier_id','=',self.id)])
						if replace_id.id:
							replace_id.state = 'replace'
					else:
						if r.is_invoice:
							purchase_vals = {
								'rma_supplier_id': self,
								'product_id': r.replaced_with,
								'replaced_qty': r.replaced_qty,
								'price_unit':r.price_unit,
								'vendor_id' : r.vendor_id.id,
							}
							self.create_replaced_product_purchase_order(purchase_vals)
						else:
							delivery_vals = {
								'rma_supplier_id': self,
								'product_id': r.replaced_with,
								'replaced_qty': r.replaced_qty,
								'vendor_id' : r.vendor_id.id,
							}
							self.create_supplier_delivery(delivery_vals)
						repair_id = self.env['rma.repair.product'].search([('rma_supplier_id','=',self.id)])
						if repair_id.id:
							repair_id.state = 'replace'
						replace_id = self.env['rma.replace.product'].search([('rma_supplier_id','=',self.id)])
						if replace_id.id:
							replace_id.state = 'replace'
			if(r.action == 'repair'):
				
				delivery_vals = {
					'rma_supplier_id': self,
					'product_id': r.product_id,
					'replaced_qty': r.return_qty,
					'vendor_id' : r.vendor_id.id,
				}
				self.create_supplier_delivery(delivery_vals)
				repair_id = self.env['rma.repair.product'].search([('rma_supplier_id','=',self.id)])
				if repair_id.id:
					repair_id.state = 'repair'

				replace_id = self.env['rma.replace.product'].search([('rma_supplier_id','=',self.id)])
				if replace_id.id:
					replace_id.state = 'replace'
			if(r.action == 'refund'):
				if r.is_invoice:

					credit_note_vals = {
						'rma_supplier_id': self,
						'product_id': r.product_id,
						'replaced_qty': r.return_qty,
						'price_unit':r.price_unit,
					}
					self.create_supplier_credit_note_for_refundable_product(credit_note_vals)

			self.write({'is_validate': True,'state' : 'inwarded_material'})
		return


class SerialPickingDetails(models.TransientModel):
	_name = 'serial.picking.details'

	inventory_details = fields.One2many(
		'inventory.picking.details',
		'serial_picking_id',
		string='Field Label',
	)
	rma_id = fields.Many2one(
		'rma.supplier',
		string='RMA id',
	)

	def generate_rma_detail(self):
		ivt_details = self.inventory_details.filtered(lambda r: r.is_added == True)
		if len(ivt_details) == 0:
			raise Warning(_("Please check any checkbox which product you want to add in RMA line."))    
		order_line_dict = {}
		order_line_list = []
		for ipd in ivt_details:
			order_line_dict = {
				'product_id': ipd.product_id.id,
				'delivery_qty': ipd.qty,
				'price_unit': ipd.price_unit,
				'lot_id' : ipd.lot_id.id
			}
			order_line_list.append((0,0, order_line_dict))

		self.rma_id.rma_line_ids = order_line_list			


class InventoryPickingDetails(models.TransientModel):
	_name = 'inventory.picking.details'

	serial_picking_id = fields.Many2one(
		'serial.picking.details',
		string='Serial Picking Details',
	)
	product_id = fields.Many2one(
		'product.product',
		string='product',
	)
	lot_id = fields.Many2one(
		'stock.production.lot',
		string='Lot / Serial NO',
	)
	qty = fields.Integer(
		string='Quantity',
	)
	price_unit = fields.Integer(
		string='Price Unit',
	)
	is_added = fields.Boolean(
		string='added?',
	)

class RmaSupplierChangeProduct(models.TransientModel):

	_name = 'rma.supplier.change.product'

	rma_prod = fields.Many2one('product.product','Product', )
	prod_change_qty = fields.Float("Quantity")
	rma_supplier_id = fields.Many2one('rma.supplier','RMA Number')
	create_invoice = fields.Boolean("Create Invoice")
	diff_product = fields.Boolean(help='Different Product Options',default=False)
	
	@api.onchange('rma_prod')
	def _onchange_wizard_product(self):

		if self.rma_prod and self._context["active_id"]:
			curr_line_prod = self.env['rma.supplier.lines'].search([('id','=',self._context["active_id"])])
			if self.rma_prod != curr_line_prod.product_id:
				self.diff_product = True
			else:
				self.diff_product = False

	@api.model
	def default_get(self,fields):

		rec = super(RmaSupplierChangeProduct, self).default_get(fields)
		ctx = self._context["active_id"]
		t = self.env['rma.supplier.lines'].browse(ctx)
		rec.update({
			'rma_supplier_id': t.rma_supplier_id.id
		})

		return rec

	@api.multi
	def change_prod(self):
		
		product_obj = self.env['product.product']
		find_curr_wiz_prod = product_obj.search([('id','=',self.rma_prod.id)])

		replaced_product_id = self.rma_prod.id
		replaced_prod_desc = find_curr_wiz_prod.name
		replaced_product_qty = self.prod_change_qty
		replaced_prod_price = find_curr_wiz_prod.lst_price

		ctx = self._context["active_id"]
		t = self.env['rma.supplier.lines'].browse(ctx)

		t.replaced_with = find_curr_wiz_prod.id

		if t.delivery_qty >= self.prod_change_qty:
			if t.return_qty >= self.prod_change_qty:
				t.replaced_qty = self.prod_change_qty
			else:
				raise Warning(_("Return quantity should be less or equal to return quantity."))    
		else:
			raise Warning(_("Return quantity should be less or equal to delivery quantity."))
			

		if self.create_invoice:
			t.is_invoice = True
		else:
			t.is_invoice = False
			

class RejectSupplierWizard(models.Model):

	_name = 'reject.supplier.reason'
	_rec_name = 'reject_reason'

	reject_reason = fields.Char("Reject Reason")

class RejectSupplierWizard(models.TransientModel):

	_name = 'create.supplier.reject'

	rma_reason_id = fields.Many2one('reject.supplier.reason','Reject reason')


	@api.multi
	def create_reject(self):
		rma_supplier_id = self.env['rma.supplier'].browse(self._context.get('active_id'))
		rma_supplier_id.write({'reject_reason':self.rma_reason_id.reject_reason,'state':'reject','reject_date_in':self.create_date})
		return

class RmaClaim(models.Model):

	_name = 'rma.supplier.claim'
	_rec_name = 'rma_supplier_id'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Number')
	subject = fields.Char('Subject')
	partner = fields.Many2one('res.partner','Partner', store=True)
	date = fields.Date('Date')
	nxt_act_dt = fields.Date('Next Action Date')
	nxt_act = fields.Char('Next Action')
	stock_picking_id = fields.Many2one('stock.picking')


class RmaRepairDetails(models.Model):

	_name = 'rma.repair.product'
	_rec_name = 'rma_supplier_id'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Number')
	partner = fields.Many2one('res.partner','Partner', store=True)
	rma_lines = fields.One2many('rma.supplier.lines','rma_repair_id',string='RMA Lines',)
	state = fields.Selection([
		('draft', 'Draft'),
		('progress', 'Work In Progress'),
		('repair', 'Repaired'),
		('replace', 'Replaced')
		], string='Status', default='draft')


	@api.multi
	def write(self, vals):
		if vals.get('rma_lines', False):
			rml_id = vals.get('rma_lines', False)[0][1]
			rma_line = self.env['rma.supplier.lines'].browse(rml_id)
			details_for_line = vals.get('rma_lines', False)[0][2]
			if details_for_line.get('reason', False):
				reason = self.env['rma.supplier.reason'].browse(details_for_line.get('reason', False))
				if reason.reason_action == 'replace':
					rma_line.show_prod_setting = True
				else:
					rma_line.show_prod_setting = False
		return super(RmaRepairDetails, self).write(vals)

class RmaRefundDetails(models.Model):

	_name = 'rma.refund.product'
	_rec_name = 'rma_supplier_id'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Number')
	partner = fields.Many2one('res.partner','Partner', store=True)
	rma_lines = fields.One2many('rma.supplier.lines','rma_refund_id',string='RMA Lines',)
	state = fields.Selection([
		('draft', 'Draft'),
		('progress', 'Work In Progress'),
		('repair', 'Repaired'),
		('replace', 'Replaced')
		], string='Status', default='draft')


	@api.multi
	def write(self, vals):
		if vals.get('rma_lines', False):
			rml_id = vals.get('rma_lines', False)[0][1]
			rma_line = self.env['rma.supplier.lines'].browse(rml_id)
			details_for_line = vals.get('rma_lines', False)[0][2]
			if details_for_line.get('reason', False):
				reason = self.env['rma.supplier.reason'].browse(details_for_line.get('reason', False))
				if reason.reason_action == 'replace':
					rma_line.show_prod_setting = True
				else:
					rma_line.show_prod_setting = False
		return super(RmaRefundDetails, self).write(vals)

class RmaReplaceDetails(models.Model):

	_name = 'rma.replace.product'
	_rec_name = 'rma_supplier_id'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Number')
	partner = fields.Many2one('res.partner','Partner', store=True)
	rma_lines = fields.One2many('rma.supplier.lines','rma_replace_id',string='RMA Lines',)
	state = fields.Selection([
		('draft', 'Draft'),
		('progress', 'Work In Progress'),
		('repair', 'Repaired'),
		('replace', 'Replaced')
		], string='Status', default='draft')


	@api.multi
	def write(self, vals):
		if vals.get('rma_lines', False):
			rml_id = vals.get('rma_lines', False)[0][1]
			rma_line = self.env['rma.supplier.lines'].browse(rml_id)
			details_for_line = vals.get('rma_lines', False)[0][2]
			if details_for_line.get('reason', False):
				reason = self.env['rma.supplier.reason'].browse(details_for_line.get('reason', False))
				if reason.reason_action == 'replace':
					rma_line.show_prod_setting = True
				else:
					rma_line.show_prod_setting = False
		return super(RmaReplaceDetails, self).write(vals)


class RmaLines(models.Model):

	_name = 'rma.supplier.lines'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Id')
	rma_repair_id = fields.Many2one('rma.repair.product','Repair Id')
	rma_replace_id = fields.Many2one('rma.replace.product','Replace Id')
	rma_refund_id = fields.Many2one('rma.refund.product','Refund Id')
	product_id = fields.Many2one('product.product','Product')
	delivery_qty = fields.Float('Delivered Quantity')
	return_qty = fields.Float('Return Quantity')
	reason = fields.Many2one('rma.supplier.reason','Reason')
	recieved_qty = fields.Float('Recieved Quantity')
	action = fields.Selection('Action',related='reason.reason_action')
	show_prod_setting = fields.Boolean('Show Poduct setting',default=False)
	price_unit = fields.Float('Price')
	replaced_with = fields.Many2one('product.product','Replaced with')
	replaced_qty = fields.Float('Replaced Quantity')
	is_invoice = fields.Boolean('Is invoice',default=False)
	vendor_id = fields.Many2one(
		'res.partner',
		string='vendor',
	)
	lot_id = fields.Many2one(
		'stock.production.lot',
		string='Serial No/Lot',
	)
	brand_id = fields.Many2one('product.brand.amz.ept','Brand',compute='compute_brand')
    

	@api.onchange('return_qty')
	def _onchange_return_qty(self):

		if self.return_qty:
			if self.delivery_qty < self.return_qty:
				raise Warning(_("Quantity should be less than delivered."))
			
	@api.multi
	def compute_brand(self):
		for rec in self:

			rec.brand_id = rec.product_id.product_brand_id.id

 			
			
  		

	# @api.multi
	# def write(self, vals):
	# 	res = super(RmaLines, self).write(vals)
	# 	# if vals.get('reason', False):
	# 	# 	print(self._context,"qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq" , vals)
	# 	if vals.get('vendor_id',False):
	# 		self.rma_supplier_id.update({
	# 			'state' : 'send_to_vendor'
	# 			})
	# 	return res 


class RmaReason(models.Model):

	_name = 'rma.supplier.reason'
	_rec_name = 'rma_reason'

	rma_reason = fields.Char('RMA Reason',required=True)
	reason_action = fields.Selection([('replace', 'Replace'),('refund', 'Refund'),('repair', 'Repair')], string='Action')

class RefundAccInvoice(models.Model):

	_inherit = 'account.invoice'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Supplier Id')

class RmaPurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	rma_supplier_id = fields.Many2one('rma.supplier','RMA Supplier Id')

class RmaSupplierStockPicking(models.Model):
	_inherit = "stock.picking"

	rma_supplier_id = fields.Many2one('rma.supplier',string='RMA Supplier ID')
	claim_supplier_id = fields.Many2one('rma.supplier.claim',string='Supplier Claim ID')
	claim_supplier_count = fields.Float('Claim Count',compute='_compute_supplier_claim_ids')

	@api.multi
	def _compute_supplier_claim_ids(self):
		for order in self:
			rma_claim_ids = self.env['rma.supplier.claim'].search([('stock_picking_id','=',order.id)])
			order.claim_supplier_count = len(rma_claim_ids)

	@api.multi 
	def action_rma_supplier_claim_view(self): 
		self.ensure_one()
		return { 
			'name': 'Rma Supplier Claim', 
			'type': 'ir.actions.act_window', 
			'view_mode': 'tree,form', 
			'res_model': 'rma.supplier.claim', 
			'domain': [('stock_picking_id','=',self.id)], 
		}

	

	@api.multi
	def button_validate(self):

		validate_super = super(RmaSupplierStockPicking,self).button_validate()
		
		rma_line_list = []
		move_line_list = []

		related_picking_rma = self.env['rma.supplier'].search([('id','=',self.rma_supplier_id.id)])
		stock_picking_ids = self.env['stock.picking'].search([('rma_supplier_id','=',self.rma_supplier_id.id),('picking_type_code','=','outgoing')])
		# self.rma_supplier_id.check_picking_ids()
		for r in related_picking_rma.rma_line_ids:
			rma_line_list.append(r.id)

		for m in self.move_lines:
			move_line_list.append(m.id)

		for m in self.move_lines:
			move_line_list.append(m.id)

		for i,j in zip(rma_line_list,move_line_list):
			get_qty = self.env['stock.move'].browse(j)
			self.env['rma.supplier.lines'].browse(i).write({'recieved_qty':get_qty.product_uom_qty})

		# related_picking_rma.write({'state':'approved_processing'})
		related_picking_rma.check_picking_ids()
		vals = {
				'rma_supplier_id' : self.rma_supplier_id.id,
				'subject' : self.rma_supplier_id.subject,
				'partner' : self.rma_supplier_id.partner.id,
				'date' : self.rma_supplier_id.date,
				'nxt_act_dt' : datetime.datetime.utcnow().date(),   
				'nxt_act' :datetime.datetime.utcnow().date(), 
				'stock_picking_id' : self.rma_supplier_id.delivery_order.id

		}
		claim = self.env['rma.supplier.claim'].create(vals)

		return validate_super

	@api.multi
	def action_cancel(self):

		cancel_supplier_super = super(RmaSupplierStockPicking,self).action_cancel()

		cancel_picking_rma = self.env['rma.supplier'].search([('id','=',self.rma_supplier_id.id)])
		
		cancel_picking_rma.update({
			'state': 'close',
		})

		return True   
			
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   
# 
class RMASuppleirSendingType(models.Model):

	_name = 'rma.supplier.sending.type'
	_description = 'RMS Supplier Sending Type'

	name = fields.Char('Name') 

class RMASuppleirType(models.Model):

	_name = 'rma.supplier.type'
	_description = 'RMS Supplier Type'

	name = fields.Char('Name') 	
