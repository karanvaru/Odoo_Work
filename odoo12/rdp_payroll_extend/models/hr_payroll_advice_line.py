# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class HrPayrollAdviceLineInherit(models.Model):

    _inherit = 'hr.payroll.advice.line'


    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    
  


    @api.model
    def create(self, vals):
        vals.update({
            'reference': self.env['ir.sequence'].next_by_code('hr.payroll.advice.line.sequence'),
        })
        return super(HrPayrollAdviceLineInherit, self).create(vals)

                    












