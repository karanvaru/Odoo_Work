from odoo.tests.common import TransactionCase
from ..utils import get_default_server


class TestServer(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.server = self.env.ref('asterisk_base.default_server')
        return result

    def test_default_server(self):
        self.assertEqual(get_default_server(self), self.server.id)
