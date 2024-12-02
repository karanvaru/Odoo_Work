import uuid
import logging
from odoo import models, fields, api, _

logger = logging.getLogger(__name__)


class Callback(models.Model):
    _name = 'asterisk_calls.callback'
    _description = 'Callback Request'
    _order = 'id desc'
    _rec_name = 'id'

    uid = fields.Char(default=lambda self: uuid.uuid4().hex)
    subject = fields.Text()
    subject_short = fields.Char(string=_('Subject'), store=True,
                                compute='_compute_subject_short')
    contact_name = fields.Char(string=_('Contact'))
    partner_name = fields.Char(string=_('Partner'))
    phone = fields.Char(required=True)
    email = fields.Char()
    status = fields.Selection(selection=[
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ], default='progress')
    status_description = fields.Char()
    queue = fields.Char(default=lambda self: self.env[
        'asterisk_calls.util'].sudo().get_asterisk_calls_param(
        'callback_queue'))
    queue_exten = fields.Char()
    #calls = fields.One2many(comodel_name='asterisk_calls.call',
    #                        inverse_name='callback')
    last_retry = fields.Datetime()
    lead_id = fields.Integer(string=_('Lead'))
    call_time = fields.Char()
    start_time = fields.Datetime()

    @api.depends('subject')
    def _compute_subject_short(self):
        for rec in self:
            if rec.subject:
                rec.subject_short = rec.subject if len(rec.subject) < 50 else \
                                                    rec.subject[:50] + '...'
