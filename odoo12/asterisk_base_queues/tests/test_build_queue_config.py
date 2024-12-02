from odoo.tests.common import TransactionCase


class QueueConfigTest(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.queue = self.env.ref('asterisk_base_queues.sales_queue')
        self.admin = self.env.ref('base.user_admin')
        self.demo = self.env.ref('base.user_demo')
        self.aster_admin = self.env.ref('asterisk_base_queues.user_admin')
        self.aster_demo = self.env.ref('asterisk_common.user_demo')
        self.server = self.env.ref('asterisk_base.default_server')
        return result

    def test_sales_queue_config(self):
        queue_config = self.env['asterisk_base.conf'].get_or_create(
            self.server.id, 'queues_odoo.conf'
        )
        self.assertEqual(
            queue_config.content,
            '[general](+)\n; Queue Settings\nautopause=True\n'
            'monitor_type=mix_monitor\nmonitor_format=wav\n'
            'shared_lastcall=True\nshared_lastcall=True\n'
            'default_ring_timeout=15\n;\n['
            'Sales]\nstrategy=ringall\nringinuse=no\nmusicclass=default'
            '\nmaxlen=0\nservicelevel=60\ntimeout=15\nreportholdtime=no'
            '\nleavewhenempty=no\njoinempty=yes\n; MEMBERS\n')
        self.env['asterisk_base_queues.queue_member'].create({
            'user': self.aster_admin.id,
            'queue': self.queue.id,
            'is_static': True
        })
        self.assertEqual(
            queue_config.content,
            '[general](+)\n; Queue Settings\nautopause=True\nmonitor_type'
            '=mix_monitor\nmonitor_format=wav\nshared_lastcall=True'
            '\nshared_lastcall=True\ndefault_ring_timeout=15\n;\n['
            'Sales]\nstrategy=ringall\nringinuse=no\nmusicclass=default'
            '\nmaxlen=0\nservicelevel=60\ntimeout=15\nreportholdtime=no'
            '\nleavewhenempty=no\njoinempty=yes\n; MEMBERS\nmember => '
            'SIP/1001\n')
        self.env['asterisk_base_queues.queue'].create({
            'name': 'Sales2',
            'exten': 102
        })
        self.assertEqual(
            queue_config.content,
            '[general](+)\n; Queue Settings\nautopause=True\nmonitor_type'
            '=mix_monitor\nmonitor_format=wav\nshared_lastcall=True'
            '\nshared_lastcall=True\ndefault_ring_timeout=15\n;\n['
            'Sales]\nstrategy=ringall\nringinuse=no\nmusicclass=default'
            '\nmaxlen=0\nservicelevel=60\ntimeout=15\nreportholdtime=no'
            '\nleavewhenempty=no\njoinempty=yes\n; MEMBERS\nmember => '
            'SIP/1001\n;\n[Sales2]\nstrategy=ringall\nringinuse=no\nmusicclass'
            '=default\nmaxlen=0\nservicelevel=60\ntimeout=15\nreportholdtime'
            '=no\nleavewhenempty=no\njoinempty=yes\n; MEMBERS\n')
