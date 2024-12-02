import json
import logging
from odoo import models, fields, api, _
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class StasisApp(models.Model):
    _name = 'asterisk_base.stasis_app'
    _description = 'Stasts Application'

    name = fields.Char(required=True)
    args = fields.Char()

    @api.model
    def on_start(self, event):
        logger.debug('Stasis start: %s', json.dumps(
                                                            event, indent=2))
        system_name = event['channel']['id'].split('-')[0]
        with self.env['asterisk_base.server'].get_server_proxy(
                                                system_name, 'ari') as proxy:
            channel = event['channel']['id']
            r1 = proxy.request('channels', 'answer', 
                              {'channelId': channel})
            logger.info('---------------- %s', r1)
            r2 = proxy.request('channels', 'hangup', 
                              {'channelId': channel})
            logger.info('---------------- %s', r2)
        return True

    @api.model
    def create(self, vals):
        ret = super(StasisApp, self).create(vals)
        self.env['asterisk_base.event'].create({
            'event_type': 'ari',
            'event_name': 'StasisStart',
            'target_model': self._name,
            'target_method': 'on_start',
        })
        return ret

    
    def unlink(self):
        self.env['asterisk_base.event'].search([
            ('event_name', '=', 'StasisStart'),
            ('event_type', '=', 'ari'),
            ('target_model', '=', self._name),
            ('target_method', '=', 'on_start')
        ]).unlink()
        return super(StasisApp, self).unlink()
