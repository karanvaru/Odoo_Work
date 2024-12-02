import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    try:
        cr.execute("""ALTER TABLE asterisk_base_conf DROP CONSTRAINT IF EXISTS asterisk_base_conf_name_server_idx""")
        cr.commit()
    except:
        logger.exception('Asterisk Base 1.6 asterisk_base_conf_name_server_idx  remove error.')

