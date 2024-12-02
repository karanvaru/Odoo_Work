from odoo import models, fields, api, _


class Event(models.Model):
    _name = 'asterisk_calls.event'
    _description = 'Asterisk Events'

    event_type = fields.Selection([('ami', 'AMI'), ('ari', 'ARI')],
                                  required=True)
    event_name = fields.Char(required=True)
    target_model = fields.Char(required=True)
    target_method = fields.Char(required=True)
    delay = fields.Float(default=0, required=True)
    is_enabled = fields.Boolean(default=True)
    condition = fields.Text()

    _sql_constraints = [
        ('hook_uniq',
         'unique (event_type,event_name,target_model,target_method)',
         _('This event hook is already defined!')),
    ]
