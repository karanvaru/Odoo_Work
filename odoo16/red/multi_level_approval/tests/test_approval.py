# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from odoo import exceptions, _
from odoo.tests import common


class TestApproval(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestApproval, cls).setUpClass()
        cls.Approval = cls.env["multi.approval"]
        cls.ApprovalLine = cls.env["multi.approval.line"]
        cls.ApprovalType = cls.env["multi.approval.type"]
        cls.ApprovalTypeLine = cls.env["multi.approval.type.line"]
        cls.user_1 = cls.env['res.users'].create({
            'name': 'Demo User 1',
            'login': 'dmuser_1',
            'password': 'dmuser_1',
            'groups_id': [
                (6, 0, cls.env.ref('base.group_user').ids),
                (4, cls.env.ref('multi_level_approval.group_approval_user').id),
            ],
        })
        cls.user_1.partner_id.email = 'dmuser_1@test.com'
        cls.user_2 = cls.env['res.users'].create({
            'name': 'Demo User 2',
            'login': 'dmuser_2',
            'password': 'dmuser_2',
            'groups_id': [
                (6, 0, cls.env.ref('base.group_user').ids),
                (4, cls.env.ref('multi_level_approval.group_approval_user').id),
            ],
        })
        cls.user_2.partner_id.email = 'dmuser_2@test.com'
        cls.approval_type = cls.ApprovalType.create({
            "name": "Type 1",
            "line_ids": [
                (0, 0, {
                    "name": "Level 1",
                    "user_id": cls.user_1.id,
                    "sequence": 1,
                    "require_opt": "Required"
                }),
                (0, 0, {
                    "name": "Level 2",
                    "user_id": cls.user_2.id,
                    "sequence": 2,
                    "require_opt": "Required"
                }),
            ]
        })
        cls.approval_request_1 = cls.Approval.create({
            "name": "New request 1",
            "type_id": cls.approval_type.id,
            "description": "I just create a new request"
        })

    def test_action_submit_error_document(self):
        self.approval_type.document_opt = "Required"
        with self.assertRaises(exceptions.UserError):
            self.approval_request_1.action_submit()
        self.env['ir.attachment'].create({
            "name": "test att",
            "res_model": self.approval_request_1._name,
            "res_id": self.approval_request_1.id
        })
        self.approval_request_1.action_submit()

    def test_action_submit_error_no_line(self):
        self.approval_type.line_ids = False
        with self.assertRaises(exceptions.UserError):
            self.approval_request_1.action_submit()

    def test_action_submit_check_line(self):
        self.approval_request_1.action_submit()
        self.assertEqual(self.approval_request_1.state, "Submitted")
        self.assertEqual(len(self.approval_request_1.line_ids), 2)
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Waiting for Approval")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Draft")
        self.assertEqual(self.approval_request_1.line_ids[0].sequence, 1)
        self.assertEqual(self.approval_request_1.line_ids[1].sequence, 2)
        self.assertEqual(self.approval_request_1.line_ids[0].user_id, self.user_1)
        self.assertEqual(self.approval_request_1.line_ids[1].user_id, self.user_2)

    def test_action_cancel(self):
        self.approval_request_1.action_cancel()
        self.assertEqual(self.approval_request_1.state, "Cancel")

    def test_action_submit_send_email(self):
        self.approval_type.mail_notification = True
        self.approval_request_1.action_submit()
        message = self.env['mail.message'].search([
            ("model", "=", self.approval_request_1._name),
            ("res_id", "=", self.approval_request_1.id),
            ("subject", "=", _('Request the approval for: {request_name}').format(
                request_name=self.approval_request_1.display_name))
        ])
        self.assertEqual(len(message), 1)

    def test_action_submit_activity_notification(self):
        self.approval_type.activity_notification = True
        self.approval_request_1.action_submit()
        activity = self.env['mail.activity'].search([
            ("res_model_id", "=", self.env['ir.model']._get(self.approval_request_1._name).id),
            ("res_id", "=", self.approval_request_1.id),
            ("activity_type_id", "=", self.env.ref("mail.mail_activity_data_todo", False).id)
        ])
        self.assertEqual(len(activity), 1)

    def test_action_approve_error_pic(self):
        self.approval_request_1.action_submit()
        with self.assertRaises(exceptions.AccessError):
            self.approval_request_1.with_user(self.user_2).action_approve()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Waiting for Approval")

    def test_action_approve_success(self):
        self.approval_type.mail_notification = True
        self.approval_type.activity_notification = True
        self.approval_request_1.action_submit()
        self.approval_request_1.with_user(self.user_1).action_approve()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Approved")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Waiting for Approval")
        messages = self.env['mail.message'].search([
            ("model", "=", self.approval_request_1._name),
            ("res_id", "=", self.approval_request_1.id),
            ("subject", "=", _('Request the approval for: {request_name}').format(
                request_name=self.approval_request_1.display_name))
        ])
        self.assertEqual(len(messages), 2)
        activitiy = self.env['mail.activity'].sudo().search([
            ("res_model_id", "=", self.env['ir.model']._get(self.approval_request_1._name).id),
            ("res_id", "=", self.approval_request_1.id),
            ("activity_type_id", "=", self.env.ref("mail.mail_activity_data_todo", False).id)
        ])
        self.assertEqual(len(activitiy), 1)  # old activity has been done

        self.approval_request_1.with_user(self.user_2).action_approve()
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Approved")
        self.assertEqual(self.approval_request_1.state, "Approved")
        activitiy = self.env['mail.activity'].sudo().search([
            ("res_model_id", "=", self.env['ir.model']._get(self.approval_request_1._name).id),
            ("res_id", "=", self.approval_request_1.id),
            ("activity_type_id", "=", self.env.ref("mail.mail_activity_data_todo", False).id)
        ])
        self.assertEqual(len(activitiy), 0)

    def test_action_refuse_error_pic(self):
        self.approval_request_1.action_submit()
        with self.assertRaises(exceptions.AccessError):
            self.approval_request_1.with_user(self.user_2).action_refuse()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Waiting for Approval")

    def test_action_refuse_success_1(self):
        self.approval_request_1.action_submit()
        self.approval_request_1.with_user(self.user_1).action_refuse()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Refused")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Cancel")
        self.assertEqual(self.approval_request_1.state, "Refused")

    def test_action_refuse_success_2(self):
        self.approval_request_1.action_submit()
        self.approval_request_1.with_user(self.user_1).action_approve()
        self.approval_request_1.with_user(self.user_2).action_refuse()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Approved")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Refused")
        self.assertEqual(self.approval_request_1.state, "Refused")

    def test_action_refuse_success_2(self):
        self.approval_type.line_ids[0].require_opt = "Optional"
        self.approval_request_1.action_submit()
        self.approval_request_1.with_user(self.user_1).action_refuse()
        self.assertEqual(self.approval_request_1.state, "Submitted")
        self.approval_request_1.with_user(self.user_2).action_refuse()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Refused")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Refused")
        self.assertEqual(self.approval_request_1.state, "Refused")

    def test_action_refuse_then_approve(self):
        self.approval_type.line_ids[0].require_opt = "Optional"
        self.approval_request_1.action_submit()
        self.approval_request_1.with_user(self.user_1).action_refuse()
        self.approval_request_1.with_user(self.user_2).action_approve()
        self.assertEqual(self.approval_request_1.line_ids[0].state, "Refused")
        self.assertEqual(self.approval_request_1.line_ids[1].state, "Approved")
        self.assertEqual(self.approval_request_1.state, "Approved")
