# -*- coding: utf-8 -*-
from odoo import fields, models


class GatiGoodsCode(models.Model):
    _name = 'gati.goods.code'
    _description = 'Gati Goods Code List'

    name = fields.Char('Goods Name', required=True, index=True, help="Name of Goods")
    code = fields.Char('Goods Code', required=True, help="Goods Code")
