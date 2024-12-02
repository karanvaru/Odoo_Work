# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase
from odoo.osv import expression


class ApprovalTypeConfigureTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.model_name = 'res.users'
        self.ApprovalType = self.env['multi.approval.type'].with_user(SUPERUSER_ID)
        self.Approval = self.env['multi.approval'].with_user(SUPERUSER_ID)
        self.type1 = self.create_type()
        self.type2 = self.create_type({
            'priority': 10, 'name': 'Approval Type 2'})
        self.Model = self.env[self.model_name].with_user(SUPERUSER_ID)

    def create_type(self, default={}):
        vals = {
            'name': 'Approval Type',
            'model_id': self.model_name,
            'apply_for_model': True,
            'domain': "[('state', '=', 'new')]",
            'line_ids': [(0, 0, {'name': 'Level 1', 'user_id': SUPERUSER_ID})],
            'refuse_python_code': 'record.write({"name": "refused_name"})', # 'record.unlink()',
            'approve_python_code': 'record.write({"name": "approval_name"})'
        }
        vals.update(default)
        res = self.ApprovalType.create(vals)
        return res

    def test_configure(self):
        domain0 = self.ApprovalType.domain_get(self.model_name)
        self.type1.action_configure()
        self.assertEqual(self.type1.is_configured, True,
                         'Cannot configure the type 1')
        domain1 = self.ApprovalType.domain_get(self.model_name)
        domain1 = sorted(str(domain1))
        expect_dm = [('state', '=', 'new')]
        expect_dm = expression.OR([domain0] + [expect_dm])
        self.assertEqual(domain1, sorted(str(expect_dm)), 'Domain 1 is not correct')
        self.type2.action_configure()
        domain2 = self.ApprovalType.domain_get(self.model_name)
        domain2 = sorted(str(domain2))
        expect_dm = expression.OR([expect_dm] + [[('state', '=', 'new')]])
        self.assertEqual(self.type2.is_configured, True,
                         'Cannot configure the type 2')
        self.assertEqual(domain2, sorted(str(expect_dm)), 'Domain 2 is not correct')
        vals = {
            'name': 'name',
            'login': 'login',
            'state': 'new'
        }
        # get type by priority
        types = self.env['multi.approval.type']._get_types(self.model_name)
        self.assertEqual(types[0], self.type2, 'Fetch type by priority: failed')

        # Create new user
        new_user = self.Model.create(vals)
        self.assertEqual(new_user.x_need_approval, True, 'Cannot update approval state')
        ctx = {
            'active_model': 'res.users',
            'active_id': new_user.id
        }
        wizard = self.env['request.approval'].with_context(ctx).create({})
        request_id = wizard.action_request()['res_id']
        request = self.env['multi.approval'].browse(request_id)
        request.action_approve()
        self.assertEqual(request.state, 'Approved', 'Cannot approve')
        self.assertEqual(new_user.name, 'approval_name', 'Cannot approve (update name)')

        # Create new user 2
        vals.update({'login': 'login2'})
        new_user = self.Model.create(vals)
        self.assertEqual(new_user.x_need_approval, True, 'Cannot update approval state')
        ctx = {
            'active_model': 'res.users',
            'active_id': new_user.id
        }
        wizard = self.env['request.approval'].with_context(ctx).create({})
        request_id = wizard.action_request()['res_id']
        request = self.env['multi.approval'].browse(request_id)

        wizard = self.env['refused.reason'].with_context({'active_ids': [request_id]}).create({'reason': 'refuse reason'})
        wizard.action_reason_apply()
        self.assertEqual(request.state, 'Refused', 'Cannot refused')
        self.assertEqual(new_user.name, 'refused_name', 'Cannot refused (update name)')
        self.assertEqual(new_user.x_has_request_approval, True, 'Cannot count approval has been refused')

        # Rework
        wizard = self.env['rework.approval'].with_context(ctx).create({})
        wizard.action_rework()
        self.assertEqual(new_user.x_has_request_approval, False, 'Cannot rework')
        wizard = self.env['request.approval'].with_context(ctx).create({})
        request_id = wizard.action_request()['res_id']
        request = self.env['multi.approval'].browse(request_id)
        request.action_approve()
        self.assertEqual(request.state, 'Approved', 'Cannot approve after rework')
        self.assertEqual(new_user.name, 'approval_name', 'Cannot approve after rework (update name)')

        # archive
        view = self.type2.view_id
        view_id = view.id
        self.type2.action_archive()
        self.assertEqual(view.id, view_id, 'View is delete unexpected')
        self.assertEqual(self.type2.is_configured, False, 'Cannot archive')
        self.type1.action_archive()


