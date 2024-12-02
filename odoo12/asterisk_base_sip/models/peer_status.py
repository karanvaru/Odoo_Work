from datetime import datetime, timedelta
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
import logging
from psycopg2 import OperationalError
from odoo import models, fields, api


DEFAULT_SIP_PEER_STATUS_KEEP_HOURS = 24  # The number of days to keep statuses

logger = logging.getLogger(__name__)


class SipPeerStatus(models.Model):
    _name = 'asterisk_base_sip.peer_status'
    _log_access = False
    _order = 'create_date desc'
    _rec_name = 'status'
    _description = "SIP Peer Status"

    create_date = fields.Datetime(required=True, index=True)
    peer = fields.Many2one(comodel_name='asterisk_base_sip.peer',
                           required=True, ondelete='cascade')
    peer_name = fields.Char()
    status = fields.Char(index=True, required=True)
    cause = fields.Char(index=True)
    address = fields.Char(index=True)
    useragent = fields.Char(index=True)
    created = fields.Char(compute='_get_created')

    @api.model
    def update_peer_status(self, values):
        # Called from the Agent
        if values.get('Event') != 'PeerStatus' or values.get(
                'ChannelType') != 'SIP':
            logger.error('Wrong event for Asterisk SIP peer status: {}'.format(
                values))
            return False
        channel, peer_name = values.get('Peer', '/').split('/')
        self.env.cr.execute(
            'SELECT id FROM asterisk_base_sip_peer WHERE '
            'name = %s FOR UPDATE NOWAIT', [peer_name])
        peer_id = self.env.cr.fetchone()
        if not peer_id:
            logger.warning('Did not find peer {} to update status.'.format(
                peer_name
            ))
            return False
        get = values.get
        self.env['asterisk_base_sip.peer_status'].create({
            'create_date': datetime.utcnow(),
            'peer': peer_id[0],
            'peer_name': peer_name,
            'status': get('PeerStatus', False),
            'cause': get('Cause', False),
            'address': get('Address', False),
            'useragent': get('UserAgent'),
        })
        return True

    @api.model
    def vacuum(self, hours=DEFAULT_SIP_PEER_STATUS_KEEP_HOURS):
        BULK_SIZE = 1000  # Unlink by blocks of 1000 records
        while True:
            try:
                records = self.env['asterisk_base_sip.peer_status'].search(
                    [('create_date', '<', fields.Datetime.to_string(
                     datetime.utcnow() - timedelta(hours=hours)))],
                    limit=BULK_SIZE)
                if records:
                    logger.info(
                        'Deleting %s peer statuses.', len(records))
                    records.unlink()
                    self.env.cr.commit()
                else:
                    break
            except Exception as e:
                logger.info('delete_expired error: %s', str(e))
                break

    def _get_created(self):
        for rec in self:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    try:
                        humanize.i18n.activate(to_translate)
                        rec.created = humanize.naturaltime(
                            fields.Datetime.from_string(rec.create_date))                        
                    except:
                        rec.created = rec.create_date
            else:
                rec.created = rec.create_date
