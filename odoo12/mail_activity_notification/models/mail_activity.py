# -*- coding: utf-8 -*-

import logging

from datetime import date
from itertools import groupby

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class mail_activity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    @api.depends("user_id")
    def _compute_url_user(self):
        """
        Compute method for url_user

        Methods:
         * _get_signup_url_for_action of res.partner
        """
        for activity in self.sudo():
            url_user = False
            if activity.user_id:
                url_user = activity.user_id.partner_id.with_context(signup_valid=True)._get_signup_url_for_action(
                    view_type="form",
                    model=activity.res_model,
                    res_id=activity.res_id,
                )[activity.user_id.partner_id.id]
                url_user = url_user.replace('res_id', 'id')
            activity.url_user = url_user


    url_user = fields.Char(
        compute=_compute_url_user,
        store=True,
    )

    @api.model
    def cron_notify(self):
        """
        Find all overdue activities with types in which is_notify attribute is in True.

        Methods:
         * render_template of 'mail.template'
         * build_email from 'ir.mail_server'
         * send_email from 'ir.mail_server'

        Extra info:
         * We purposefully do not attach email to any object
        """
        context = self.env.context.copy()
        context.update({'date': date,})
        types = self.env['mail.activity.type'].search([('is_notify', '=', True)])
        today_date = fields.Date.today()
        mail_activities = self.env["mail.activity"].search([
            ('date_deadline', '<=', today_date),
            ('activity_type_id', 'in', types.ids),
            ('user_id', '!=', False),
        ])
        user_ids = mail_activities.mapped("user_id")
        for user in user_ids:
            try:
                user_task_ids = mail_activities.filtered(lambda acti: acti.user_id == user)
                context.update({"task_ids": user_task_ids})
                # Ugly hack to force Odoo translate template
                template = self.with_context(lang=user.partner_id.lang).env.ref(
                    'mail_activity_notification.mail_activity_notification_template'
                )
                body_html = template.with_context(context)._render_template(
                    template.body_html,
                    'res.users',
                    user.id,
                )
                subject =template.with_context(context).subject
                mail_server = self.env['ir.mail_server']
                message = mail_server.build_email(
                    email_from=template.email_from or self.env.user.email,
                    subject=subject,
                    body=body_html,
                    subtype='html',
                    email_to=[user.partner_id.email],
                )
                mail_server.send_email(message)
            except Exception as e:
                _logger.error("Daily reminder is not sent to user {}. Reason: {}".format(user.name, e))
