from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ChartOfAccountInherited(models.Model):
    _inherit = 'account.account'

    ebitda_group_id = fields.Many2one('ebitda.group', string="EBITDA Group", required=True)


class EbitdaGroup(models.Model):
    _name = 'ebitda.group'

    name = fields.Char('Name')