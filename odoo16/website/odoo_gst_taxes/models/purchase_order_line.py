from odoo import fields,api,models,_
from odoo.exceptions import ValidationError


class purchase_order_line(models.Model):

	_inherit = "purchase.order.line"

	hsn_config_id = fields.Many2one(
		"account.hsn.taxes",
		string="HSN Config",
		related="product_id.hsn_tax_id",
	)

	def get_hsn_tax_ids(self):
		if self.company_id.state_id.id == self.partner_id.state_id.id:
			child_ids = self.hsn_config_id.purchase_gst_tax_id.children_tax_ids
			if child_ids:
				return child_ids
			else:
				return self.hsn_config_id.purchase_gst_tax_id
		else:
			return self.hsn_config_id.purchase_igst_tax_id


	@api.onchange('hsn_config_id','partner_id')
	def _set_tax_ids(self):
		if self.partner_id:
			if self.hsn_config_id:
				self.taxes_id = self.get_hsn_tax_ids()
		else:
			raise ValidationError(
				_("Select Customer Before adding invoice lines.")
			)


# class purchase_order(models.Model):

# 	_inherit = "purchase.order"

# 	product_url = fields.Char(
# 		string="Product URL",
# 	)

# 	def action_rfq_send(self):
# 		res = super(purchase_order, self).action_rfq_send()
# 		self._compute_access_url()
# 		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
# 		self.product_url = str(base_url) + str(self.access_url)
# 		print(self.product_url)
# 		return res