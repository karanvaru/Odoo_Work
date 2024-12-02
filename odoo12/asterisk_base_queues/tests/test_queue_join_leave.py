from odoo.tests.common import TransactionCase
from odoo.addons.asterisk_common.models.res_users import ResUser
from odoo.addons.asterisk_common.models.agent import Agent

from unittest.mock import patch, call

import logging

logger = logging.getLogger(__name__)


class TestOperators(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.queue = self.env.ref('asterisk_base_queues.sales_queue')
        self.admin = self.env.ref('base.user_admin')
        self.demo = self.env.ref('base.user_demo')
        self.aster_admin = self.env.ref('asterisk_base_queues.user_admin')
        self.aster_demo = self.env.ref('asterisk_common.user_demo')
        return result

    @patch.object(ResUser, 'asterisk_notify')
    def test_response_functions_no_agent_response(self, mock_asterisk_notify):
        """If agent response is none return False. Make sure user is notified"""
        no_response = {
            'pass_back': {
                'uid': 1,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            },
            'result': None
        }
        self.assertEqual(self.queue.join_response(no_response), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('No response from agent. Please make sure it is running.',
                     uid=1)])
            mock_asterisk_notify.reset_mock()
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")
        self.assertEqual(self.queue.leave_response(no_response), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('No response from agent. Please make sure it is running.',
                     uid=1)])
            mock_asterisk_notify.reset_mock()
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")
        self.assertEqual(self.queue.update_status_response(no_response), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('No response from agent. Please make sure it is running.',
                     uid=1)])
            mock_asterisk_notify.reset_mock()
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")
        self.assertEqual(self.queue.update_users_response(no_response), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('No response from agent. Please make sure it is running.',
                     uid=1)])
            mock_asterisk_notify.reset_mock()
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")

    @patch.object(ResUser, 'asterisk_notify')
    def test_join_response_static_exists_in_aster(
            self, mock_asterisk_notify):
        """ If user in aster, check if static locally. Notify if static"""
        self.env['asterisk_base_queues.queue_member'].with_context(
            no_build_conf=True).create({
                'user': self.aster_admin.id,
                'queue': self.queue.id,
                'is_static': True
            })
        data = {
            'result': [{
                'Response': 'Error',
                'Message': 'Already there',
            }],
            'pass_back': {
                'uid': self.admin.id,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            }
        }
        self.assertEqual(self.queue.join_response(data), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('User has been already added as static member!',
                     uid=self.admin.id)])
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")

    @patch.object(ResUser, 'asterisk_notify')
    def test_join_response_static_user_in_odoo(self, mock_asterisk_notify):
        """If static in Odoo, absent in Aster notify user to apply changes"""
        self.env['asterisk_base_queues.queue_member'].with_context(
            no_build_conf=True).create({
                'user': self.aster_admin.id,
                'queue': self.queue.id,
                'is_static': True
            })

        data = {
            'result': [{
                'Response': 'Success',
                'Message': 'Added member',
            }],
            'pass_back': {
                'uid': self.admin.id,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            }
        }
        self.assertEqual(self.queue.join_response(data), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('Apply changes to add the static user!',
                     uid=self.admin.id)])
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")

    @patch.object(ResUser, 'asterisk_notify')
    def test_join_response_generic_error(self, mock_asterisk_notify):
        """If error in Aster, notify user with the error"""
        data = {
            'result': [{
                'Response': 'Error',
                'Message': 'Generic Queue Error',
            }],
            'pass_back': {
                'uid': self.admin.id,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            }
        }
        self.assertEqual(self.queue.join_response(data), False)
        try:
            mock_asterisk_notify.assert_called_once()
            mock_asterisk_notify.assert_has_calls([
                call('Join queue error: Generic Queue Error',
                     uid=self.admin.id)])
        except AttributeError:
            print("Not testing mock calling, being implemented in version 3.6")

    def test_successful_join_response(self):
        """Test that user was successfully created"""
        data = {
            'result': [{
                'Response': 'Success',
                'Message': 'Joined user',
            }],
            'pass_back': {
                'uid': self.admin.id,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            }
        }
        with patch.object(Agent, 'reload_view') as mock_reload, \
                patch.object(ResUser, 'asterisk_notify') as mock_notify:
            self.assertEqual(self.queue.join_response(data), True)
            try:
                mock_notify.assert_called_once()
                mock_notify.assert_has_calls([
                    call('User added successfully',
                         uid=self.admin.id)])
                mock_reload.assert_called_once()
                mock_reload.assert_has_calls([
                    call(
                        model='asterisk_base_queues.queue',
                        uid=self.admin.id)])
            except AttributeError:
                print("Not testing mock calling, implemented in version 3.6")

    def test_join_response_dynamic_exists_in_aster(self):
        """ If user in aster, check if static locally. Notify if static"""
        self.env['asterisk_base_queues.queue_member'].with_context(
            no_build_conf=True).create({
                'user': self.aster_admin.id,
                'queue': self.queue.id,
                'is_static': False
            })
        data = {
            'result': [{
                'Response': 'Error',
                'Message': 'Already there',
            }],
            'pass_back': {
                'uid': self.admin.id,
                'queue': self.queue.id,
                'asterisk_user': self.aster_admin.id
            }
        }
        self.assertEqual(self.queue.join_response(data), True)
