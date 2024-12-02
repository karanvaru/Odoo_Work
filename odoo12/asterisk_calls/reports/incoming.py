import logging
from odoo import fields, models, _


logger = logging.getLogger(__name__)


class StatDstUser(models.Model):
    _name = 'asterisk_calls.stats_dst_user'
    _description = 'Destination User Stats'
    _auto = False
    _sql = """
    DROP VIEW IF EXISTS asterisk_calls_stats_dst_user CASCADE;
    CREATE VIEW asterisk_calls_stats_dst_user AS
    SELECT
        row_number() OVER () AS id,
        dst_user,
        SUM(billsec) AS total_duration,
        AVG(billsec) AS average_duration,
        count(*) AS count
     FROM asterisk_calls_call
     WHERE
        dst_user IS NOT NULL
        AND date_trunc('month', started) = date_trunc('month', current_date)
        AND date_trunc('year', started) = date_trunc('year', current_date)
            GROUP BY dst_user
            ORDER BY total_duration desc;
    """

    def init(self):
        self.env.cr.execute(self._sql)

    dst_user = fields.Many2one('res.users', string=_('User'))
    total_duration = fields.Float()
    average_duration = fields.Float()
    count = fields.Integer()


class StatDstPartner(models.Model):
    _name = 'asterisk_calls.stats_dst_partner'
    _description = 'Destination Partner Stats'
    _auto = False
    _sql = """
    DROP VIEW IF EXISTS asterisk_calls_stats_dst_partner CASCADE;
    CREATE VIEW asterisk_calls_stats_dst_partner AS
    SELECT
        row_number() OVER () AS id,
        partner,
        SUM(billsec) AS total_duration,
        AVG(billsec) AS average_duration,
        count(*) AS count
     FROM asterisk_calls_call
     WHERE
        partner IS NOT NULL
        AND src_user IS NULL
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
