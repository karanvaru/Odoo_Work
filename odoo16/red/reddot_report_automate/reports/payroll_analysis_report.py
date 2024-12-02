# -*- coding: utf-8 -*-

from odoo import models, fields, api



class PayrollAnalysisReport(models.Model):
    _name = "payroll.analysis"
    _description = "Payroll Analysis"
    _auto = False

    name = fields.Char(
        required=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        tracking=True,
    )
    struct_type_id = fields.Selection(
        [
            ('monthly', 'Monthly Fixed Wage'),
            ('hourly', 'Hourly Wage')
        ],
        default='monthly',
        required=True)

    date_from = fields.Date(
        string='From',
        store=True
    )
    date_to = fields.Date(
        string='To',
        store=True
    )
    category_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Category',
    )
    sequence = fields.Integer(
        required=True,
        index=True,
        default=5,
        help='Use to arrange calculation sequence'
    )
    code = fields.Char(
        required=True,
        help="The code of salary rules can be used as reference in computation of other rules. "
             "In that case, it is case sensitive."
    )

    quantity = fields.Float(
        digits='Payroll',
        default=1.0
    )
    rate = fields.Float(
        string='Rate (%)',
        digits='Payroll Rate',
        default=100.0
    )
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Rule',
        required=True
    )
    amount = fields.Float()
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        copy=False,
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, readonly=True,
    )

    payslip_name = fields.Char(
        string='Payslip Name', required=True,
    )

    @property
    def _table_query(self):
        query = '%s %s %s' % (self._select(), self._from(), self._where())
        return query

    @api.model
    def _select(self):
        return '''
            SELECT
                payslip_line.id AS id,
                payslip_line.sequence AS sequence,
                payslip_line.code AS code,
                payslip_line.quantity AS quantity,
                payslip_line.rate AS rate,
                payslip_line.name AS name,
                payslip_line.amount AS amount,
                payslip_line.category_id AS category_id,
                payslip_line.salary_rule_id AS salary_rule_id,
                payslip.company_id AS company_id,
                payslip.employee_id AS employee_id,
                payslip.name AS payslip_name,
                employee.department_id AS department_id,
                employee.parent_id AS manager_id,
                payslip.date_from AS date_from,
                payslip.date_to AS date_to
               
        '''

    @api.model
    def _from(self):
        return '''
            FROM
                hr_payslip_line as payslip_line
                LEFT JOIN hr_employee as employee ON payslip_line.employee_id = employee.id
                INNER JOIN hr_payslip payslip ON payslip.id = payslip_line.slip_id
        '''

    @api.model
    def _where(self):
        return '''
               WHERE payslip_line.category_id IS NOT NULL
                   AND payslip_line.salary_rule_id IS NOT NULL
                   AND payslip_line.slip_id IS NOT NULL
                   AND employee.id IS NOT NULL
           '''
