# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

import werkzeug.urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReworkApproval(models.TransientModel):
    _name = 'rework.approval'
    _description = 'Rework Approval'

    type_id = fields.Many2one(
        string="Type", comodel_name="multi.approval.type", required=True)
    origin_ref = fields.Reference(
        string="Origin",
        selection='_selection_target_model')

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.model
    def default_get(self, fs):
        '''
        1. Get approval type
        2. Set origin
        '''
        res = super(ReworkApproval, self).default_get(fs)
        ctx = self._context
        model_name = ctx.get('active_model')
        res_id = ctx.get('active_id')
        types = self.env['multi.approval.type']._get_types(model_name)
        approval_type = self.env['multi.approval.type'].filter_type(
            types, model_name, res_id)
        if not approval_type and types:
            approval_type = types[0]
        res.update({
            'type_id': approval_type.id,
            'origin_ref': '{model},{res_id}'.format(
                model=model_name, res_id=res_id),
        })
        return res

    def action_rework(self):
        '''
        1. update x_review_result = False
        2. update x_has_request_approval = False
        '''
        self.ensure_one()

        if not self.type_id.active or not self.type_id.is_configured or \
                self.origin_ref.x_review_result != 'refused':
            raise UserError(
                _('Data is changed! Please refresh your browser in order to continue !'))

        # update x_has_request_approval
        self.env['multi.approval.type'].update_x_field(
            self.origin_ref, 'x_has_request_approval', False)
        self.env['multi.approval.type'].update_x_field(
            self.origin_ref, 'x_review_result', False)
