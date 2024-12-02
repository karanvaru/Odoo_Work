import logging
from odoo import fields, models, _

logger = logging.getLogger(__name__)


class StatSrcUser(models.Model):
    _name = 'asterisk_calls.stats_src_user'
    _description = 'Source User Stats'
    _auto = False
    _sql = """
    DROP VIEW IF EXISTS asterisk_calls_stats_src_user CASCADE;
    CREATE VIEW asterisk_calls_stats_src_user AS
    SELECT
        row_number() OVER () AS id,
        src_user,
        SUM(billsec) AS total_duration,
        AVG(billsec) AS average_duration,
        count(*) AS count
     FROM asterisk_calls_call
     WHERE
        src_user IS NOT NULL
        AND date_trunc('month', started) = date_trunc('month', current_date)
        AND date_trunc('year', started) = date_trunc('year', current_date)
            GROUP BY src_user
            ORDER BY total_duration desc;
    """

    def init(self):
        self.env.cr.execute(self._sql)

    src_user = fields.Many2one('res.users', string=_('User'))
    total_duration = fields.Float()
    average_duration = fields.Float()
    count = fields.Integer()


class StatSrcPartner(models.Model):
    _name = 'asterisk_calls.stats_src_partner'
    _description = 'Source Partner Stats'
    _auto = False
    _sql = """
    DROP VIEW IF EXISTS asterisk_calls_stats_src_partner CASCADE;
    CREATE VIEW asterisk_calls_stats_src_partner AS
    SELECT
        row_number() OVER () AS id,
        partner,
        SUM(billsec) AS total_duration,
        AVG(billsec) AS average_duration,
        count(*) AS count
     FROM asterisk_calls_call
     WHERE
        partner IS NOT NULL
        AND dst_user IS NULL
        AND date_trunc('month', started) = date_trunc('month', current_date)
        AND date_trunc('year', started) = date_trunc('year', current_date)
            GROUP BY partner
            ORDER BY total_duration desc;
    """

    def init(self):
        self.env.cr.execute(self._sql)

    partner = fields.Many2one('res.partner')
    total_duration = fields.Float()
    average_duration = fields.Float()
    count = fields.Integer()
