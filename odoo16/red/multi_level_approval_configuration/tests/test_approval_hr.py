# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import exceptions
from .base_configuration import ApprovalTestConfiguration


class ApprovalReviewTest(ApprovalTestConfiguration):

    def test_hr_no_special_user(self):
        if "special_user" not in self.approval_type_2.line_ids._fields:
            return
        self.approval_type_2.line_ids[0].special_user = "Line Manager"
        self.approval_type_2.line_ids[0].special_user = "Coach"
        self.approval_type_2.line_ids = [(0, 0, {
            "name": "Level 3",
            "user_id": self.approver_1.id,
            "sequence": 3,
            "require_opt": "Required",
            "special_user": "Manager of Department"
        })]
        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.line_ids[0].user_id, self.approver_1)
        self.assertEqual(request1.line_ids[1].user_id, self.approver_2)
        self.assertEqual(request1.line_ids[2].user_id, self.approver_1)
 
    def test_hr_special_user(self):
        if "special_user" not in self.approval_type_2.line_ids._fields:
            return
        self.approval_type_2.line_ids[0].special_user = "Line Manager"
        self.approval_type_2.line_ids[1].special_user = "Coach"
        self.approval_type_2.line_ids = [(0, 0, {
            "name": "Level 3",
            "user_id": self.approver_1.id,
            "sequence": 3,
            "require_opt": "Required",
            "special_user": "Manager of Department"
        })]
        approver_10 = self.new_user(10)
        approver_11 = self.new_user(11)
        approver_12 = self.new_user(12)
        employee_1 = self.new_employee(1, self.user_1)
        employee_line_man = self.new_employee(2, approver_10)
        employee_coach = self.new_employee(3, approver_11)
        employee_dep_man = self.new_employee(4, approver_12)
        dept = self.env['hr.department'].create([
            {
                'name': 'parent',
                'manager_id': employee_dep_man.id
            },
        ])
        employee_1.department_id = dept
        employee_1.parent_id = employee_line_man
        employee_1.coach_id = employee_coach

        request1 = self.request_one(self.obj_1, self.user_1)
        self.assertEqual(request1.line_ids[0].user_id, approver_10)
        self.assertEqual(request1.line_ids[1].user_id, approver_11)
        self.assertEqual(request1.line_ids[2].user_id, approver_12)
