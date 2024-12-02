# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    origin_ref = fields.Reference(
        string="Origin",
        selection='_selection_target_model')

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    def update_source_obj(self, obj, result='approved', log_msg=''):
        if not obj:
            return False
        obj.write({
            'x_review_result': result,
        })
        if log_msg and hasattr(obj, 'message_post'):
            obj.message_post(body=log_msg)

    def set_approved(self):
        super(MultiApproval, self).set_approved()

        # customized code
        '''
        1. Write a log on the source document
        2. Call the callback action when approved
        Note: always update the x_has_approved first !
        '''
        if not self.origin_ref:
            return False
        log_msg = _('{} has approved this document !').format(
            self.env.user.name)
        self.update_source_obj(self.origin_ref, log_msg=log_msg)
        res = self.type_id.run(self.origin_ref)
        if res:
            return res

    def set_refused(self, reason=''):
        super(MultiApproval, self).set_refused()

        # customized code
        '''
        1. Write a log on the source document
        2. Call the callback action when refused
        Note: always update the x_has_approved first !
        '''
        if not self.origin_ref:
            return False
        log_msg = _('{} has refused this document due to this reason: {}'
                    ).format(self.env.user.name, reason)
        self.update_source_obj(self.origin_ref, 'refused', log_msg)
        res = self.type_id.run(self.origin_ref, 'refuse')
        if res:
            return res

    @api.model
    def open_request(self):
        ctx = self._context
        model_name = ctx.get('active_model')
        res_id = ctx.get('active_id')
        origin_ref = '{model},{res_id}'.format(
            model=model_name, res_id=res_id)
        return {
            'name': 'My Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'multi.approval',
            'view_type': 'list',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('origin_ref', '=', origin_ref)],
        }
