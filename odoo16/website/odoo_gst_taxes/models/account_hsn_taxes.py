from odoo import fields,api,models

class account_hsn_taxes(models.Model):

	_name = "account.hsn.taxes"

	name = fields.Char(
		string="Name",
		required=True,
		size=6
	)
	company_id = fields.Many2one(
		'res.company',
		default=lambda self: self.env.company,
		required=True
	)

	description = fields.Char(
		string="Description",
	)

	sale_igst_tax_id = fields.Many2one(
		"account.tax",
		string="Sale IGST Tax",
# 		domain=lambda self: "[('type_tax_use','in',['sale']),('tax_group_id','=',%s)]"\
# 						% self.env['account.tax.group'].sudo().search([('name','=','IGST')]).id,
		required=True,
	)

	sale_gst_tax_id = fields.Many2one(
		"account.tax",
		string="Sale SGST and CGST Tax",
# 		domain=lambda self: "[('type_tax_use','in',['sale']),('tax_group_id','in',%s)]"\
# 						% self.env['account.tax.group'].sudo().search([('name','in',['SGST','GST','CGST'])]).ids,
		required=True,
	)

	purchase_igst_tax_id = fields.Many2one(
		"account.tax",
		string="Purchase IGST Tax",
# 		domain=lambda self: "[('type_tax_use','in',['purchase']),('tax_group_id','=',%s)]"\
# 						% self.env['account.tax.group'].sudo().search([('name','=','IGST')]).id,
		required=True,
	)

	purchase_gst_tax_id = fields.Many2one(
		"account.tax",
		string="Purchase SGST and CGST Tax",
# 		domain=lambda self: "[('type_tax_use','in',['purchase']),('tax_group_id','in',%s)]"\
# 						% self.env['account.tax.group'].sudo().search([('name','in',['SGST','GST','CGST'])]).ids,
		required=True,
	)

	product_ids = fields.One2many(
		"product.template",
		"hsn_tax_id",
		string="Products",
	)