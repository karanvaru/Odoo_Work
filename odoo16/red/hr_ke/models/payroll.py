# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as Eval
from datetime import datetime, timedelta
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    paye = fields.Float('PAYE', compute="_compute_basic_net", store=True)

    @api.depends('line_ids.total')
    def _compute_basic_net(self):
        if self.contract_id.company_id.country_id.id == self.env.ref(
                'base.ae').id:
            super(HrPayslip, self)._compute_basic_net()
            for payslip in self:
                payslip.paye = 0
        else:
            line_values = (self._origin)._get_line_values(
                ['P010', 'P120', 'P101'])
            for payslip in self:
                payslip.basic_wage = line_values['P010'][payslip._origin.id][
                    'total']
                payslip.net_wage = line_values['P120'][payslip._origin.id][
                    'total']
                payslip.paye = line_values['P101'][payslip._origin.id]['total']


class KESalaryRule(models.Model):
    """ inherits salary rules model to add more """
    _inherit = 'hr.salary.rule'

    def _satisfy_condition(self, localdict):
        """
        @param rule_id: id of hr.salary.rule to be tested
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the
        condition for the given contract. Return False otherwise.
        """
        localdict = dict(localdict, rule=self)  # include current rule object
        return super(KESalaryRule, self)._satisfy_condition(localdict)

    def _compute_rule(self, localdict):
        """
        :param  rule_id: id  of rule  to compute
        :param localdict:  dictionary containing the environement
        in which to compute the rule
        return: returns a tuple build as the base/amount computed,
        the quantity and the rate :type: (float, float, float)
        """
        localdict = dict(localdict, rule=self)  # include current rule object
        return super(KESalaryRule, self)._compute_rule(localdict)


class KECarBenefit(models.Model):
    """ Car benefits model"""
    _name = "ke.cars"
    _description = "Car Benefit"
    _inherit = ["mail.thread"]

    name = fields.Char('Car Registration Number:', required=True)
    make = fields.Char('Make', required=True)
    body = fields.Selection(
        [
            ('saloon',
             'Saloon Hatch Backs and Estates'),
            ('pickup',
             'Pick Ups,Panel Vans Uncovered'),
            ('cruiser',
             'Land Rovers/Cruisers(excluding Range Rover and similar cars)')],
        required=True,
        default='saloon',
        string="Body Type:")
    cc_rate = fields.Integer('CC Rating:', required=True)
    cost_type = fields.Selection([('Owned',
                                   'Owned'),
                                  ('Hired',
                                   'Hired')],
                                 required=True,
                                 string="Type of Car Cost:",
                                 default='Owned')
    cost_hire = fields.Float('Cost of Hire:', digits=(32, 2))
    cost_own = fields.Float('Cost of Owned Car:', digits=(32, 2))
    contract_id = fields.Many2one('hr.contract', 'Contract')


class KEBenefitType(models.Model):
    """ Types of benefits model """
    _name = "ke.benefit.type"
    _description = "Benefit Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Benefit', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Payroll Rule',
        domain=[
            ('sequence',
             '<=',
             '36'),
            ('sequence',
             '>=',
             '31'),
            ('active',
             '=',
             True)],
        help='Pick a salary rule that will be used to compute this \
		type of benefit in the payslip',
        required=True)
    company_id = fields.Many2one('res.company', 'Company', required=False)


class KEBeforeGrossDeductionsType(models.Model):
    """ Types of Cash allowances model """
    _name = "ke.before.gross.deduction.type"
    _description = "Before Gross Deduction Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Deduction', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule', 'Salary Rule', required=True,
        help="""This is the Salary rule that will be used to compute the amount of\
				before gross deduction in the payslip for each applicable employee""")
    company_id = fields.Many2one('res.company', 'Company', required=False)


class KECashAllowancesType(models.Model):
    """ Types of Cash allowances model """
    _name = "ke.cash.allowances.type"
    _description = "Cash Allowances Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Cash Allowance', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule', 'Salary Rule', required=True,
        domain=[('sequence', '>=', 11),
                ('sequence', '<=', 24),
                ('active', '=', True)],
        help="""This is the Salary rule that will be used to compute the amount of\
				allowance in the payslip for each applicable employee""")
    company_id = fields.Many2one('res.company', 'Company',required=False)


