from odoo import _, api, fields, models




class CommissionKpiCategory(models.Model):
	_name = 'commission.kpi.category'
	_description = 'Commission Kpi Category'


	name = fields.Char('KPI Category', required=True)




class CommissionDedCategory(models.Model):
	_name = 'commission.ded.category'
	_description = 'Commission Ded Category'

	name = fields.Char('Deduction Category', required=True)

