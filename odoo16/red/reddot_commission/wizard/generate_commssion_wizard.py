from odoo import models, fields, api


class GenerateCommissionWizard(models.TransientModel):
    _name = 'generate.commission.wizard'
    _description = "Generate Commission Manually"

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today().replace(day=1)
    )
    end_date = fields.Date(
        string='End Date',
        default=fields.Date.today().replace(day=31),
        required=True
    )
    department_id = fields.Many2many(
        'hr.department',
        string='Department',
    )
    employee_ids = fields.Many2many(
        'hr.employee',
    )

    def action_confirm(self):
        domain = [
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('commission_history_line_id', '=', False),
            ('payment_state', '=', 'paid'),

        ]
        if self.employee_ids:
            domain += [('agent_id', 'in', self.employee_ids.ids)]
        invoice = self.env['account.move'].sudo().search(domain)
        for rec in invoice:
            rec._generate_bu_commission()
