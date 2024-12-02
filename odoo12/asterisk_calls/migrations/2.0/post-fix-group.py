import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    try:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})
            u = env['res.users'].search([('login', '=', 'asterisk_agent')])
            if u and not u.has_group(
                                'asterisk_common.group_asterisk_agent'):
                logger.info(
                    'ADDING asterisk_agent user to Asterisk Agent group')
                g = env['ir.model.data'].get_object('asterisk_common',
                                                    'group_asterisk_agent')
                g.users = [(4, u.id)]
    except:
        logger.exception('Asterisk Calls 2.0 migration non-critical error')
