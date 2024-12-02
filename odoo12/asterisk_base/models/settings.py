import logging
from odoo import fields, models, api, addons, _
from odoo.tools import ormcache


logger = logging.getLogger(__name__)


class BaseSettings(models.Model):
    _inherit = 'asterisk_common.settings'

    default_exten_length = fields.Integer(
        required=True, default=3, string='Default extension length')
    default_exten_start = fields.Integer(default=100)

    def build_all_conf(self):
        # Iterate over all Asterisk Base modules and build conf for all models.
        for app in filter(
                lambda x: x.startswith('asterisk_base'), dir(addons)):
            models = dir(eval('addons.{}.models'.format(app)))
            for model in filter(lambda x: not x.startswith('_'), models):
                app_model = '{}.{}'.format(app, model)
                if app_model in self.env and hasattr(
                        self.env[app_model], 'build_conf'):
                    logger.info('Building conf for %s.%s', app, model)
                    self.env['{}.{}'.format(app, model)].build_conf()
        
    @api.model
    def on_agent_start(self):
        super(BaseSettings, self).on_agent_start()
        # Upload all conf files to server
        server = self.env.user.asterisk_server
        # Update security rules
        self.env['asterisk_base.access_list'].update_rules(server_id=server.id)
        return True
