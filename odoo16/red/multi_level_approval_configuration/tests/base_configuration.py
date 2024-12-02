# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo.tests.common import TransactionCase, Form


class ApprovalTestConfiguration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(ApprovalTestConfiguration, cls).setUpClass()
        cls.Approval = cls.env["multi.approval"]
        cls.ApprovalLine = cls.env["multi.approval.line"]
        cls.ApprovalType = cls.env["multi.approval.type"]
        cls.ApprovalTypeLine = cls.env["multi.approval.type.line"]
        cls.user_group = cls.env["res.groups"].create({"name": "Demo Group"})
        cls.approver_1 = cls.new_user(cls, 1)
        cls.approver_2 = cls.new_user(cls, 2)
        cls.user_1 = cls.new_user(cls, 3)
        cls.user_2 = cls.new_user(cls, 4)
        cls.user_2.groups_id |= cls.user_group
        cls.model_name = "test.approval"
        cls.Obj = cls.env[cls.model_name]
        cls.approval_type_1 = cls.new_approval_type(cls, 1)
        cls.approval_type_2 = cls.new_approval_type(cls, 2, priority=50)
        cls.approval_type_3 = cls.new_approval_type(cls, 3, state='to_approve_2')
        cls.approval_type_4 = cls.new_approval_type(cls, 4, priority=10, defaults={
            "group_ids": [(6, 0, cls.user_group.ids)]
        })
        cls.approval_type_1.action_configure()
        cls.approval_type_2.action_configure()
        cls.approval_type_3.action_configure()
        cls.approval_type_4.action_configure()
        cls.obj_1 = cls.new_object(cls, 1, cls.user_1, 'to_approve')
        cls.obj_2 = cls.new_object(cls, 2, cls.user_1,)
        cls.obj_3 = cls.new_object(cls, 3, cls.user_1, 'to_approve_2')
        cls.obj_4 = cls.new_object(cls, 4, cls.user_2, 'to_approve')

    def new_user(self, no):
        user = self.env['res.users'].create({
            'name': 'Demo User {}'.format(no),
            'login': 'dmuser_{}'.format(no),
            'password': 'dmuser_{}'.format(no),
            'groups_id': [
                (6, 0, self.env.ref('base.group_user').ids),
                (4, self.env.ref('multi_level_approval.group_approval_user').id),
            ],
        })
        user.partner_id.email = 'dmuser_{}@test.com'.format(no)
        return user

    def new_employee(self, no, user):
        e = self.env['hr.employee'].create({
            'name': 'Demo Employee {}'.format(no),
            'user_id': user.id
        })
        return e

    def new_approval_type(self, no, state='to_approve', priority=100, defaults={}):
        vals = {
            'name': 'Approval Type {}'.format(no),
            'model_id': self.model_name,
            'apply_for_model': True,
            'domain': "[('state', '=', '{}')]".format(state),
            'priority': priority,
            "line_ids": [
                (0, 0, {
                    "name": "Level 1",
                    "user_id": self.approver_1.id,
                    "sequence": 1,
                    "require_opt": "Required"
                }),
                (0, 0, {
                    "name": "Level 2",
                    "user_id": self.approver_2.id,
                    "sequence": 2,
                    "require_opt": "Required"
                }),
            ],
            'refuse_python_code': 'record.write({"state": "refuse"})',
            'approve_python_code': 'record.write({"state": "approve"})'
        }
        vals.update(defaults)
        return self.ApprovalType.create(vals)

    def new_object(self, no, user, state='draft'):
        return self.Obj.with_user(user.id).create({
            "name": "New object {}".format(no),
            "state": state
        })

    def request_one(self, obj, user):
        request_form = Form(self.env["request.approval"] \
                    .with_context(active_model=self.model_name, active_id=obj.id)\
                        .with_user(user.id))
        #wizard = self.env['request.approval'].with_context(ctx).create({})
        wiz = request_form.save()
        request_id = wiz.action_request()['res_id']
        request = self.env['multi.approval'].browse(request_id)
        return request
