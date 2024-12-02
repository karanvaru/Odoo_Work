# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JobCardRport(models.TransientModel):
    _name = 'job.card.report.wizard'
    _description = 'Job Card Report Wizard'


    report_type = fields.Selection(
        [('dailay_report','Daily Report'),
         ('project_report','Project Report'),
         ('employee_report', 'Employee Report')],
        default='dailay_report',
        string='Report Type',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today()
    )
    project_id = fields.Many2many(
        'project.project',
        string="Project"
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today()
    )
    end_date = fields.Date(
        string='End Date',
        default=fields.Date.today()
    )
    employee_id = fields.Many2many(
        'hr.employee',
        string="Employee"
    )

    #@api.multi
    def print_job_card_report(self):
        datas = {'id': self, 'form': self.sudo().read()[0], 'line_ids': [], 'report_type': self.report_type}
        if self.report_type == 'dailay_report' and self.date:
            line_ids = self.env['account.analytic.line'].search([('date', '=', self.date),('task_id.is_jobcard', '=', True)])
            datas.update({
                'date': self.date,
                'line_ids': line_ids.ids,
            })
        if self.report_type == 'project_report' and self.project_id:
            account_ids = []
            project_name = ''
            for r in self.project_id:
                if r.analytic_account_id:
                    account_ids.append(r.analytic_account_id.id)
                if project_name == '':
                    project_name = r.name
                else:
                    project_name = project_name + ' , ' + r.name
            line_ids = self.env['account.analytic.line'].search([('account_id', 'in', account_ids), ('task_id.is_jobcard', '=', True)])
            datas.update({
                'project_name': project_name,
                'line_ids': line_ids.ids,
            })
        if self.report_type == 'employee_report':
            leader_name = ''
            for r in self.employee_id:
                if leader_name == '':
                    leader_name = r.name
                else:
                    leader_name = leader_name + ' , ' + r.name
            line_ids = self.env['account.analytic.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('leader_id', 'in', self.employee_id.ids),
                ('task_id.is_jobcard', '=', True)
            ])
            datas.update({
                'start_date': self.start_date,
                'end_date': self.end_date,
                'leader_name': leader_name,
                'line_ids': line_ids.ids,
                'report_name': 'Employee Report'
            })
        return self.env.ref('job_card.job_card_report').report_action(self, data=datas, config=False)
