from odoo import Command, api, fields, models


class ReportAutomationConfig(models.Model):
    _name = "report.automation.config"

    name = fields.Char(
        string="Name"
    )

    action_id = fields.Many2one(
        'ir.cron',
        string="Action"
    )

    email_template_id = fields.Many2one(
        'mail.template',
        string="Mail Template"
    )

    interval_number = fields.Integer(
        default=1,
    )
    interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')],
        string='Interval Unit',
        default='months'
    )
    email_to = fields.Char(
        string='To (Emails)',
    )
    # start_day = fields.Integer(
    #     string="Start Day"
    # )

    nextcall = fields.Datetime(
        string='Next Execution Date',
        default=fields.Datetime.now,
        help="Next planned execution date for this job."
    )

    period_days = fields.Integer(
        string="Contract Expiry In(Days)"
    )

    def write(self, vals):
        super_res = super(ReportAutomationConfig, self).write(vals)
        if 'interval_number' in vals:
            self.action_id.interval_number = self.interval_number
        if 'interval_type' in vals:
            self.action_id.interval_type = self.interval_type
        if 'email_to' in vals:
            self.email_template_id.email_to = self.email_to
        if 'nextcall' in vals:
            self.action_id.nextcall = self.nextcall

        return super_res
