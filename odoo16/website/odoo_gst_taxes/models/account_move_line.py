from odoo import fields,api,models,_
from odoo.exceptions import ValidationError


class account_move(models.Model):

	_inherit = "account.move"

	@api.onchange('partner_id')
	def _onchange_partner_id(self):
		res = super(account_move, self)._onchange_partner_id()
		if self.partner_id:
			if self.invoice_line_ids:
				self.invoice_line_ids._set_tax_ids()
		return res


class account_move_line(models.Model):

	_inherit = "account.move.line"

	hsn_config_id = fields.Many2one(
		"account.hsn.taxes",
		string="HSN Config",
		related="product_id.hsn_tax_id",
	)

	def get_hsn_tax_ids(self):
		if self.company_id.state_id.id == self.partner_id.state_id.id:
			if self.move_id.move_type in ['out_invoice','out_refund']:
				child_ids = self.hsn_config_id.sale_gst_tax_id.children_tax_ids
				if child_ids:
					return child_ids
				else:
					return self.hsn_config_id.sale_gst_tax_id
			elif self.move_id.move_type in ['in_invoice','in_refund']:
				child_ids = self.hsn_config_id.purchase_gst_tax_id.children_tax_ids
				if child_ids:
					return child_ids
				else:
					return self.hsn_config_id.purchase_gst_tax_id
		else:
			if self.move_id.move_type in ['out_invoice','out_refund']:
				return self.hsn_config_id.sale_igst_tax_id
			elif self.move_id.move_type in ['in_invoice','in_refund']:
				return self.hsn_config_id.purchase_igst_tax_id

# 		if self.move_id.branch_id.state_id.id == self.partner_id.state_id.id:
# 			if self.move_id.move_type in ['out_invoice','out_refund']:
# 				child_ids = self.hsn_config_id.sale_gst_tax_id.children_tax_ids
# 				if child_ids:
# 					return child_ids
# 				else:
# 					return self.hsn_config_id.sale_gst_tax_id
# 			elif self.move_id.move_type in ['in_invoice','in_refund']:
# 				child_ids = self.hsn_config_id.purchase_gst_tax_id.children_tax_ids
# 				if child_ids:
# 					return child_ids
# 				else:
# 					return self.hsn_config_id.purchase_gst_tax_id
# 		else:
# 			if self.move_id.move_type in ['out_invoice','out_refund']:
# 				return self.hsn_config_id.sale_igst_tax_id
# 			elif self.move_id.move_type in ['in_invoice','in_refund']:
# 				return self.hsn_config_id.purchase_igst_tax_id


	@api.onchange('hsn_config_id','partner_id')
	def _set_tax_ids(self):
		print("sssssssssssssssssssssss")
		if self.partner_id:
			if self.hsn_config_id:
				self.tax_ids = self.get_hsn_tax_ids()
# 		else:
# 			raise ValidationError(
# 				_("Select Customer Before adding invoice lines.")
# 			)