class KEReliefType(models.Model):
    """ Kenya's types of tax relief model"""
    _name = "ke.relief.type"
    _description = "Tax Relief Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Relief', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        required=True,
        domain=[
            ('sequence',
             '>=',
             96),
            ('sequence',
             '<=',
             99),
            ('active',
             '=',
             True)],
        help="""Pick a salary rule that will be used to compute \
				this type of tax relief in the payslip""")


class KEDeductionsType(models.Model):
    """ Kenya's type of post tax deductions model"""
    _name = "ke.deductions.type"
    _description = "After Tax Deduction Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Deduction', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        required=True,
        domain=[
            ('sequence',
             '>=',
             107),
            ('sequence',
             '<=',
             114),
            ('active',
             '=',
             True)],
        help="""This is the payslip rule which is used to calculate \
		how much of this deduction will be effected in the payroll.\
		Try to match the name of the rule with the name of the \
		deduction you are creating""")
    company_id = fields.Many2one('res.company', 'Company',required=False)



class KETaxRelief(models.Model):
    """ Kenya's tax reliefs model"""
    _name = "ke.reliefs"
    _description = "Tax Relief"
    _inherit = ["mail.thread"]
    _order = "employee_id, name asc"

    @api.depends('employee_id')
    def _default_company_id(self):
        for rec in self:
            rec.company_id = rec.employee_id.company_id.id or rec.employee_id.user_id.company_id.id

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.relief_id.name) + \
                       ' (' + str(rec.employee_id.name) + ')' + \
                       str(rec.date_start)

    def _default_formula(self):
        return """
# Available variables for use in formula:
# -----------------------------------------
# employee: selected employee record.
# relief: the current relief  record.
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    @api.depends('computation', 'fixed')
    def compute_relief(self):
        if self.computation == 'fixed':
            self.amount = self.fixed
        elif self.computation == 'formula':
            baselocaldict = {
                'result': None,
                'employee': self.employee_id,
                'relief': self}
            localdict = dict(baselocaldict)
            try:
                Eval(self.formula, localdict, mode='exec', nocopy=True)
            except BaseException:
                raise ValidationError(
                    _('Wrong formula defined for this \
					  Tax Relief: %s\n [%s].') % (self.name, self.formula))
            self.amount = localdict['result']
        else:
            self.amount = 0.00

    name = fields.Char('Name of Relief', compute='compute_name', store=True)
    relief_id = fields.Many2one(
        'ke.relief.type',
        'Type of Relief',
        required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        related='relief_id.rule_id',
        string='Salary Rule')
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        required=True)
    fixed = fields.Float('Fixed Value', digits='Account')
    amount = fields.Float(
        'Computed value',
        compute='compute_relief',
        digits='Account',
        store=True,
        help="This is computed value of the relief if you are using a formula\
		else it is the fixed value of the relief")
    computation = fields.Selection(
        [
            ('fixed',
             'Use a Fixed Value'),
            ('formula',
             'Use a Formula')],
        'Computation Method',
        required=True,
        help="Choose a method to use to arrive at a value for the relief")
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="Define a formula to use to arrive at the tax relief if its \
		based on certain variables. Available variables are stated in the\
		text area of the formula")
    company_id = fields.Many2one(
        'res.company',
        'Company',
        compute='_default_company_id', store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)

    date_start = fields.Datetime('Date Start', default=default_date)
    date_end = fields.Datetime('Date End')
    is_permanent = fields.Boolean('No Date End')


class KEDeductions(models.Model):
    _name = "ke.deductions"
    _description = "After Tax Deduction"
    _inherit = ["mail.thread"]
    _order = "id, name asc"

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.deduction_id.name) + \
                       ' (' + str(rec.employee_id.name) + ')' + \
                       str(rec.date_start)

    @api.depends('computation', 'fixed')
    def compute_deduction(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed

            elif rec.computation == 'formula':
                baselocaldict = {
                    'result': None,
                    'employee': rec.employee_id,
                    'deduction': rec}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Error in the formula defined for this\
						  deduction: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']
            else:
                rec.amount = 0.00

    def _default_formula(self):
        return """
