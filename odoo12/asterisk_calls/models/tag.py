from odoo import models, fields, api, _


class Tag(models.Model):
    _name = 'asterisk_calls.tag'
    _description = 'Call Tag'

    name = fields.Char(required=True)
    calls = fields.Many2many('asterisk_calls.call', relation='asterisk_calls_call_tag',
                             column1='call', column2='tag')
    call_count = fields.Integer(compute=lambda self: self._compute_call_count(),
                                string=_('Calls'))

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The name must be unique!')),
    ]


    
    def _compute_call_count(self):
        for rec in self:
            rec.call_count = self.env['asterisk_calls.call'].search_count(
                    [('tags', 'in', rec.id)])

