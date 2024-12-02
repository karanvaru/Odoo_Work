from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import time
import logging

_logger = logging.getLogger(__name__)


class EmployeeAutomation(models.Model):
    _inherit = 'hr.employee'

    # _logger = logging.getLogger(__name__)

    def onchange_date_of_joining(self):
        employee_ids = self.env['hr.employee'].search([('active', '=', True)])
        for rec in employee_ids:
            _logger.info("============================Coming In======================= %s", rec.x_studio_joining_date)
            if rec.x_studio_joining_date:
                _logger.info("=================coming inside of if=========================")
                today = datetime.today()
                # today_date = today.strftime("%m/%d/%Y")
                start = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(rec.x_studio_joining_date, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                _logger.info("============================start date===================== %s", start_last)
                _logger.info("============================end date====================== %s", end_last)
                days = (start_last - end_last).days

                if days <= 7:
                    _logger.info("=======================induction========== %s", rec.name)
                    rec.update({'x_studio_field_AZ3Lh': 'induction'})
                    rec.x_studio_field_az3lh = "induction"

                if (days >= 7) and (days <= 30):
                    _logger.info("=======================On Job Training ========== %s", rec.name)
                    rec.update({'x_studio_field_AZ3Lh': 'on_job_training'})
                    rec.x_studio_field_az3lh = "on_job_training"

                if (days >= 30) and (days <= 180):
                    _logger.info("=======================Probation========== %s", rec.name)
                    rec.update({'x_studio_field_AZ3Lh': 'probation'})

                if days > 180:
                    if rec.id == 640:
                        _logger.info("=======================Employment========== %s", rec.name)
                        rec.update({'x_studio_field_AZ3Lh': 'employment'})
                        _logger.info("=======================Employment========== %s", rec.x_studio_field_AZ3Lh)

            # if rec.user_id:
            #     exit = rec.env['hr.exit'].search([('user_id', '=', rec.user_id), ('dept_approved_date', '=', True)])
            #     if exit:
            #         rec.x_studio_field_az3lh = 'serving_np'
            #         end_np = datetime.today() - exit.dept_approved_date
            #         if end_np >= rec.x_studio_notice_period:
            #             rec.x_studio_field_az3lh = 'under_fnf'

    def state_update(self):
        for rec in self:
            rec.state = rec.x_studio_field_AZ3Lh
