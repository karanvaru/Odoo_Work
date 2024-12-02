from odoo import fields,api,models


class ResCountryState(models.Model):

	_inherit = "res.country.state"

	professional_tax = fields.Float(
		'PT'
	)

	def name_get(self):
		result = []
		for record in self:
			result.append((record.id, "{} ({})".format(record.name, record.l10n_in_tin or record.country_id.code)))
		return result