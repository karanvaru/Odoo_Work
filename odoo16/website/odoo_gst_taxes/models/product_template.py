from odoo import fields,api,models


class product_category(models.Model):

	_inherit = "product.category"

	hsn_tax_id = fields.Many2one(
		"account.hsn.taxes",
		string="HSN Tax",
	)


class product_template(models.Model):

	_inherit = "product.template"

	hsn_tax_id = fields.Many2one(
		"account.hsn.taxes",
		string="HSN Tax",
	)

	@api.onchange('categ_id')
	def set_categ_id(self):
		if self.categ_id:
			if self.categ_id.hsn_tax_id:
				self.hsn_tax_id = self.categ_id.hsn_tax_id.id

	@api.onchange('hsn_tax_id')
	def set_hsn_fields(self):
		self.l10n_in_hsn_code = self.hsn_tax_id.name
		self.l10n_in_hsn_description = self.hsn_tax_id.description