from .import models
from .import controllers


def do_post_install(cr, registry):
    from odoo import api, SUPERUSER_ID
    import logging
    logger = logging.getLogger(__name__)

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Create servers for agents
        for agent in env['remote_agent.agent'].search([]):
            server = env['asterisk_base.server'].search(
                [('agent', '=', agent.id)])
            if not server:
                logger.info(
                    'Creating Asterisk server for agent %s', agent.system_name)
                env['asterisk_base.server'].create({
                    'agent': agent.id,
                    'name': agent.system_name})

        users = env['asterisk_common.user'].search([])
        for user in users:
            # Set user's server.
            if not user.server:
                server = env['asterisk_base.server'].search(
                    [('agent', '=', agent.id)])
                user.server = server
            # Create user's extensions.
            if not user.extension:
                logger.info('Creating extension %s.', user.exten)
                env['asterisk_base.extension'].create_extension_for_obj(user)
    return True
