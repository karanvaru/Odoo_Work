#coding: utf-8

import calendar

from calendar import monthrange
from calendar import monthcalendar
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import  _, api, fields, models


def _calc_month_day_byday_and_weekday(next_month_day, byday, week_list):
    """
    Method to return month day based on week day and the number of month week
    Zero might be returned only in case the number of week is too big, e.g fith Sunday might not exists

    Args:
     * next_month_day - date.date
     * byday - the number of week in a month [1-4; -1], where 1 is the first week
     * weeklist - the weekday [0-6]

    Returns:
     * integer

    Extra info:
     * 5th and bigger byday is not supported!
    """
    monthcal = monthcalendar(year=next_month_day.year, month=next_month_day.month)
    if byday != -1:
        byday -= 1
    these_days = list(filter(bool, [week_ca[week_list] for week_ca in monthcal]))
    new_day = these_days[byday]
    return new_day


class recurrent_activity_template(models.Model):
    """
    The model to keep information of recurrent activity
    """
    _name = "recurrent.activity.template"
    _description = "Recurrent Activity"

    @api.model
    def _selection_res_reference(self):
        """
        To return available selection values of the document
        """
        self._cr.execute("""
            SELECT model, name
            FROM ir_model
            WHERE is_mail_thread = true AND transient = false
            ORDER BY name
        """)
        return self._cr.fetchall()

    @api.model
    def _return_year_month(self):
        """
        The method to return year months
        """
        month = 1
        months = []
        while month < 13:
            months.append((str(month), calendar.month_name[month]))
            month += 1
        return months

    @api.multi
    @api.depends("res_reference")
    def _compute_res_model_id(self):
        """
        Compute method for res_model_id
        """
        for create_new in self:
            if self.res_reference:
                model_name = self.res_reference._name
                model_id = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
                self.res_model_id = model_id


    name = fields.Char(
        string="Reference",
        required=True,
    )
    res_reference = fields.Reference(
        selection='_selection_res_reference',
        string='Related Document',
        required=True,
    )
    res_model_id = fields.Many2one(
        "ir.model",
        string="Model",
        compute=_compute_res_model_id,
        store=True,
        compute_sudo=True,
    )
    activity_type_id = fields.Many2one(
        'mail.activity.type',
        string='Activity',
        domain="['|', ('res_model_id', '=', False), ('res_model_id', '=', res_model_id)]",
        required=True,
    )
    summary = fields.Char(
        'Summary',
        required=True,
    )
    note = fields.Html('Note')
    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        default=lambda self: self.env.user,
        required=True,
    )
    number_of_days = fields.Integer(
        string="Deadline in x Days",
        help="What is activity deadline in comparison to its creation date",
    )
    last_sent_date = fields.Date(string="Last Activity Date")
    next_sent_date = fields.Date(
        string="Next Activity Date",
        default=fields.Date.today(),
    )
    interval = fields.Integer(
        string="Interval",
        default=1,
    )
    periodicity = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)')
        ],
        string="Repeat Every",
        default="monthly",
    )
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection(
        [
            ('the_first_date', 'The first day'),
            ('the_last_date', 'The last day'),
            ('date', 'Date of month'),
            ('day', 'Day of month')
        ],
        string='Option',
        default='date',
    )
    day = fields.Integer('Date of month', default=1)
    year_day = fields.Integer('Date of Month', default=1)
    year_month = fields.Selection(
        _return_year_month,
        string="Month",
        default="1",
    )
    week_list = fields.Selection(
        [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday')
        ],
        string='Weekday',
    )
    byday = fields.Selection(
        [
            ('1', 'First'),
            ('2', 'Second'),
            ('3', 'Third'),
            ('4', 'Fourth'),
            ('-1', 'Last')
        ],
        string='By day',
    )
    the_very_last_date = fields.Date(
        "To Archive Date",
        help="The date after which this rule will be archived and no more recurrent activities will be created",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        ('interval_check', 'check (interval>0)', _('Repeat interval should be positive!')),
    ]

    @api.multi
    def _calc_the_next_sent_date(self):
        """
        Method to find the next date by the setting
         1. We are from today not from the last_sent_date not to make excess repeats
         2. Althoug the period is weekly, it might be this week by days. If the days are not define, it just a week dif
         3. In case a day is not found (e.g. 30th in February, we get the last month day)

        Returns:
         * date.date()

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        periodicity = self.periodicity
        interval = self.interval
        # 1
        today = fields.Date.from_string(fields.Date.today())
        res_date = False
        if periodicity == "daily":
            res_date = today + relativedelta(days=interval)
        elif periodicity == "weekly":
            current_week_day = today.weekday()
            wd_ids = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            time_delta = 7 * interval
            # 2
            for wd in wd_ids[current_week_day+1:7]:
                # Firstly search in this week days
                if self[wd]:
                    time_delta = wd_ids.index(wd) - current_week_day
                    break
            if time_delta == 7 * interval:
                # Then search in the next week
                for wd in wd_ids[0:current_week_day]:
                    if self[wd]:
                        time_delta = (7 * interval) + (wd_ids.index(wd) - current_week_day)
                        break
            # if no other days, just go to the next interval
            res_date = today + relativedelta(days=time_delta)
        elif periodicity == "monthly":
            month_by = self.month_by
            next_month_day = today + relativedelta(months=interval)
            first_month_date = date(
                year=next_month_day.year,
                month=next_month_day.month,
                day=1
            )
            last_month_date = date(
                year=next_month_day.year,
                month=next_month_day.month,
                day=monthrange(next_month_day.year, next_month_day.month)[1],
            )
            if month_by in ["the_first_date"]:
                res_date = first_month_date
            elif month_by in ["the_last_date"]:
                res_date = last_month_date
            elif month_by in ["day"]:
                byday = int(self.byday)
                week_list = int(self.week_list)
                new_day = _calc_month_day_byday_and_weekday(
                    next_month_day=next_month_day,
                    byday=byday,
                    week_list=week_list,
                )
                res_date = date(
                    year=next_month_day.year,
                    month=next_month_day.month,
                    day=new_day,
                )
            elif month_by in ["date"]:
                # 3
                try:
                    res_date = date(
                        year=next_month_day.year,
                        month=next_month_day.month,
                        day=self.day,
                    )
                except:
                    next_month_day = last_month_date
        elif periodicity == "yearly":
            the_next_year_day = today + relativedelta(years=interval)
            try:
                res_date = date(
                    year=the_next_year_day.year,
                    month=int(self.year_month),
                    day=self.year_day,
                )
            except:
                res_date = date(
                    year=the_next_year_day.year,
                    month=int(self.year_month),
                    day=monthrange(the_next_year_day.year, int(self.year_month))[1],
                )
        if self.the_very_last_date and res_date > self.the_very_last_date:
            res_date = False
        return res_date

    @api.model
    def return_view_action(self):
        """
        The method to open recurrent activities view

        Returns:
         * dict of ir.actions.window
        """
        action_id = self.env.ref("recurrent_activities.recurrent_activity_template_action").read()[0]
        action_id["views"] = [(False, 'list'), (False, 'form')]
        return action_id

    @api.multi
    def _action_prepare_activity(self):
        """
        The method to create new activity based on this template values

        Methods:
         * _calc_the_next_sent_date
        """
        today = fields.Date.today()
        for activity in self:
            act_vals = {
                "summary": activity.summary,
                "note": activity.note,
                "user_id": activity.user_id.id,
                "activity_type_id": activity.activity_type_id.id,
                "date_deadline": today + relativedelta(days=activity.number_of_days),
                "res_model_id": self.res_model_id.id,
                "res_id": self.res_reference.id,
            }
            self.env["mail.activity"].create(act_vals)
            activity.last_sent_date = today
            next_sent_date = activity._calc_the_next_sent_date()
            activity.next_sent_date = next_sent_date
            if not next_sent_date:
                activity.active = False
                activity.the_very_last_date = False

    @api.model
    def prepare_recurrent_activities(self):
        """
        Method to check all recurrent activities to be made

        Methods:
         * _action_prepare_activity

        Extra info:
         * we are in loop to make commits each time
        """
        today = fields.Date.today()
        to_close_rules = self.search([("the_very_last_date", "<", today)])
        if to_close_rules:
            to_close_rules.write({
                "active": False,
                "next_sent_date": False,
                "the_very_last_date": False,
            })
        recurrent_acts = self.search([
            "|", 
                ("next_sent_date", "<=", today), 
                ("next_sent_date", "=", False),

        ])
        for activity in recurrent_acts:
            activity._action_prepare_activity()
            self.env.cr.commit()
