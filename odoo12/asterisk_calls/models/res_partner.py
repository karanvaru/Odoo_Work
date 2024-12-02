import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    asterisk_calls_count = fields.Integer(compute='_get_asterisk_calls_count')
    recorded_calls = fields.One2many(
        'asterisk_calls.call', 'partner',
        domain=[('recording_filename', '!=', False)])

    def _get_asterisk_calls_count(self):
        for rec in self:
            if rec.is_company:
                rec.asterisk_calls_count = self.env[
                    'asterisk_calls.call'].sudo().search_count(
                    ['|', ('partner', '=', rec.id),
                          ('partner.parent_id', '=', rec.id)])
            else:
                rec.asterisk_calls_count = self.env[
                    'asterisk_calls.call'].sudo().search_count(
                    [('partner', '=', rec.id)])

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        try:
            if self.env.context.get('create_call_partner'):
                call = self.env[
                    'asterisk_calls.call'].browse(
                    self.env.context['create_call_partner'])
                call.partner = res.id
        except Exception as e:
            logger.exception(e)
        finally:
            return res
