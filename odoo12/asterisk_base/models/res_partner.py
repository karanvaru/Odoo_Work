import logging
from odoo import models, fields, api, tools, _

logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    def write(self, values):
        try:
            # Check if email is changed and change also in user settings
            if values.get('email'):
                for rec in self:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', rec.id)])
                    for asterisk_user in user.asterisk_users:
                        if asterisk_user.vm_email == rec.email:
                            # Change also VM email
                            asterisk_user.vm_email = values['email']
            if values.get('mobile'):
                for rec in self:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', rec.id)])
                    for asterisk_user in user.asterisk_users:
                        if asterisk_user.cf_on_busy_number == rec.mobile:
                            # Change also VM email
                            asterisk_user.cf_on_busy_number = \
                                values['mobile']
                        if asterisk_user.cf_on_unavail_number == rec.mobile:
                            # Change also VM email
                            asterisk_user.cf_on_unavail_number = \
                                values['mobile']
                        if asterisk_user.cf_uncond_number == rec.mobile:
                            # Change also VM email
                            asterisk_user.cf_uncond_number = \
                                values['mobile']
            if values.get('phone'):
                for rec in self:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', rec.id)])
                    for asterisk_user in user.asterisk_users:
                        if asterisk_user.cf_on_busy_number == rec.phone:
                            # Change also VM email
                            asterisk_user.cf_on_busy_number = \
                                values['phone']
                        if asterisk_user.cf_on_unavail_number == rec.phone:
                            # Change also VM email
                            asterisk_user.cf_on_unavail_number = \
                                values['phone']
                        if asterisk_user.cf_uncond_number == rec.phone:
                            # Change also VM email
                            asterisk_user.cf_uncond_number = \
                                values['phone']
        except Exception:
            logger.exception('Res partner write error:')
        finally:
            return super(Partner, self).write(values)
