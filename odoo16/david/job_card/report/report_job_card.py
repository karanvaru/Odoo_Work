
# -*- coding: utf-8 -*-

import time
#from openerp import api, fields, models
from odoo import api, fields, models


class ReportJobCard(models.AbstractModel):
    _name = 'report.job_card.job_card_report_template'
    _description = 'Report Job Card Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'doc_id': data['id'],
            'doc_ids': data['line_ids'],
            'doc_model': 'account.analytic.line',
            'docs': self.env['account.analytic.line'].browse(data['line_ids']),
            'data': data,
            'report_type': data['report_type']
        }
        if data['report_type'] == 'dailay_report':
            docargs.update({
                'date': data['date'],
                'report_name': 'Timesheet Report'
            })
        if data['report_type'] == 'project_report':
            docargs.update({
                'project_name': data['project_name'],
                'report_name': 'Project Report'
            })
        if data['report_type'] == 'employee_report':
            docargs.update({
                'start_date': data['start_date'],
                'end_date': data['end_date'],
                'leader_name': data['leader_name'],
                'report_name': 'Employee Report'
            })
        
        return self.env.ref('job_card.job_card_report').report_action(self, data=docargs, config=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
