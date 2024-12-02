import json
import logging
from odoo import models, fields
from odoo.tools import safe_eval


logger = logging.getLogger(__name__)


class UserOptionWizard(models.TransientModel):
    _name = 'asterisk_common.user_option_wizard'
    _description = 'Set Option'

    option = fields.Char(required=True)
    value = fields.Char()

    def do_change(self):
        users = self.env['asterisk_common.user'].browse(
            self._context.get('active_ids', []))
        value = self.value
        if isinstance(users._fields[self.option], (
                fields.Char, fields.Integer, fields.Selection, fields.Text)):
            value = value
        elif value and value[0] == '[' and value[-1:] == ']':
            # Many2many field update
            value = json.loads(value.lower())
        else:
            value = safe_eval(value)
        specs = users._onchange_spec()
        values = {self.option: value}
        for user in users:
            values = values.copy()
            updates = user.onchange(values, [self.option], specs)
            value = updates.get('value', {})
            for name, val in value.items():
                if isinstance(val, tuple):
                    value[name] = val[0]
                values.update(value)
            user.write(values)
        return {}
