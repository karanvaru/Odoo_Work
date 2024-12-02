# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleEstimate(models.Model):
    _name = 'sale.estimate'
    _inherit = ['sale.estimate','portal.mixin']


    def _compute_access_url(self):
        super(SaleEstimate, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/estimate_report/print/pdf/%s' % (rec.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
