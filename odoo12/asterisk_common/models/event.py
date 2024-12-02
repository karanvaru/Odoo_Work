from odoo import models, fields, api, _


class Event(models.Model):
    _name = 'asterisk_common.event'
    _description = 'Asterisk Events'

    source = fields.Selection([('AMI', 'AMI'), ('ARI', 'ARI')],
                              required=True)
    name = fields.Char(required=True)
    model = fields.Char(required=True)
    method = fields.Char(required=True)
    delay = fields.Float(default=0, required=True)
    is_enabled = fields.Boolean(default=True, string='Enabled')
    condition = fields.Text()

    _sql_constraints = [
        ('event_uniq',
         'unique (source,name,model,method)',
         _('This event is already defined!'))
    ]
