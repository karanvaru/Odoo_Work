# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


# journal entery type
class JournalEntryType(models.Model):
    _name = 'journal.entry.type'

    name = fields.Char("Name")