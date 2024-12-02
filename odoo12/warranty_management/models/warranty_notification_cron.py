# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

import datetime
from dateutil.relativedelta import relativedelta
import logging

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class WarrantyNotificationCron(models.TransientModel):
    _name = 'warranty.notification.cron'


    @api.model
    def _send_notification(self):
        IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo()
        sendNotification = IrConfigPrmtrSudo.get_param(
            'warranty_management.warranty_expire_notification')
        if sendNotification:
            daysBefore = int(IrConfigPrmtrSudo.get_param('warranty_management.days_before'))
            crntDate = datetime.date.today()
            expDate = crntDate + relativedelta(days=daysBefore)
            domain = [
                ('state', 'not in', ['draft', 'cancel', 'expired']),
                ('warranty_end_date', '=', expDate)
            ]
            wrntObjs = self.env['warranty.registration'].search(domain)
            for wrntObj in wrntObjs:
                self.send_mail_notification(wrntObj)
        self._check_warranty()
        return True

    @api.model
    def send_mail_notification(self, wrntObj):
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        templXmlId = irModelData.get_object_reference(
            'warranty_management', 'email_warranty_expire_notification')[1]
        if templXmlId:
            today = datetime.date.today()
            month = today.strftime("%B")
            day = today.day
            year = today.year
            tdDate = "{} {}, {}".format(month, day, year)
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            ctx = {
                'wkemail': wrntObj.partner_id.email,
                'wkdate': tdDate,
                'lang': wrntObj.partner_id.lang,
            }
            mailTmplObj.with_context(
                **ctx).send_mail(wrntObj.id, force_send=True)
        return True


    @api.model
    def _check_warranty(self):
        wrntyObjs = self.env['warranty.registration'].search([
            ('state', '=', 'confirm')])
        for wrntyObj in wrntyObjs:
            diffdate = wrntyObj.warranty_end_date - datetime.date.today()
            dayLeft = diffdate.days
            if dayLeft < 0:
                wrntyObj.write({'state' : 'expired'})
                wrntyObj.warranty_history_ids.write({'state' : 'expired'})
        return True