from odoo import api, fields, models


class ApplicantInherit(models.Model):
    _inherit = "hr.applicant"

    gender = fields.Selection(
        selection='_get_new_gender',
        string='Gender',
        copy=False
    )

    # agent_id = fields.Many2one(
    #     'res.users',
    #     string="Agent",
    #     readonly=True,
    #     copy=False
    # )
    recruitment_agent_id = fields.Many2one(
        'recruiting.agent',
        string="Agent",
        readonly=True,
        copy=False
    )
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ],
        string="Payment Status:",
        copy=False,
        default='unpaid'
    )

    @api.model
    def _get_new_gender(self):
        selection = [
            ('male', 'Male'),
            ('female', 'Female'),
        ]
        return selection

    def mark_as_paid(self):
        self.update({
            'payment_status': 'paid'
        })

    ############# Trades Assessment Questionnaire  #############

    age = fields.Integer(
        string="Age",
        copy=False
    )
    country_of_nationality = fields.Many2one(
        'res.country',
        string="Nationality",
        tracking=True,
        copy=False
    )
    citizenship = fields.Char(
        string="Citizenship",
        copy=False
    )
    middle_name = fields.Char(
        "Middle Name"
    )

    most_work_experience = fields.Char(
        copy=False,
        string='In what trade do you have the most work experience:'
    )
    number_years_in_trade = fields.Char(
        copy=False,
        string='Number years in this trade:'
    )
    hours_work_per_day = fields.Char(
        copy=False,
        string='How many hours worked in this trade per day:'
    )
    days_work_per_week = fields.Char(
        copy=False,
        string='How many days worked in this trade per week:'
    )
    weeks_per_month = fields.Char(
        copy=False,
        string='How many weeks worked in this trade per month:'
    )
    month_per_year = fields.Char(
        copy=False,
        string='How many months worked in this trade per year:'
    )
    year_per_5_10_year = fields.Char(
        copy=False,
        string='How many years worked in this trade in the last 5 to 10 years:'
    )
    describe_detail = fields.Char(
        copy=False,
        string='Describe in detail ALL the tasks performed on a daily basis within this trade (Maximum words 500)-: '
    )
    complete_high_school_year = fields.Char(
        copy=False,
        string='How many years did you complete in high school:'
    )
    is_training = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Do you have any training in this trade:",
        copy=False
    )
    is_other_trade_skill = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Are you skilled in any other trades:",
        copy=False
    )
    varify_experience = fields.Selection(
        [('employer', 'Employer'),
         ('supervisor', 'Supervisor'),
         ('customer_clients', 'Customer/Clients'),
         ],
        string=" Who can verify your work experience under this trade: ",
        copy=False
    )
    is_complete_high_school = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Have you completed high school?:",
        copy=False
    )
    is_criminal_offence = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Have you ever been arrested or charged for any criminal offence?:",
        copy=False
    )
    is_applied_visa = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Have you ever applied for a Canadian or US visa:",
        copy=False
    )
    travelled_by_plane = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Have you ever travelled by plane to any country outside your home country?:",
        copy=False
    )
    is_denied_visa = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Have you ever been denied a visa?:",
        copy=False
    )

    ############# Trades Assessment Report  #############

    education_level = fields.Selection(
        [('high_school', 'High School'),
         ('college', 'College'),
         ('university', 'University'),
         ],
        string="Education Level: ",
        copy=False
    )
    trade_applied = fields.Char(
        copy=False,
        string='Trade applied under:'
    )
    report_no_year = fields.Char(
        copy=False,
        string='Number years in this Trade:'
    )
    report_hour_per_day = fields.Char(
        copy=False,
        string='How many hours worked in this trade per day:'
    )
    report_day_per_week = fields.Char(
        copy=False,
        string='How many days worked in this trade per week:'
    )
    report_week_per_month = fields.Char(
        copy=False,
        string='How many weeks worked in this trade per month:'
    )
    report_month_per_year = fields.Char(
        copy=False,
        string='How many months worked in this trade per year:'
    )
    year_work5_10 = fields.Char(
        copy=False,
        string='How many years worked in this trade in the last 5 to 10 years:'
    )
    report_is_training = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Training in this trade:",
        copy=False
    )
    report_is_skill = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Skilled in any other trades:",
        copy=False
    )
    is_red_seal = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
        string="Does the Applicant trade tasks meet the NOC Code and Red Seal task description:",
        copy=False
    )
    is_applicant_eligible = fields.Char(
        copy=False,
        string='Is the applicant eligible to proceed to RED SEAL Trades Qualifier and Training?:'
    )
    recommendations = fields.Text(
        copy=False,
        string='Additional Recommendations For Trades Qualifier Assessment:'
    )

    ############# Additional Recommendations for Trades Qualifier Assessment  #############

    application_document_ids = fields.One2many(
        'application.document',
        'hr_applicant_id'
    )

    def _get_employee_create_vals(self):
        res = super(ApplicantInherit, self)._get_employee_create_vals()
        res.update({
            'gender': self.gender,
            'country_id': self.country_of_nationality.id,
            'birthday': self.birthday,
            'description': self.description,
        })
        return res
