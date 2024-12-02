# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


# journal entery type
class JournalEntryType(models.Model):
    _name = 'inventory.value.type.je'

    name = fields.Char("Inventory Value Type")