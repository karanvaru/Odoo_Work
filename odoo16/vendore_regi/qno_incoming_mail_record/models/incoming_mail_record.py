from odoo import api, fields, models, _


class IncomingMailRecord(models.Model):
    _name = 'incoming.mail.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Incoming Mail Records"

    name = fields.Char(
        string="Name",
        copy=False
    )
    description = fields.Html(
        string="Description",
        copy=False
    )
    task_id = fields.Many2one(
        'project.task',
        string="Task",
        copy=False
    )

    def _message_post_after_hook(self, message, msg_vals):
        if not self.description:
            self.description = message.body
        return super(IncomingMailRecord, self)._message_post_after_hook(message, msg_vals)
