from odoo import fields,api,models,_
from odoo.exceptions import ValidationError

class sale_order_line(models.Model):

	_inherit = "sale.order.line"

	hsn_config_id = fields.Many2one(
		"account.hsn.taxes",
		string="HSN Config",
		related="product_id.hsn_tax_id",
	)

	partner_id = fields.Many2one(
		string="Customer",
		related="order_id.partner_id",
	)

	def get_hsn_tax_ids(self):
		if self.company_id.state_id.id == self.partner_id.state_id.id:
			child_ids = self.hsn_config_id.sale_gst_tax_id.children_tax_ids
			if child_ids:
				return child_ids
			else:
				return self.hsn_config_id.sale_gst_tax_id
		else:
			return self.hsn_config_id.sale_igst_tax_id


	@api.onchange('hsn_config_id', 'partner_id')
	def _set_tax_ids(self):
		if self.partner_id:
			if self.hsn_config_id:
				self.tax_id = self.get_hsn_tax_ids()
		else:
			raise ValidationError(
				_("Select Customer Before adding invoice lines.")
			)