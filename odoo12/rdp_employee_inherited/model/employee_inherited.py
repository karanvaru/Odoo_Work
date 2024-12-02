from odoo import models, fields,api


class EmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    pan_number = fields.Char(string='PAN Number')
    bank_name = fields.Many2one('res.bank', string='Bank Name', compute="compute_bank_name", readonly=False)
    personal_email = fields.Char(string="Personal Email")
    joining_date = fields.Date(string='Joining Date')
    intercom_number = fields.Char(string='Intercom Number')
    parent_department_id = fields.Many2one('hr.department',compute="compute_parent_department_id", readonly=False)
    recruiter_id = fields.Many2one('res.users',string='Recruiter',compute='_compute_recruiter_id',readonly=False)

    # <__________________added fields in this model_________pavi____27-03-2023_______________>
    separation_type = fields.Selection([("resigned", "Resigned"),
                                        ("terminated", "Terminated"),
                                        ("absconded", "Absconded")], string='Separation Type')
    notice_period = fields.Selection([
        ('one_month', '30 Days'),
        ('two_month', '60 Days'),
        ('three_month', '90 Days'),
    ], string='Notice Period', required=True)
    ff_status = fields.Selection([("Cleared", "Cleared"), ("Discrepancy", "Discrepancy")], string="F&F Status")
    employment_bond = fields.Selection(
        [("12_months", "12 Months"), ("18_months", "18 Months"), ("24_months", "24 Months"), ("30_months", "30 Months"),
         ("36_months", "36 Months")], string="Employment Bond")
    work_office = fields.Selection([("anantapur", "Anantapur"),
                                    ("hyderabad_Office_1", "Hyderabad Office 1"),
                                    ("hyderabad_Office_2", "Hyderabad Office 2"),
                                    ("hyderabad_Office_3", "Hyderabad Office 3"),
                                    ("property1", "Property 1"),
                                    ("work_from_home", "Work from Home")
                                    ], string="Work Office")
    desk_number = fields.Selection(
        [("2001", "2001"), ("2002", "2002"), ("2003", "2003"), ("2004", "2004"), ("2005", "2005"),
         ("2006", "2006"), ("2007", "2007"), ("2008", "2008"), ("2009", "2009"), ("2010", "2010"),
         ("2011", "2011"), ("2012", "2012"), ("2013", "2013"), ("2014", "2014"), ("2015", "2015"),
         ("2016", "2016"), ("2017", "2017"), ("2018", "2018"), ("2019", "2019"), ("2020", "2020"),
         ("2021", "2021"), ("2022", "2022"), ("2023", "2023"), ("2024", "2024"), ("2024", "2024"),
         ("2025", "2025"), ("2026", "2026"), ("2027", "2027"), ("2028", "2028"), ("2029", "2029"),
         ("2030", "2030"), ("2031", "2031"), ("2032", "2032"), ("2033", "2033"), ("2039", "2039"),
         ("2040", "2040"), ("2041", "2041"), ("2042", "2042"), ("2043", "2043"), ("2044", "2044"),
         ("2045", "2045"), ("2046", "2046"), ("2047", "2047"), ("2048", "2048"), ("2049", "2049"),
         ("2050", "2050"), ("2051", "2051"), ("2052", "2052"), ("2053", "2053"), ("2054", "2054"),
         ("2055", "2055"), ("2056", "2056"), ("2057", "2057"), ("2058", "2058"), ("2059", "2059"),
         ("2060", "2060"), ("2061", "2061"), ("2062", "2062"), ("2063", "2063"), ("2064", "2064"),
         ("2065", "2065"), ("2066", "2066"), ("2067", "2067"), ("2068", "2068"), ("2069", "2069"),
         ("2070", "2070"), ("2071", "2071"), ("2072", "2072"), ("2073", "2073"), ("2074", "2074"),
         ("2075", "2075"), ("2076", "2076"), ("3001", "3001"), ("3002", "3002"), ("3003", "3003"),
         ("3004", "3004"), ("3005", "3005"), ("3006", "3006"), ("3007", "3007"), ("3008", "3008"),
         ("3009", "3009"), ("3010", "3010"), ("3011", "3011"), ("3012", "3012"), ("3013", "3013"),
         ("3014", "3014"), ("3015", "3015"), ("3016", "3016"), ("3017", "3017"), ("3018", "3018"),
         ("3019", "3019"), ("3020", "3020"), ("3021", "3021"), ("3022", "3022"), ("3023", "3023"),
         ("3024", "3024"), ("3025", "3025"), ("3026", "3026"), ("3027", "3027"), ("3028", "3028"),
         ("3029", "3029"), ("3030", "3030"), ("3031", "3031"), ("3032", "3032"), ("3033", "3033"),
         ("3034", "3034"), ("3035", "3035"), ("3036", "3036"), ("3037", "3037"), ("3038", "3038"),
         ("3039", "3039"), ("3040", "3040"), ("3041", "3041"), ("3042", "3042"), ("3043", "3043"),
         ("3044", "3044"),
         ], string="Desk Number")

    hr_payslips_ids = fields.One2many('hr.payslip','hr_employee_id')

    @api.depends('bank_account_id')
    def compute_bank_name(self):
        for rec in self:
            rec.bank_name = rec.bank_account_id.bank_id

    @api.depends('department_id')
    def compute_parent_department_id(self):
        for rec in self:
            rec.parent_department_id = rec.department_id.parent_id


    @api.depends('job_id')
    def _compute_recruiter_id(self):
        for rec in self:
            rec.recruiter_id = rec.job_id.user_id




class PayslipInherited(models.Model):
    _inherit = 'hr.payslip'

    joining_date = fields.Date(string='Joining Date',compute='_compute_joining_date')

    hr_employee_id = fields.Many2one('hr.employee')

    @api.depends('joining_date')
    def _compute_joining_date(self):
        for rec in self:
            rec.joining_date = rec.contract_id.employee_id.joining_date

