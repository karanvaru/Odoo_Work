from odoo import api, fields, models, _
from datetime import datetime


class EmployeeAppraisalInherited(models.Model):
    _inherit = "employee.appraisal"

    spoc_id = fields.Many2one("hr.employee", 'SPOC', compute='compute_employee',store=True)
    difficulty_level = fields.Selection([
        ('easy', 'Easy'),
        ('normal', 'Normal'),
        ('difficult', ' Difficult'),
        ('hard', 'Hard'),
        ('extreme', 'Extreme'),
        ('insane', 'Insane')
    ], string='Difficulty Level')
    category = fields.Selection([
    ('learning', 'Learning'),
    ('discovery', 'Discovery'),
    ('invention', ' Invention'),
    ('experiment_failed', 'Experiment Failed'),
    ('process_improvement', 'Process Improvement'),
    ('process_execution', 'Process Execution'),
    ('strategy_presentation', 'Strategy Presentation'),
    ('out_of_the_box_work', 'Out-Of-The Box Work'),
    ('jugaad', 'Jugaad'),
    ('training_given', 'Training_Given'),
    ('customer_appreciation', 'Customer Appreciation'),
    ('kra_kpi_accomplishment', 'KRA/KPI Accomplishment'),
    ('self_satisfaction', 'Self Satisfaction'),
    ('task_accomplishment', 'Task Accomplishment'),
    ('project_accomplishment', 'Project Accomplishment'),
    ('decision_making', 'Decision_Making'),
    ('soft_skills_accomplishment', 'Soft Skills Accomplishment'),
    ('helping_hand_in_your_society', 'Helping Hand In Your Society'),
    ('sports_games', 'Sports/Games'),
    ('personal_accomplishment', 'Personal Accomplishment'),
    ('others', 'Others')], string='Category')

    sa_story_name = fields.Char(string='Sa Story Name')
    open_days = fields.Char(compute='_compute_open_days', string='Open Days')
    closed_date = fields.Datetime(string='closed date')

    @api.depends('employee_name')
    def compute_employee(self):
        for rec in self:
            print("The current user id ", rec.env.uid)
            rec_spoc_id = rec.env['hr.employee'].sudo().search([('user_id', '=', rec.env.uid)])
            rec.spoc_id = rec_spoc_id.coach_id.id
            print("spoc_id", rec_spoc_id.coach_id.id)
            rec.spoc_id = rec_spoc_id.coach_id.id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.appraisal.sequence')
        res = super(EmployeeAppraisalInherited, self).create(vals)
        template_id = \
            self.env['ir.model.data'].get_object_reference('rdp_employee_appraisal_inherited',
                                                           'hr_self_appraisal_app_employee_notification')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)

        template_id = \
            self.env['ir.model.data'].get_object_reference('rdp_employee_appraisal_inherited',
                                                           'Here_is_a_template_for_an_automated_email_that_can_be_sent_to_an_employee')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)
        return res

    @api.multi
    def action_to_closed(self):
        self.closed_date = datetime.today()
        self.state = 'closed'
        template_id = self.env.ref(
            "rdp_employee_appraisal_inherited.notification_after_ticket_closed")
        print("The template id is ", template_id)
        # template = self.env['mail.template'].browse(template_id)
        template_id.send_mail(self.id, force_send=True)

    # @api.multi
    # def calculate_open_days(self):
    #     for rec in self:
    #         if rec.closed_date:
    #             rec.open_days = (rec.closed_date - rec.create_date).days
    #         else:
    #             rec.open_days = (datetime.today() - rec.create_date).days

