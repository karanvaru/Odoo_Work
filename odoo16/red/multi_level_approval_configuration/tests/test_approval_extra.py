# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import exceptions
from odoo.tests.common import Form
from .base_configuration import ApprovalTestConfiguration


class ApprovalExtraTest(ApprovalTestConfiguration):

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

    def test_rework(self):
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.type_id, self.approval_type_2)
        request1.with_user(self.approver_1).action_refuse()
        rework_form = Form(self.env["rework.approval"] \
            .with_context(active_model=self.obj_1._name, active_id=self.obj_1.id)\
                .with_user(self.user_1.id))
        wiz = rework_form.save()
        wiz.action_rework()
        self.assertFalse(self.obj_1.x_has_request_approval)

        # Request again after rework
        self.obj_1.state = "to_approve"
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.type_id, self.approval_type_2)
        request1.with_user(self.approver_1).action_approve()
        self.assertEqual(request1.with_user(self.approver_2).is_pic, True)
        request1.with_user(self.approver_2).action_approve()
        self.assertEqual(request1.state, 'Approved')
        self.assertEqual(request1.origin_ref.state, 'approve')

    def test_archive(self):
        self.assertTrue(self.approval_type_2.view_id.id)
        self.approval_type_2.action_archive()
        self.assertFalse(self.approval_type_2.view_id.id)
        self.assertFalse(self.approval_type_2.is_configured)
        self.approval_type_1.action_archive()
        self.approval_type_3.action_archive()
        self.approval_type_4.action_archive()
        domain0 = self.ApprovalType.with_user(self.user_2.id).domain_get(self.model_name)
        self.assertFalse(domain0)

    def test_change_approver(self):
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.pic_id, self.approver_1)
        change_form = Form(self.env["change.approver"] \
            .with_context(active_model=request1._name,
                    active_id=request1.id,
                    active_ids=request1.ids)\
                .with_user(self.user_1.id))
        change_form.new_pic_id = self.approver_2
        change_form.reason = "Test change approver"
        wiz = change_form.save()
        wiz.action_update()
        self.assertEqual(request1.pic_id, self.approver_2)
        res = request1.with_user(self.approver_1).action_approve()
        self.assertFalse(res)
        res = request1.with_user(self.approver_2).action_approve()
        self.assertTrue(res)
        request1.with_user(self.approver_2).action_approve()
        self.assertEqual(request1.origin_ref.state, 'approve')

    def test_change_approver_by_deputy(self):
        deputy_group = self.env["res.groups"].create({"name": "Deputy Group"})
        self.approval_type_2.line_ids.group_ids |= deputy_group
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.pic_id, self.approver_1)
        change_form = Form(self.env["change.approver"] \
            .with_context(active_model=request1._name,
                    active_id=request1.id,
                    active_ids=request1.ids)\
                .with_user(self.user_1.id))
        change_form.new_pic_id = self.approver_2
        change_form.reason = "Test change approver"
        wiz = change_form.save()
        with self.assertRaises(exceptions.UserError):
            wiz.action_update()
        self.approver_2.groups_id |= deputy_group
        wiz.action_update()
        self.assertEqual(request1.pic_id, self.approver_2)
        res = request1.with_user(self.approver_1).action_approve()
        self.assertFalse(res)
        res = request1.with_user(self.approver_2).action_approve()
        self.assertTrue(res)
        request1.with_user(self.approver_2).action_approve()
        self.assertEqual(request1.origin_ref.state, 'approve')
        
    def test_cancel_approval(self):
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.pic_id, self.approver_1)
        cancel_form = Form(self.env["cancel.approval"] \
            .with_context(active_model=request1._name,
                    active_id=request1.id,
                    active_ids=request1.ids)\
                .with_user(self.user_1.id))
        cancel_form.reason = "Test cancel approval"
        wiz = cancel_form.save()
        wiz.action_cancel()
        self.assertEqual(request1.state, "Cancel")
        self.assertFalse(request1.origin_ref.x_has_request_approval)
        self.assertFalse(request1.origin_ref.x_review_result)
