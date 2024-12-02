from .import models
from .import wizards


def do_post_install(cr, registry):
    from odoo import api, SUPERUSER_ID
    import logging
    logger = logging.getLogger(__name__)    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Notify Agent to reload events.
        logger.info('Reloading Asterisk Agent events.')
        env['asterisk_common.settings'].reload_events()
        # Create SIP peers for existing users.
        users = env['asterisk_common.user'].search([])
        default_channel = env['asterisk_common.settings'].get_param(
            'default_sip_channel_type', 'sip')
        for user in users:
            user_channels = [
                k.channel for k in user.channels if 'SIP' in k.channel.upper()]
            for ch in user_channels:
                env['asterisk_common.user_channel'].search(
                    [('channel', '=', ch)]).with_context(
                    from_peer=True).unlink()
                logger.info('Creating SIP channel %s.', ch)
                ch_type, ch_name = ch.split('/')
                if 'SIP' not in ch_type.upper():
                    # Ommit Local channels
                    continue
                env['asterisk_base_sip.peer'].create({
                    'server': user.server.id,
                    'user': user.id,
                    'name': ch_name,
                    'host': 'dynamic',
                    'peer_type': 'user',
                    'channel_type': default_channel})
    return True


def do_uninstall(cr, registry):
    from odoo import api, SUPERUSER_ID
    import logging
    logger = logging.getLogger(__name__)    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Notify Agent to reload events.
        logger.info('Reload Asterisk Agent events.')
        env['asterisk_common.settings'].reload_events()
