# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class mail_activity_todo(models.TransientModel):
    """
    The model to combine activities in a single to-do list
    """
    _name = 'mail.activity.todo'
    _description = 'To-Do Activities'

    @api.model
    def _selection_res_reference(self):
        """
        To return available selection values of the document
        """
        self._cr.execute("SELECT model, name FROM ir_model ORDER BY name")
        return self._cr.fetchall()

    @api.multi
    @api.depends("current_number", "total_number", "activities")
    def _compute_progress(self):
        """
        Compute method for progress
        """
        for todo in self:
            activities = safe_eval(todo.activities)
            done_number = len([act["activity_id"] for act in activities if act["state"] == "done"])
            todo.done_number = done_number
            if todo.total_number:
                progress = todo.total_number and done_number * 100 / todo.total_number
            else:
                progress = 100.0
            if progress == 100.0:
                todo.current_activity_id = False
            else:
                all_acts = [act["activity_id"] for act in activities if act["number"] == self.current_number]
                todo.current_activity_id = all_acts and all_acts[0] or False
            todo.progress = progress

    @api.multi
    @api.depends('current_activity_id')
    def _compute_res_reference(self):
        """
        Compute method for res_reference

        We need a real id of a parent object (in case of virtual id we get to the parent one)
        """
        for todo in self:
            current_activity = todo.current_activity_id
            if current_activity and current_activity.res_id and current_activity.res_model:
                todo.res_reference = '{},{}'.format(current_activity.res_model, current_activity.res_id)
            else:
                todo.res_reference = False

    activities = fields.Char(string="Activities")
    current_activity_id = fields.Many2one(
        "mail.activity",
        string="Current activity",
        compute=_compute_progress,
    )
    progress = fields.Float(
        string="Progress",
        compute=_compute_progress,
    )
    current_number = fields.Integer(string="Number")
    total_number = fields.Integer(string="Total")
    done_number = fields.Integer(
        string="Done",
        compute=_compute_progress,
        store=True,
    )
    res_reference = fields.Reference(
        selection='_selection_res_reference',
        string='Document',
        compute=_compute_res_reference,
        compute_sudo=True,
    )
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        related="current_activity_id.activity_type_id"
    )
    summary = fields.Char(related="current_activity_id.summary")
    note = fields.Html(related="current_activity_id.note")
    date_deadline = fields.Date(related="current_activity_id.date_deadline")

    @api.multi
    def name_get(self):
        """
        Overloading the method to pass some proper name
        """
        result = []
        today = fields.Date.today()
        for todo in self:
            name = u"Activities To-Do #{}".format(today)
            result.append((todo.id, name))
        return result

    @api.model
    def start_todo(self):
        """
        The method to start to-do by current activities

        Returns:
         * dict of ir.actions.window
        """
        user = self.env.user
        domain = [("user_id", "=", user.id)]
        if user.act_type_ids:
            domain.append(("activity_type_id", "in", user.act_type_ids.ids))
        if user.only_old_activities:
            domain.append(("date_deadline", "<=", fields.Date.today()))

        activity_ids = self.env["mail.activity"].search(domain, order="date_deadline, id")
        if activity_ids:
            act_ids = []
            itera = 0
            for activity in activity_ids:
                act_ids.append({
                    "activity_id": activity.id,
                    "number": itera,
                    "state": "to_do",
                })
                itera += 1
            todo_id = self.create({
                "activities": act_ids,
                "current_number": 0,
                "total_number": len(act_ids),
                "done_number": 0,
            })
            action = self.env.ref("activities_todo.mail_activity_todo_action").read()[0]
            action["res_id"] = todo_id.id
        else:
            raise UserError(_("There are no activities to process"))
        return action

    @api.multi
    def _get_next_todo(self):
        """
        The method to get the next record in a row

        Methods:
         * _check_and_update_activities

        Returns:
         * number - int or False

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        activities = self._check_and_update_activities()
        number = False
        for act in activities:
            if act["state"] == "to_do" and act["number"] > self.current_number:
                number = act["number"]
                break
        if not number and self.progress != 100:
            for act in activities:
                if act["state"] == "to_do":
                    number = act["number"]
                    break
        return number

    @api.multi
    def _get_previous_todo(self):
        """
        The method to get the previous record in a row

        Methods:
         * _check_and_update_activities

        Returns:
         * number - int or False

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        activities = self._check_and_update_activities()
        activities = list(reversed(activities))
        number = False
        for act in activities:
            if act["state"] == "to_do" and act["number"] < self.current_number:
                number = act["number"]
                break
        if not number and self.progress != 100:
            for act in activities:
                if act["state"] == "to_do":
                    number = act["number"]
                    break
        return number

    @api.multi
    def _check_and_update_activities(self):
        """
        The method to update activities state, since activity might be done / cancelled separately

        Returns:
         * activities list

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        activities = safe_eval(self.activities)
        for act in activities:
            if act["state"] == "to_do" and not self.env["mail.activity"].browse(act["activity_id"]).exists():
                act["state"] = "done"
        self.activities = activities
        return activities

    @api.multi
    def action_done(self):
        """
        The method to mark activity as done and pass to the next one

        Methods:
         * action_feedback of mail.activity
         * action_skip

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if self.current_activity_id:
            self.current_activity_id.action_feedback()
        self.action_skip()

    @api.multi
    def action_cancel(self):
        """
        The method to cancel activity and pass to the next

        Methods:
         * unlink of mail.activity
         * _get_next_todo

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        self.current_activity_id.unlink()
        self.current_number = self._get_next_todo()

    @api.multi
    def action_skip(self):
        """
        The method to pass to the next activity without doing anything

        Methods:
         * _get_next_todo()

        Extra info:
         * Expected singletom
        """
        self.ensure_one()
        current_number = self._get_next_todo()
        self.current_number = current_number

    @api.multi
    def action_previous(self):
        """
        The method to pass to the previous activity without doing anything

        Methods:
         * _get_previous_todo()

        Extra info:
         * Expected singletom
        """
        self.ensure_one()
        self.current_number = self._get_previous_todo()
