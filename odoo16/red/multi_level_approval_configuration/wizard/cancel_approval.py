# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import fields, models


class CancelApproval(models.TransientModel):
    _name = 'cancel.approval'
    _description = 'Cancel Approval'

    reason = fields.Text(string='Reason', required=True)

    def action_cancel(self):
        '''
        '''
        self.ensure_one()
        ctx = self._context
        if ctx.get('active_model') != 'multi.approval':
            return False
        request_ids = ctx.get('active_ids', [])
        requests = self.env[ctx['active_model']].search(
            [('id', 'in', request_ids), ('state', '=', 'Submitted')]
        )
        if not requests:
            return False
        notify_type = self.env.ref("mail.mail_activity_data_todo", False)
        for request in requests:
            activities = request.sudo().activity_ids.filtered(
                    lambda a: a.activity_type_id == notify_type)
            activities.unlink()
        if requests:
            requests.message_post(body=self.reason)
        requests.write({'state': 'Cancel'})
        requests = requests.filtered(lambda x: x.origin_ref)
        for r in requests:
            # update x_has_request_approval
            self.env['multi.approval.type'].update_x_field(
                r.origin_ref, 'x_has_request_approval', False)
            self.env['multi.approval.type'].update_x_field(
                r.origin_ref, 'x_review_result', False)
