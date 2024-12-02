from odoo import fields,api,models,_
from odoo.exceptions import ValidationError

class res_partner(models.Model):

	_inherit = "res.partner"


	@api.model
	def create(self, vals):
		partner = super(res_partner, self).create(vals)
		if self._context.get('from_employee', False):
			return partner
		if partner.state_id and partner.vat:
			tan_num = partner.state_id.l10n_in_tin
			vat_num = partner.vat[:2]
			print(tan_num)
			print(vat_num)
			if str(tan_num) != str(vat_num):
				raise ValidationError(
					_("GST should start from tan number of selected state id.")
				)		
		return partner


	def write(self, vals):
		res = super(res_partner, self).write(vals)
		if self._context.get('from_employee', False):
			return res
		for partner in self:
			if partner.state_id and partner.vat:
				tan_num = partner.state_id.l10n_in_tin
				vat_num = partner.vat[:2]
				print(tan_num)
				print(vat_num)
				if str(tan_num) != str(vat_num):
					raise ValidationError(
						_("GST should start from tan number of selected state id.")
					)
		return res


# 
# 	@api.onchange('state_id','vat')
# 	def validate_vat(self):
# 		if self.state_id and self.vat:
# 			tan_num = self.state_id.l10n_in_tin
# 			vat_num = self.vat[:2]
# 			print(tan_num)
# 			print(vat_num)
# 			if str(tan_num) != str(vat_num):
# 				raise ValidationError(
# 					_("VAT should start from tan number of selected state id.")
# 				)