# Available variables for use in formula:
# --------------------------------------
# employee: selected employee record
# deduction: current deduction record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    @api.depends('employee_id')
    def _default_company_id(self):
        for rec in self:
            rec.company_id = rec.employee_id.company_id.id or rec.employee_id.user_id.company_id.id

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    company_id = fields.Many2one(
        'res.company',
        'Company',
        compute='_default_company_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)
    name = fields.Char(
        'Name',
        compute='compute_name',
        store=True,
        help="Name of the after-tax deduction")
    deduction_id = fields.Many2one(
        'ke.deductions.type',
        'Type of Deduction',
        required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        related='deduction_id.rule_id',
        string='Payslip Rule',
        help="The Payslip or salary rule used to compute the value of \
		this deduction")
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        required=True)
    fixed = fields.Float(
        'Fixed Amount',
        digits='Account',
        help="Fixed value of this deduction as opposed to a changing value \
		based on formula")
    computation = fields.Selection([('fixed',
                                     'Fixed Amount'),
                                    ('formula',
                                     'Use a Formula'),
                                    ],
                                   'Computation Method',
                                   required=True,
                                   help="Select a method to use to compute \
								   this deduction.")
    amount = fields.Float(
        'Amount to Deduct',
        compute='compute_deduction',
        digits='Account',
        store=True,
        help="This is the computed amount to be deducted after tax, \
		this amount is equal to the fixed amount if the computation \
		method is set to 'Fixed Amount'")
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="The Formula to use in computing the dedcutions. \
		The variables containing useful data is stated within \
		the text inside the formula ")

    date_start = fields.Datetime('Date Start', default=default_date)
    date_end = fields.Datetime('Date End')
    is_permanent = fields.Boolean('No Date End')


class KEBeforeGrossDeductions(models.Model):
    _name = "ke.before.gross.deduction"
    _description = "Before Gross Deduction"
    _inherit = ["mail.thread"]
    _order = "id, name asc"

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.deduction_id.name) + \
                       ' (' + str(rec.employee_id.name) + ')' + \
                       str(rec.date_start)

    @api.depends('computation', 'fixed')
    def compute_deduction(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed

            elif rec.computation == 'formula':
                baselocaldict = {
                    'result': None,
                    'employee': rec.employee_id,
                    'deduction': rec}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Error in the formula defined for this\
						  deduction: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']
            else:
                rec.amount = 0.00

    def _default_formula(self):
        return """
# Available variables for use in formula:
# --------------------------------------
# employee: selected employee record
# deduction: current deduction record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    @api.depends('employee_id')
    def _default_company_id(self):
        for rec in self:
            rec.company_id = rec.employee_id.company_id.id or rec.employee_id.user_id.company_id.id

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    company_id = fields.Many2one(
        'res.company',
        'Company',
        compute='_default_company_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)
    name = fields.Char(
        'Name',
        compute='compute_name',
        store=True,
        help="Name of the after-tax deduction")
    deduction_id = fields.Many2one(
        'ke.before.gross.deduction.type',
        'Type of Deduction',
        required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        related='deduction_id.rule_id',
        string='Payslip Rule',
        help="The Payslip or salary rule used to compute the value of \
		this deduction")
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        required=True)
    fixed = fields.Float(
        'Fixed Amount',
        digits='Account',
        help="Fixed value of this deduction as opposed to a changing value \
		based on formula")
    computation = fields.Selection([('fixed',
                                     'Fixed Amount'),
                                    ('formula',
                                     'Use a Formula'),
                                    ],
                                   'Computation Method',
                                   required=True,
                                   help="Select a method to use to compute \
								   this deduction.")
    amount = fields.Float(
        'Amount to Deduct',
        compute='compute_deduction',
        digits='Account',
        store=True,
        help="This is the computed amount to be deducted after tax, \
		this amount is equal to the fixed amount if the computation \
		method is set to 'Fixed Amount'")
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="The Formula to use in computing the dedcutions. \
		The variables containing useful data is stated within \
		the text inside the formula ")

    date_start = fields.Datetime('Date Start', default=default_date)
    date_end = fields.Datetime('Date End')
    is_permanent = fields.Boolean('No Date End')


class KEBenefits(models.Model):
    _name = "ke.benefits"
    _description = "Benefits"
    _inherit = ["mail.thread"]
    _order = "contract_id, name asc"

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    @api.depends('computation', 'fixed')
    def compute_benefit(self):
        if self.computation == 'fixed':
            self.amount = self.fixed
        elif self.computation == 'formula':
            baselocaldict = {
                'result': None,
                'contract': self.contract_id,
                'benefit': self}
            localdict = dict(baselocaldict)
            try:
                Eval(self.formula, localdict, mode='exec', nocopy=True)
            except BaseException:
                raise ValidationError(
                    _('Wrong formula defined for this benefit: %s\n [%s].') %
                    (self.name, self.formula))
            self.amount = localdict['result']
        else:
            self.amount = 0.00

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.benefit_id.name) + \
                       ' (' + str(rec.contract_id.name) + ')' + \
                       str(rec.date_start)

    @api.depends('contract_id')
    def _default_company_id(self):
        for rec in self:
            rec.company_id = rec.contract_id.employee_id.company_id.id or rec.contract_id.employee_id.user_id.company_id.id

    def _default_formula(self):
        return """
# Available variables for use in formula:
# --------------------------------------
# contract: the current contract record
# benefit: the current benefit record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    name = fields.Char(
        'Name',
        compute='compute_name',
        store=True,
        help="The name of this benefit as would appear in \
		the employee contract.")
    benefit_id = fields.Many2one(
        'ke.benefit.type',
        'Type of Benefit',
        required=True)
    rule_id = fields.Many2one(
        related='benefit_id.rule_id',
        store=True,
        string="Salary Rule",
        help="The Payslip rule used to compute this benefit")
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        required=True,
        help="The contract of the employee in which the benefit is given")
    amount = fields.Float(
        'Computed Value',
        compute='compute_benefit',
        digits='Account',
        store=True,
        help="This is the computed value of the benefit if you are using \
		a formula else this value is equal to the fixed value if there \
		is not formula to apply ")
    computation = fields.Selection([('fixed',
                                     'Use the fixed value'),
                                    ('formula',
                                     'Use a Formula')],
                                   'Computation Method',
                                   required=True,
                                   help="Select a method to use to compute the\
								   benefit")
    fixed = fields.Float(
        'Fixed Value',
        digits='Account',
        help="This is a fixed value of the benefit as opposed to a changing \
		value based on formula")
    company_id = fields.Many2one(
        'res.company',
        'Company',
        compute='_default_company_id', store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="Define a formula to use to compute the value of the benefit \
		if the value depends on certain variables. The available variables are listed in the formula area.")

    date_start = fields.Datetime('Date Start', default=default_date)
    date_end = fields.Datetime('Date End')
    is_permanent = fields.Boolean('No Date End')


