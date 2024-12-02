from odoo.tests import common
from odoo.tests import tagged
from odoo.exceptions import ValidationError
from odoo.addons.asterisk_base.models.server import AsteriskServer


@tagged('extension', 'post_install')
class TestExtension(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestExtension, cls).setUpClass()
        # Create a server
        cls.server = cls.env['asterisk_base.server'].create(
            {'system_name': 'test', 'name': 'Test'})
        # We take server for object as we does not care here really.
        cls.extension = cls.env['asterisk_base.extension'].with_context(
            {'no_build_conf': True}).create({
            'server': cls.server.id,
            'number': '100',
            'app': 'asterisk_base',
            'model': 'server',
            'obj_id': cls.server.id,
        })

    def test_app_model(self):
        self.assertEqual(self.extension.app_model, 'asterisk_base.server')

    def test_check_number(self):
        with self.assertRaises(ValidationError) as context:
            extension2 = self.env['asterisk_base.extension'].with_context(
                {'no_build_conf': True}).create({
                'server': self.server.id,
                'number': '100',
                'app': 'asterisk_base',
                'model': 'server',
                'obj_id': self.server.id,
            })
        self.assertTrue("This extension number is already used!",
                        context.exception)

    def test_open_extension(self):
        self.assertEqual(
            self.extension.open_extension(),
            {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_base.server',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'res_id': self.server.id,
            })

    def test_build_conf(self):
        ext = self.env['asterisk_base.extension'].browse(self.extension.id)
        # Monkey patch render_extension as it does not exist on server object
        AsteriskServer.render_extension = lambda x: ''
        conf = self.env['asterisk_base.conf'].get_or_create(self.server.id,
                                                            'extensions.conf',
                                                            content='')
        ret = ext.build_conf()
        self.assertEqual(ret, True)
