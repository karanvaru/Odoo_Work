# -*- coding: utf-8 -*-


from odoo import api, fields, models

class do_with_feedback(models.TransientModel):
    """
    The wizard to pass feedback to activity
    """
    _name = 'do.with.feedback'
    _description = 'Mark Done With Feedback'

    activity_id = fields.Many2one(
        "mail.activity",
        string="Activity",
    )
    todo_id = fields.Many2one(
        "mail.activity.todo",
        string="To Do"
    )
    feedback = fields.Text(string="Feedback")

    @api.multi
    def action_do_with_feedback(self):
        """
        The method to add feedback to activity and return to to-do

        Methods:
         * action_done of mail.activity.todo

        Extra info:
         * Expected Singleton
        """
        self.ensure_one()
        self.activity_id.feedback = self.feedback
        self.todo_id.action_done()
