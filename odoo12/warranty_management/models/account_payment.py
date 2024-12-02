# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import base64
import logging
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = "account.payment"


    @api.multi
    def post(self):
        res = super().post()
        histryModel = self.env['warranty.history']
        for rec in self:
            invObjs = rec.invoice_ids
            for invLine in invObjs.mapped('invoice_line_ids'):
                saleLinObjs = invLine.sale_line_ids
                for saleLineObj in saleLinObjs:
                    if saleLineObj.to_renew_wrnty:
                        wrntyObj = saleLineObj.to_renew_wrnty
                        histryObjs = histryModel.search([('warranty_id', '=', wrntyObj.id)])
                        sortedObjs = sorted(histryObjs, key=lambda x: x.old_end_date)
                        newRef = sortedObjs[-1].name
                        if not sortedObjs[-1].is_fresh:
                            toAppend = newRef.split('/')[-1]
                            toAppend = str((int(toAppend) + 1)).zfill(2)
                            newRef = newRef[:-2] + toAppend
                        else:
                            newRef += '/01'
                        crntExpireDate = wrntyObj.warranty_end_date
                        dyasLeft = saleLineObj.days_difference(crntExpireDate)
                        if dyasLeft > 0:
                            newStartDate = wrntyObj.warranty_end_date
                        else:
                            newStartDate = datetime.date.today()
                        expirDate = self.get_expire_date(wrntyObj.product_id, newStartDate)
                        histryObjs.write({'state' : 'expired'})
                        histryObj = histryModel.create({
                            'name' : newRef,
                            'invoice_id' : invLine.invoice_id.id,
                            'warranty_id' : wrntyObj.id,
                            'state' : "confirm",
                            'old_start_date' : newStartDate,
                            'old_end_date' : expirDate,
                        })
                        wrntyObj.write({
                            'name' : newRef,
                            'warranty_start_date' : newStartDate,
                            'warranty_end_date' : expirDate,
                        })
                        pdf = self.env.ref('warranty_management.action_report_warranty_rec').sudo(
                        ).render_qweb_pdf([histryObj.id])[0]
                        base64Data = base64.b64encode(pdf)
                        histryObj.datas = base64Data
                        self.send_warranty_renew_mail_notification(wrntyObj)
        return res


    @api.model
    def get_expire_date(self, productObj, startDate):
        wPeriod = productObj.renewal_period
        wUnit = productObj.renewal_unit
        wDict = {wUnit: wPeriod}
        endDate = startDate + relativedelta(**wDict)
        return endDate


    @api.model
    def send_warranty_renew_mail_notification(self, wrntObj):
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        tempName = 'email_template_warranty_renewal'
        templXmlId = irModelData.get_object_reference(
            'warranty_management', tempName)[1]
        if templXmlId:
            extendDate = wrntObj.warranty_end_date
            month = extendDate.strftime("%B")
            day = extendDate.day
            year = extendDate.year
            tillDt = "{} {}, {}".format(month, day, year)
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            ctx = {
                'extendate' : tillDt,
                'warrantyref': wrntObj.name,
            }
            mailTmplObj.with_context(
                **ctx).send_mail(wrntObj.id, force_send=True)
        return True