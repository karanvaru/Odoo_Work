import json
import logging
from odoo import models, fields, api, _
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


DEFAULT_EXPIRE_SECONDS = 3600 * 24  # One day


class Cache(models.Model):
    """
    Simple key/value storage with expiration feature.
    Duplicate keys are accepted but get returns the first key.
    """
    # TODO: ORM Cache

    _name = 'kv_cache.cache'
    _description = 'Cache Impementation'
    _log = False  # TODO: Check that auto disables special fields

    key = fields.Char(required=True, index=True)
    tag = fields.Char(required=True, default='/', index=True)
    value = fields.Char(required=True)
    expire = fields.Datetime(required=True, index=True)

    _sql_constraints = [
        ('tag_key_uniq', 'unique (tag,key)',
            _('The key/tag must be unique !')),
    ]

    @api.model
    def put(self, key, value, tag='/', expire=DEFAULT_EXPIRE_SECONDS,
            serialize=None):
        self.do_expiration()
        try:
            expire_time = (datetime.utcnow() + timedelta(
                seconds=expire)).strftime('%Y-%m-%d %H:%M:%S')
            # Check serialize option
            if serialize == 'json':
                value = json.dumps(value)
            with self.env.cr.savepoint():
                self.create({
                    'key': key,
                    'tag': tag,
                    'value': value,
                    'expire': expire_time,
                })
                logger.debug('CACHE PUT KEY: %s VALUE: %s', key, value)
        except Exception as e:
            if 'kv_cache_cache_tag_key_uniq' in str(e):
                # Value already there
                logger.debug('CACHE PUT DUPLICATE KEY %s TAG %s', key, tag)
            else:
                logger.exception('[ODOO_ERROR] CACHE PUT ERROR:')

    @api.model
    def get(self, key, tag='/', clean=False, serialize=None):
        try:
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            res = self.search([('tag', '=', tag), ('key', '=', key),
                               ('expire', '>=', now)])
            if res:
                val = res[0].value
                # Check for serialize
                if serialize == 'json':
                    val = json.loads(val)
                if clean:
                    res.unlink()
                logger.debug('CACHE GET KEY: %s, CLEAN: %s, VALUE: %s.',
                             key, clean, val)
                return val
            else:
                logger.debug('CACHE TAG %s KEY %s NOT FOUND', tag, key)
                return {} if serialize == 'json' else False
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE GET ERROR:')
            return {} if serialize == 'json' else False

    @api.model
    def delete(self, key, tag='/'):
        self.do_expiration()
        try:
            with self.env.cr.savepoint():
                res = self.search([('tag', '=', tag), ('key', '=', key)])
                if res:
                    res.unlink()
                else:
                    logger.debug('KEY %s NOT FOUND UNDER TAG: %s', key, tag)
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE DELETE ERROR:')

    @api.model
    def do_expiration(self):
        try:
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            with self.env.cr.savepoint():
                expired_recs = self.search(
                    [('expire', '<', now)])
                logger.debug('CACHE VACUUM %s RECORDS', len(expired_recs))
                expired_recs.unlink()
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE DO EXPIRATION ERROR:')
