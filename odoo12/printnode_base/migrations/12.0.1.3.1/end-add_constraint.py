# Copyright 2020 VentorTech OU
# License OPL-1.0 or later.

import logging

from psycopg2 import ProgrammingError

_logger = logging.getLogger(__file__)


def migrate(cr, version):
    try:
        cr.execute("""
            ALTER TABLE printnode_action_method
            ADD CONSTRAINT printnode_action_method_unique_action_method UNIQUE (model_id,method)
        """)
    except ProgrammingError as ex:
        _logger.debug(ex)
