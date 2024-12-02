from odoo import models, fields, api,_
from datetime import datetime
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import *



class TATandSLA(models.Model):
    _name = 'tat.sla'
    _discription = "TAT SLA"

    name = fields.Char('Name')
    ticket_id = fields.Many2one('helpdesk.ticket')
    stage_id = fields.Many2one('helpdesk.stage')

    from_stage_id = fields.Many2one('helpdesk.stage')
    to_stage_id = fields.Many2one('helpdesk.stage')
    current_stage_id =fields.Many2one('helpdesk.stage')

    date_in = fields.Datetime(defaul=fields.datetime.today().replace(day=16))
    date_out = fields.Datetime()
    days = fields.Char('Open Days',compute="_compute_days",store=True)
    from_team_id = fields.Many2one('helpdesk.team','From Team')
    to_team_id = fields.Many2one('helpdesk.team','To Team')
    sla_days = fields.Char('SLA Days')
    sla_days_time = fields.Float('SLA Days Time',compute="_compute_sla_days")
    description = fields.Text(string='Description')
    duration = fields.Float(
        string='Duration',
        # compute="_compute_duration",
        store=True
    )
    timer_status = fields.Selection(
        [
            ('on', 'on'),
            ('off', 'off'),

        ],
        string="Status", default='on')
    is_active = fields.Boolean('Active', default=True)

    #tat_status = fields.Char('TAT Status',compute="_compute_tat_status")
    tat_status = fields.Selection(
        selection=[('new', 'New') ,('pass', 'Pass'), ('fail', 'Fail')],
        string='TAT Status',
        compute="_compute_tat_status",
        default='new',
        store=True
    )

    tat_time = fields.Integer('TAT Time')#compute='compute_tat_time'
    tat_name = fields.Char('TAT Name', compute='compute_tat_time_value',store=True)
    tat_time_value = fields.Char('TAT Time value', compute='compute_tat_time_value')
    current_user = fields.Char('User',default=lambda self: self.env.user.name,readonly="1")
    # tat_id = fields.Many2one('helpdesk.ticket.tat',"TAT ID")
    tat_id = fields.Many2one('tat.config',"TAT ID")
    tat_value =fields.Integer('TAT Value',)#compute="compute_tat_value")
    sla_id = fields.Many2one('helpdesk.sla','SLA Policy ID')

    # def compute_tat_value(self):
    #     for rec in self:
    #         tav_min_val = rec.date_out -rec.date_in
    #         rec.tat_value = tav_min_val

    @api.depends('ticket_id.team_id','name')
    def compute_tat_time_value(self):
        for rec in self:
            tat_val = rec.env['tat.config'].search([
                ('team_id', '=', rec.ticket_id.team_id.id),
                ('stage_id', '=', rec.to_stage_id.id)
            ])
            for tt in tat_val:
                rec.tat_name = tt.name
                tat_time_line_value = '{} days {} hour {} minites'.format(tt.time_days, tt.time_hours, tt.time_minutes)
                rec.tat_time_value = tat_time_line_value





    def action_stop_time(self):
        # user = self.env.user.name
        # if (user != self.current_user) and not self.env.user._is_admin():
        #     raise ValidationError(
        #         _('You can not do other users operations!')
        #     )
        self.timer_status ='off'
        return True


    # @api.depends('ticket_id.team_id')
    # def compute_tat_time(self):
    #     for rec in self:
    #         tat_val = rec.env['tat.config'].search([('team_id','=',rec.ticket_id.team_id.id)])
    #         tat_vall = rec.env['tat.config'].search([('team_id','=',rec.from_team_id.id)])
    #         for tt in tat_val:
    #             rec.tat_time = tt.tat_value
    #         # if rec.from_team_id.id and rec.to_team_id.id == rec.ticket_id.team_id.id:
    #         #     rec.tat_time = tt.tat_value
    #         else:
    #             for t1 in tat_vall:
    #                 rec.tat_time = t1.tat_value


    @api.depends('date_in', 'date_out', 'tat_id')
    def _compute_days(self):
        for res in self:
            if res.date_in and res.date_out:
                if res.date_out:
                    if res.tat_id and res.tat_id.resource_calendar_id:
                        start_dt=res.date_in
                        end_dt=res.date_out
                        result = res.tat_id.resource_calendar_id.get_work_hours_count(
                            start_dt,
                            end_dt,
                            compute_leaves=True,
                        )
                        seconds = result * 60 * 60
                        minutes, seconds = divmod(seconds, 60)
                        hours, minutes = divmod(minutes, 60)
                        res.days  = "%02d:%02d:%02d"%(hours,minutes,seconds)
                    else:
                        res.days = str(((res.date_out - res.date_in))).split('.')[0]


    @api.depends('date_in', 'date_out', 'tat_id')
    def _compute_sla_days(self):
        for res in self:
            if res.date_in and res.date_out:
                res.sla_days = str(((res.date_out - res.date_in).total_seconds())/60).split('.')[0]
                if res.tat_id and res.tat_id.resource_calendar_id:
                    start_dt = res.date_in
                    end_dt = res.date_out
                    result = res.tat_id.resource_calendar_id.get_work_hours_count(
                        start_dt,
                        end_dt,
                        compute_leaves=True,
                    )
                    seconds = result * 60 * 60
                    minutes, seconds = divmod(seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    res.sla_days_time = result * 60#result#"%02d:%02d:%02d" % (hours, minutes, seconds)

            else:
                if res.date_in:
                    res.sla_days_time = ((datetime.today() - res.date_in).total_seconds())/60
                else:
                    res.sla_days_time = 0



    @api.multi
    @api.depends("date_out", "date_in")
    def _compute_tat_status(self):
        for rec in self:
            if rec.to_stage_id:
                day = rec.tat_id.time_days * 24 * 60
                hour = rec.tat_id.time_hours * 60
                minutes = rec.tat_id.time_minutes
                t_status = day + hour + minutes
                if not rec.date_out and rec.sla_days_time > int(t_status):
                    rec.tat_status = "fail"
                elif rec.date_out:
                    if rec.sla_days_time <= t_status:
                        rec.tat_status = "pass"
                    else:
                        rec.tat_status = "fail"
                else:
                    rec.tat_status = "new"