class KECashAllowances(models.Model):
    _name = "ke.cash_allowances"
    _description = "Cash Allowances"
    _inherit = ["mail.thread"]
    _order = "contract_id asc"

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    @api.depends('computation', 'fixed')
    def compute_cash_allowance(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed
            elif rec.computation == 'formula':
                baselocaldict = {'result': None, 'contract': rec.contract_id}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Wrong formula defined for Cash Allowances: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']

            else:
                rec.amount = 0.00

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.cash_allowance_id.name) + \
                       ' (' + str(rec.contract_id.name) + ')'

    @api.depends('contract_id')
    def _default_company_id(self):
        for rec in self:
            rec.company_id = rec.contract_id.employee_id.company_id.id or rec.contract_id.employee_id.user_id.company_id.id

    def _default_formula(self):
        return """
# Available variables for use in formula:
# ----------------------------------------
# contract: the current contract record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    name = fields.Char('Name', compute='compute_name', store=True)
    cash_allowance_id = fields.Many2one(
        'ke.cash.allowances.type',
        'Type of Cash Allowance',
        required=True)
    rule_id = fields.Many2one(
        related='cash_allowance_id.rule_id',
        store=True,
        string="Salary Rule")
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)
    amount = fields.Float(
        'Taxable Value',
        compute='compute_cash_allowance',
        digits='Account',
        store=True)
    computation = fields.Selection([('fixed',
                                     'Use Fixed Value'),
                                    ('formula',
                                     'Use Predefined Formula')],
                                   'Computation Method',
                                   required=True)
    fixed = fields.Float('Fixed Value', digits='Account')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        compute='_default_company_id', store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)
    formula = fields.Text('Formula', default=_default_formula)
    date_start = fields.Datetime('Date Start', default=default_date)
    date_end = fields.Datetime('Date End')
    is_permanent = fields.Boolean('No Date End')


class KERelationType(models.Model):
    _name = "ke.relation.type"
    _description = "Relation Type"
    _order = "name asc"
    _inherit = ["mail.thread"]

    name = fields.Char('Name')
    medical = fields.Boolean('Medical Beneficiary?', default=False)
    amount = fields.Float(string='Amount')
    dep_multiplying_factor = fields.Float(string='Dependants Multiplying Factor')
    non_dep_multiplying_factor = fields.Float(string='Dependants Multiplying Factor')

class KEKins(models.Model):
    _description = "Employee Kin"
    _name = "ke.employee.kin"
    _order = "name asc"
    _inherit = ["mail.thread"]

    name = fields.Char('Name', required=True)
    birthday = fields.Date('Date of Birth')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    phone = fields.Char('Phone Number')
    kin = fields.Boolean('Is Next of Kin?', default=False)
    relation = fields.Many2one(
        'ke.relation.type',
        'Type of Relation',
        required=True)
    address = fields.Text('Next of Kin Address')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)


class KEEmployee(models.Model):
    _inherit = ["hr.employee"]

    @api.depends('write_date')
    def _compute_employee_number(self):
        for rec in self:
            if rec.payroll_no:
                rec.employee_no = rec.payroll_no
            else:
                rec.employee_no = str(rec.id).zfill(4)

    def _get_default_currency(self):
        return self.env.user.company_id.currency_id

    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=_get_default_currency)
    nhif = fields.Char(
        'NHIF No.',
        help="Fill in the NHIF number issued by National Hospital Insurance Fund. For those employees in the formal sector, it is compulsory to be a member.")
    nssf_vol = fields.Boolean(
        'NSSF Voluntary Contributions?',
        default=False,
        help="Check this box if the employee or employer or both are is willing to contribute voluntarily to NSSF Scheme.The amount will be a voluntary top up by either employee or employer over and above the mandatory tier I and tier II contributions")
    nssf_t3 = fields.Boolean(
        'NSSF Tier III Contributions?', default=False,
        help="This is for pension contributions above the mandatory amount defined in the NSSF Act 2013.The exact figure will vary from employer to employer")
    nssf_vol_mem = fields.Float(
        'Voluntary Member Amount',
        digits='Account')
    nssf_vol_emp = fields.Float(
        'Voluntary Employer Amount',
        digits='Account')
    nssf_t3_emp = fields.Float(
        'Tier III Employer Amount',
        digits='Account')
    nssf_t3_mem = fields.Float(
        'Tier III Member Amount',
        digits='Account')
    nssf = fields.Char(
        'NSSF No.',
        help="key in the Employee NSSF number. It is mandatory to register as a memmber of NSSF as an employee")
    helb = fields.Boolean(
        'HELB Loan ?', default=False,
        help="Check this box if the employee is currently paying for Higher Education Loans Board Loan")
    helb_rate = fields.Float(
        'HELB Monthly Amount',
        digits='Account',
        help="HELB will issue Loan payment instructions for your employee upon contacting them. Upon the employment of any loanee, you need to inform the Board in writing within a period of three months of such employment. Fill in the monthly figure advised by HELB.")
    tax_pin = fields.Char(
        'KRA PIN',
        help="Key in the 11 charater PIN of the employee, It is mandatory to have a PIN as a tax payer")
    # Others
    # birth_country = fields.Many2one('res.country', 'Country of Birth')
    kins = fields.One2many(
        'ke.employee.kin',
        'employee_id',
        'Dependants',
        help="These are records of details of family members of the employee who may be benefiting from Health Insurance or any other such benefits offered by employer")
    employee_no = fields.Char(
        'Internal Number',
        compute='_compute_employee_number',
        store=True,
        help="This is a unique number assigned to each employee internally in the DB. If you do not set the payroll number, this number will be used as the payroll number")
    payroll_no = fields.Char(
        'Payroll Number',
        help="a unique number assigned to each employee to be used in payroll")
    personal_email = fields.Char(
        'Personal Email',
        help="Personal Email that can be used to reach the employee before or after employment")
    before_gross_deductions = fields.One2many(
        'ke.before.gross.deduction',
        'employee_id',
        'Before Gross Deductions')
    deductions = fields.One2many(
        'ke.deductions',
        'employee_id',
        'Deductions',
        help="These are after-tax deductions (other than NHIF and HELB) made on employee salary.They include contributions or deductions towards SACCO,Salary Advance,etc")

    reliefs = fields.One2many(
        'ke.reliefs', 'employee_id', 'Tax Relief',
        help="These are tax reliefs (other than the Personal Tax Relief) entitled to th employee..example is the Insurance relief.")
    # disability Tax Exemption
    disability = fields.Boolean(
        'Employee has disability ?',
        default=False,
        help="Check this box if the employee has disability and is registered with Council of Persons with Disability and has a certificate of exemption from commissioner of Domestic Taxes")
    disability_rate = fields.Float(
        'Disability Exempt Amount',
        digits='Account',
        help="For Persons with Disability, First KShs 150,000 pm is exempt from tax. Here, you can record expenses related to personal care and home care allowable up to a maximum of KShs 50,000 per month.")
    disability_cert = fields.Char(
        'Disability Cert No',
        help="Persons with Disability must apply for certificate of exemption from Commissioner of Domestic Taxes. Cetificate is issued within 30 days and is valid for 3 years")
    hosp = fields.Boolean(
        'H.O.S.P Deposit?',
        default=False,
        help='Check this box if the employee is making monthly deposits in respect of funds deposited in “approved Institution” under "Registered Home Ownership Savings Plan". Such Employee is eligible to a deduction up to a maximum of Kshs. 4,000 /- (Four thousand shillings) per month or Kshs. 48,000/- per annum ')
    hosp_deposit = fields.Float(
        'Actual Deposit to H.O.S.P (Monthly):', digits=(32, 2))
    mortgage = fields.Boolean(
        'Owner Occupied Interest (O.C.I)?',
        default=False,
        help="Check this box if the employee is paying any interest on load borrowed to finance the purchase or improvement of his or her own house which is occupying.The amount of interest allowable under the law to be deducted from taxable pay must not exceed Kshs.150,000 per year (equivalent to Kshs. 12,500 per month). ")
    mortgage_interest = fields.Float(
        'Actual Interest paid (Monthly):', digits=(32, 2))
    pension = fields.Boolean(
        'Personal Pension/Providend Fund Scheme?',
        default=False,
        help="Check this box if the employee is registered to a personal pension or provident fund scheme.Contribution to any registered defined benefit fund or defined contribution fund is an admissible deduction in arriving at the employee's taxable pay of the month")
    pen_contrib = fields.Float(
        'Actual Pension Contribution  (Monthly):', digits=(
            32, 2))
    resident = fields.Boolean(
        'Resident?',
        default=True,
        help="Check this box if the employee is a resident in Kenya. Such inviduals are entitled to a personal tax relief of Kshs. 1,162 per month and insurance relief if any")
    emp_type = fields.Selection(
        [('primary', 'Primary Employee'),
         ('secondary', 'Secondary Employee')],
        default='primary', required=True, string="Type of Employee:",
        help='[primary] - Select this option of this is the primary employment for the employee\n [Secodary] -Select tis option if this is the secondary employment for the employee.\n Default case is [primary] ')
    director = fields.Boolean(
        'Employee is a Director?',
        default=False,
        help='Check this box if the employee is a director of the Company')
    director_type = fields.Selection([("full",
                                       "Full Time Service Director"),
                                      ("nonfull",
                                       "Non Full Time Service Director")],
                                     string="Director Type")
    global_income = fields.Float(
        'Global Income (Non Full Time Director):', digits=(32, 2),
        help="Please record the Global Income of a Non Full time Service director. This amount will be used in computing the taxable pay as per the law")

    def compute_deductions(self, payslip, rule):
        for rec in self:
            user_tz = self.env.context.get('tz') or 'UTC'
            local_tz = timezone(user_tz)
            deductions = rec.deductions
            _logger.error(f"deductions: {deductions}")
            recurring_domain = [
                ('date_end', '=', None),
                ('is_permanent', '=', True),
                ('rule_id', '=', rule.id),
                ('employee_id', 'in', rec.ids)
            ]

            recurring_deductions = deductions.search(recurring_domain).filtered(
                lambda m: m.date_start.astimezone(
                    local_tz).date() <= payslip.date_to
            )

            _logger.error(f"recurring deductions: {recurring_deductions}")

            # For non-recurring deductions
            non_recurring_domain = [
                ('is_permanent', '=', False),
                ('rule_id', '=', rule.id),
                ('employee_id', 'in', rec.ids)
            ]
            non_recurring_deductions = []
            if non_recurring_domain:
                non_recurring_deductions = deductions.search(
                    non_recurring_domain).filtered(
                    lambda m: m.date_start.astimezone(
                        local_tz).date() <= payslip.date_to and
                              m.date_end.astimezone(
                                  local_tz).date() >= payslip.date_from
                )
            all_deductions = recurring_deductions + non_recurring_deductions

            _logger.error(f"all deductions: {all_deductions}")

            return sum(all_deductions.mapped('amount'))

    def compute_before_gross_deductions(self, payslip, rule):
        for rec in self:
            user_tz = self.env.context.get('tz') or 'UTC'
            local_tz = timezone(user_tz)
            before_gross = rec.before_gross_deductions

            payslip_start_dt = datetime.combine(payslip.date_from,
                                                datetime.min.time()).replace(
                tzinfo=local_tz)
            payslip_end_dt = datetime.combine(payslip.date_to,
                                              datetime.min.time()).replace(
                tzinfo=local_tz)

            recurring_domain = [
                ('is_permanent', '=', True),
                ('rule_id', '=', rule.id),
                ('employee_id', 'in', rec.ids)
            ]

            recurring_deductions = before_gross.search(
                recurring_domain).filtered(
                lambda m: m.date_start.astimezone(
                    local_tz).date() <= payslip.date_to
            )

            # For non-recurring deductions
            non_recurring_domain = [
                ('is_permanent', '=', False),
                ('rule_id', '=', rule.id),
                ('employee_id', 'in', rec.ids)
            ]
            non_recurring_deductions = []

            if non_recurring_domain:
                non_recurring_deductions = before_gross.search(
                    non_recurring_domain).filtered(
                    lambda m: m.date_start.astimezone(
                        local_tz).date() <= payslip.date_to and
                              m.date_end.astimezone(
                                  local_tz).date() >= payslip.date_from
                )

            all_deductions = recurring_deductions + non_recurring_deductions

            return sum(all_deductions.mapped('amount'))


class KEContract(models.Model):
    _inherit = ["hr.contract"]

    @api.constrains('wage')
    def ke_validate_values(self):
        if self.wage < 0:
            raise ValidationError(
                "Only Positive value is accepted for salary or wage")

    benefits = fields.One2many(
        'ke.benefits',
        'contract_id',
        'Benefits',
        help="These are all non cash benefits other than Housing and Car benefit that are entitled to your employee and are taxable by Kenyan Law. These includes, Eletricity, water, Telephone, servants..etc.Such benefits amounting to KES 3000/- and above are taxable")
    cash_allowances = fields.One2many(
        'ke.cash_allowances',
        'contract_id',
        'Cash Allowances',
        help='These are all cash allowances that are taxable as per kenyan law. These incluses overtime allowances, leave alllowances,transport allowances,house allowances, directors fee, lump sum pay, etc..')
    house = fields.Boolean(
        'Housing Benefit ?', default=False,
        help="Check this box if your employee is entitled to housing by employer. Such benefit is taxable")
    house_type = fields.Selection(
        [("own", "Employer's Owned House"),
         ("rented", "Employer's Rented House"),
         ("agric", "Agriculture Farm"),
         ("director", "House to Non full time service Director")])
    rent = fields.Float(
        'Rent of House/Market Value', digits=(32, 2),
        help="This the actual rent of house paid by the employer if the house is rented by employer on behalf of the employee. If the House is owned by the Employer, then this is the Market value of the rent of the house.")
    rent_recovered = fields.Float('Rent Recovered from Employee:', digits=(
        32, 2),
                                  help="This is the actual rent recovered from the employee if any")
    car = fields.Boolean('Car Benefit:', default=False,
                         help="Check this box if the employee is provided with a motor vehicle by employer. the chargeable benefit for private use shall be the higher of the rate determined by the Commissioner of taxes and the prescribed rate of benefit. Where such vehicle is hired or leased from third party, employees shall be deemed to have received a benefit in that year of income, equal to the cost of hiring or leasing")
    cars = fields.One2many(
        'ke.cars',
        'contract_id',
        'Car Benefits',
        help="This is a record of cars provided to the employee by the employer for personal use. The taxable value of this benefit is computed here as per the prescribed rates in the law")


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    nhif = fields.Char(
        'NHIF No.',
        help="Fill in the NHIF number issued by National Hospital Insurance Fund. For those employees in the formal sector, it is compulsory to be a member.")
    nssf_vol = fields.Boolean(
        'NSSF Voluntary Contributions?',
        default=False,
        help="Check this box if the employee or employer or both are is willing to contribute voluntarily to NSSF Scheme.The amount will be a voluntary top up by either employee or employer over and above the mandatory tier I and tier II contributions")
    nssf_t3 = fields.Boolean(
        'NSSF Tier III Contributions?', default=False,
        help="This is for pension contributions above the mandatory amount defined in the NSSF Act 2013.The exact figure will vary from employer to employer")
    nssf_vol_mem = fields.Float(
        'Voluntary Member Amount',
        digits='Account')
    nssf_vol_emp = fields.Float(
        'Voluntary Employer Amount',
        digits='Account')
    nssf_t3_emp = fields.Float(
        'Tier III Employer Amount',
        digits='Account')
    nssf_t3_mem = fields.Float(
        'Tier III Member Amount',
        digits='Account')
    nssf = fields.Char(
        'NSSF No.',
        help="key in the Employee NSSF number. It is mandatory to register as a memmber of NSSF as an employee")
    helb = fields.Boolean(
        'HELB Loan ?', default=False,
        help="Check this box if the employee is currently paying for Higher Education Loans Board Loan")
    helb_rate = fields.Float(
        'HELB Monthly Amount',
        digits='Account',
        help="HELB will issue Loan payment instructions for your employee upon contacting them. Upon the employment of any loanee, you need to inform the Board in writing within a period of three months of such employment. Fill in the monthly figure advised by HELB.")
    tax_pin = fields.Char(
        'KRA PIN',
        help="Key in the 11 charater PIN of the employee, It is mandatory to have a PIN as a tax payer")
    # Others
    # birth_country = fields.Many2one('res.country', 'Country of Birth')
    employee_no = fields.Char(
        'Internal Number',
        help="This is a unique number assigned to each employee internally in the DB. If you do not set the payroll number, this number will be used as the payroll number")
    payroll_no = fields.Char(
        'Payroll Number',
        help="a unique number assigned to each employee to be used in payroll")
    personal_email = fields.Char(
        'Personal Email',
        help="Personal Email that can be used to reach the employee before or after employment")
    # disability Tax Exemption
    disability = fields.Boolean(
        'Employee has disability ?',
        default=False,
        help="Check this box if the employee has disability and is registered with Council of Persons with Disability and has a certificate of exemption from commissioner of Domestic Taxes")
    disability_rate = fields.Float(
        'Disability Exempt Amount',
        digits='Account',
        help="For Persons with Disability, First KShs 150,000 pm is exempt from tax. Here, you can record expenses related to personal care and home care allowable up to a maximum of KShs 50,000 per month.")
    disability_cert = fields.Char(
        'Disability Cert No',
        help="Persons with Disability must apply for certificate of exemption from Commissioner of Domestic Taxes. Cetificate is issued within 30 days and is valid for 3 years")
    hosp = fields.Boolean(
        'H.O.S.P Deposit?',
        default=False,
        help='Check this box if the employee is making monthly deposits in respect of funds deposited in “approved Institution” under "Registered Home Ownership Savings Plan". Such Employee is eligible to a deduction up to a maximum of Kshs. 4,000 /- (Four thousand shillings) per month or Kshs. 48,000/- per annum ')
    hosp_deposit = fields.Float(
        'Actual Deposit to H.O.S.P (Monthly):', digits=(32, 2))
    mortgage = fields.Boolean(
        'Owner Occupied Interest (O.C.I)?',
        default=False,
        help="Check this box if the employee is paying any interest on load borrowed to finance the purchase or improvement of his or her own house which is occupying.The amount of interest allowable under the law to be deducted from taxable pay must not exceed Kshs.150,000 per year (equivalent to Kshs. 12,500 per month). ")
    mortgage_interest = fields.Float(
        'Actual Interest paid (Monthly):', digits=(32, 2))
    pension = fields.Boolean(
        'Personal Pension/Providend Fund Scheme?',
        default=False,
        help="Check this box if the employee is registered to a personal pension or provident fund scheme.Contribution to any registered defined benefit fund or defined contribution fund is an admissible deduction in arriving at the employee's taxable pay of the month")
    pen_contrib = fields.Float(
        'Actual Pension Contribution  (Monthly):', digits=(
            32, 2))
    resident = fields.Boolean(
        'Resident?',
        default=True,
        help="Check this box if the employee is a resident in Kenya. Such inviduals are entitled to a personal tax relief of Kshs. 1,162 per month and insurance relief if any")
    emp_type = fields.Selection(
        [('primary', 'Primary Employee'),
         ('secondary', 'Secondary Employee')],
        default='primary', required=True, string="Type of Employee:",
        help='[primary] - Select this option of this is the primary employment for the employee\n [Secodary] -Select tis option if this is the secondary employment for the employee.\n Default case is [primary] ')
    director = fields.Boolean(
        'Employee is a Director?',
        default=False,
        help='Check this box if the employee is a director of the Company')
    director_type = fields.Selection([("full",
                                       "Full Time Service Director"),
                                      ("nonfull",
                                       "Non Full Time Service Director")],
                                     string="Director Type")
    global_income = fields.Float(
        'Global Income (Non Full Time Director):', digits=(32, 2),
        help="Please record the Global Income of a Non Full time Service director. This amount will be used in computing the taxable pay as per the law")
