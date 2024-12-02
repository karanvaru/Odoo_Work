# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import exceptions
from .base_configuration import ApprovalTestConfiguration


class ApprovalReviewTest(ApprovalTestConfiguration):

    def test_configure(self):
        domain0 = self.ApprovalType.with_user(self.user_2.id).domain_get(self.model_name)
        expect_dm = ['|', '|', '|', ('state', '=', 'to_approve'), ('state', '=', 'to_approve'),
            ('state', '=', 'to_approve_2'), ('state', '=', 'to_approve')]
        self.assertEqual(sorted(str(expect_dm)), sorted(str(domain0)), 'Domain is not correct')

        self.assertTrue(self.approval_type_1.is_global)
        self.assertTrue(self.approval_type_2.is_global)
        self.assertTrue(self.approval_type_3.is_global)
        self.assertFalse(self.approval_type_4.is_global)

        # Check priority
        types = self.env['multi.approval.type'].with_user(self.user_1.id)._get_types(self.model_name)
        self.assertEqual(types[0], self.approval_type_2)
        types = self.env['multi.approval.type'].with_user(self.user_2.id)._get_types(self.model_name)
        self.assertEqual(types[0], self.approval_type_4)

        # Check field existence
        f_names = ['x_review_result', 'x_has_request_approval', 'x_need_approval']
        mail_fields = self.obj_1._fields
        for f_name in f_names:
            self.assertTrue(f_name in mail_fields, 'Field {} does not exists'.format(f_name))
        self.assertTrue(self.approval_type_1.is_configured)
        self.assertTrue(self.approval_type_2.is_configured)
        self.assertTrue(self.approval_type_3.is_configured)
        self.assertTrue(self.approval_type_4.is_configured)
        self.assertTrue(self.obj_1.x_need_approval)
        self.assertFalse(self.obj_2.x_need_approval)
        self.assertTrue(self.obj_3.x_need_approval)
        self.assertTrue(self.obj_4.x_need_approval)

    def test_request_approval(self):
        # Request approval
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.type_id, self.approval_type_2)
        with self.assertRaises(exceptions.UserError):
            request2 = self.request_one(self.obj_2, self.user_1)
        request3 = self.request_one(self.obj_3, self.user_1)
        self.assertEqual(request3.type_id, self.approval_type_3)
        request4 = self.request_one(self.obj_4, self.user_2)
        self.assertEqual(request4.type_id, self.approval_type_4)

        # Approve Request
        request1.with_user(self.approver_1).action_approve()
        self.assertEqual(request1.with_user(self.approver_2).is_pic, True)
        request1.with_user(self.approver_2).action_approve()
        self.assertEqual(request1.state, 'Approved')
        self.assertEqual(request1.origin_ref.state, 'approve')

    def test_request_refuse(self):
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.type_id, self.approval_type_2)
        request1.with_user(self.approver_1).action_refuse()
        #request1.with_user(self.approver_2).action_refuse()
        self.assertEqual(request1.state, 'Refused')
        self.assertEqual(request1.origin_ref.state, 'refuse')
