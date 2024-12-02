from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class MultiApproveInherit(models.Model):
    _inherit = 'multi.approval'

    def set_approved(self):
        super(MultiApproveInherit, self).set_approved()

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
        if 'purchase.order' in self.origin_ref._name:
            self.origin_ref.button_approve(force=False)
        res = self.type_id.run(self.origin_ref)
        if res:
            return res

    def action_approve(self):
        ret_act = None
        recs = self.filtered(lambda x: x.state == 'Submitted')
        for rec in recs:
            _logger.error(f"rec: {rec}")
            if not rec.is_pic:
                msg = _('{} do not have the authority to approve this request !'.format(rec.env.user.name))
                self.sudo().message_post(body=msg)
                return False
            lines = rec.line_id
            for line in lines:
                if not line or line.state != 'Waiting for Approval':
                    # Something goes wrong!
                    self.message_post(body=_('Something goes wrong!'))
                    return False

                # Update follower
                rec.update_follower(self.env.uid)

                # check if this line is required
                other_lines = rec.line_ids.filtered(
                    lambda x: x.sequence >= line.sequence and x.state == 'Draft')
                _logger.error(f"other lines: {other_lines}")
                if not other_lines:
                    or_lines = rec.line_ids.filtered(
                        lambda r: r.require_opt in ['or', 'Optional'] and r.state == 'Waiting for Approval')
                    _logger.error(f"or lines: {or_lines}")
                    if or_lines:
                        rec.pic_ids = None
                        rec.line_id = None
                        for option in or_lines:
                            option.set_approved()

                    ret_act = rec.set_approved()
                else:
                    required_vals = other_lines.filtered(
                        lambda r: r.require_opt in ['Required'] and r.state == 'Draft')
                    if required_vals:
                        optional_vals = other_lines.filtered(
                            lambda r: r.require_opt in ['Optional'] and r.state == 'Draft')
                        next_line = required_vals.sorted('sequence')[0]
                        next_line.write({
                            'state': 'Waiting for Approval',
                        })

                        rec.line_id = next_line
                        rec.pic_ids = rec.line_id.user_id
                        if optional_vals:
                            for option in optional_vals:
                                rec.pic_ids += option.user_id
                        rec.send_request_mail()
                        recs.send_activity_notification()
                    else:
                        or_lines = other_lines.filtered(
                            lambda r: r.require_opt in ['or', 'Optional'] and r.state == 'Waiting for Approval')

                        _logger.error(f"or lines: {or_lines}")

                        if or_lines:
                            optional_vals = other_lines.filtered(
                                lambda r: r.require_opt in ['Optional'] and r.state == 'Draft')
                            rec.pic_ids = None
                            rec.line_id = None
                            for option in or_lines:
                                option.write({
                                    'state': 'Approved'
                                })
                                rec.line_id += option
                                rec.pic_ids += option.user_id

                                option.set_approved()

                            if optional_vals:
                                for option in optional_vals:
                                    rec.pic_ids += option.user_id

                            rec.send_request_mail()
                            recs.send_activity_notification()
                line.set_approved()

                break
            msg = _('I approved')
            rec.finalize_activity_or_message('approved', msg)

        if ret_act:
            return ret_act
        return True


class RequestApprovalInherit(models.TransientModel):
    _inherit = 'request.approval'
    _description = 'Request Approval'

    def action_request(self):
        '''
        1. create request
        2. Submit request
        3. update x_has_request_approval = True
        4. open request form view
        '''
        self.ensure_one()

        if not self.type_id.active or not self.type_id.is_configured or \
                not self.origin_ref.x_need_approval:
            raise UserError(
                _('Data is changed! Please refresh your browser in order to continue !'))
        if self.origin_ref.x_has_request_approval and \
                not self.type_id.is_free_create:
            raise UserError(
                _('Request has been created before !'))
        # create request
        vals = {
            'name': self.name,
            'priority': self.priority,
            'type_id': self.type_id.id,
            'description': self.description,
            'origin_ref': '{model},{res_id}'.format(
                model=self.origin_ref._name,
                res_id=self.origin_ref.id)
        }
        request = self.env['multi.approval'].create(vals)
        request.action_submit()

        # update x_has_request_approval
        self.env['multi.approval.type'].update_x_field(request.origin_ref, 'x_has_request_approval')

        if 'purchase.order' in request.origin_ref._name:
            order = self.env['purchase.order'].search([('id', '=', request.origin_ref.id)])
            order.sudo().write({
                'state': 'to approve'
            })

            return {
                'name': _('Purchase Orders'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'res_id': request.origin_ref.id,
            }

        elif 'travel.request' in request.origin_ref._name:
            order = self.env['travel.request'].search([('id', '=', request.origin_ref.id)])
            order.sudo().write({
                'state': 'confirmed'
            })

            return {
                'name': _('Travel Requests'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'travel.request',
                'res_id': request.origin_ref.id,
            }
        else:
            return {
                'name': _('My Requests'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'multi.approval',
                'res_id': request.id,
            }
