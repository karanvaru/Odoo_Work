from odoo import fields, models, api

class LoanSettings(models.Model):
    _name = 'loan.settings'
    _description = 'Approvers for loan'

    country_accountant = fields.Many2one('res.users', '1. Country Accountant')
    hr_manager = fields.Many2one('res.users', '2. HR Manager')
    chief_financial_officer = fields.Many2one('res.users', '3. Chief Finance Officer')
    super_approver = fields.Many2one('res.users', '4. Super Approver')
    company_id = fields.Many2one('res.company', 'Company', required=True)
