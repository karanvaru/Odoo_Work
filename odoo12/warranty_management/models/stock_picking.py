# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = 'stock.picking'

    warranty_ids = fields.One2many('warranty.registration', 'picking_id', 'Warranty', readonly=True)

    # @api.multi
    # def action_done(self):
    #     res = super().action_done()
    #     try:
    #         for pickObj in self:
    #             _logger.info("*****************Action done here********************") 
    #             pickObj._create_warranty()
    #     except Exception as _:
    #         _logger.info('--Exception--------%r', _)
    #         pass
    #     return res

    def _write(self,val):
        print('*********values******',val)
        if val.get('state','')=='done':
            try:
                for pickObj in self:
                    _logger.info("*****************write here********************") 
                    pickObj._create_warranty()
            except Exception as _:
                _logger.info('--Exception--------%r', _)
                pass

        return super()._write(val)


    @api.multi
    def _create_warranty(self):
        warrantyModel = self.env['warranty.registration']
        _logger.info("*****************create warranty********************") 
        orderObj = self.sale_id
        origin = self.origin
        if origin != orderObj.name:
            return False
        warrantyIds = []
        startDate = datetime.today().date()
        orderLines = self.move_lines
        orderLines = orderLines.filtered(
            lambda obj: obj.product_id.is_warranty)
        for moveLine in self.move_lines:
            # print("*********move lines******",moveLine.product_id,moveLine.product_id.name)
            _logger.info('*****************ProQTY********************%s',moveLine.product_id.name)
            if not (moveLine.product_id.is_warranty):
                continue
            proQty = int(moveLine.product_uom_qty)
            # print("*********ProQTY******",proQty)
            _logger.info('*****************ProQTY********************%s', str(proQty))
            endDate = warrantyModel.get_warranty_end_date(
                moveLine.product_id, startDate)
            moveLineIds = moveLine.move_line_ids
            lotObjs = moveLineIds and moveLineIds.mapped('lot_id') or []
            # print("*********Lot Obj******",lotObjs)
            _logger.info('*****************Lot Obj********************%s', str(lotObjs))
            if lotObjs:
                for lotObj in lotObjs:
                    vals = {
                        'partner_id': orderObj.partner_id.id,
                        'product_id': moveLine.product_id.id,
                        'order_id': orderObj.id,
                        'picking_id': self.id,
                        'prod_qty' : 1,
                        'lot_id' : lotObj.id,
                        'order_line': moveLine.sale_line_id.id,
                        'warranty_start_date' : startDate, 
                        'warranty_end_date': endDate,
                        'state' : 'confirm' if moveLine.product_id.warranty_auto_confirm else'draft'
                    }
                    wrntObj = warrantyModel.with_context(not_onchange=True).sudo().create(vals)
                    self.send_warranty_mail_notification(wrntObj)
                    warrantyIds.append(wrntObj.id)
            else:
                for _ in range(proQty):
                    vals = {
                        'partner_id': orderObj.partner_id.id,
                        'product_id': moveLine.product_id.id,
                        'order_id': orderObj.id,
                        'picking_id': self.id,
                        'prod_qty' : 1,
                        'order_line': moveLine.sale_line_id.id,
                        'warranty_start_date' : startDate, 
                        'warranty_end_date': endDate,
                        'state' : 'confirm' if moveLine.product_id.warranty_auto_confirm else 'draft'
                    }
                    wrntObj = warrantyModel.with_context(not_onchange=True).sudo().create(vals)
                    self.send_warranty_mail_notification(wrntObj)
                    warrantyIds.append(wrntObj.id)
        _logger.info('*****************warranty ids********************%s', str(warrantyIds))
                  
        if warrantyIds:
            orderObj.warranty_ids = [(6, 0, warrantyIds)]
            self.warranty_ids = [(6, 0, warrantyIds)]
        print("------------create warranty executing here--------------")    
        return True


    @api.model
    def send_warranty_mail_notification(self, wrntObj):
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        if wrntObj.state == 'draft':
            tempName = 'email_template_edi_wk_warranty_regi_2'
        else:
            tempName = 'email_template_edi_wk_warranty_regi_3'
        templXmlId = irModelData.get_object_reference(
            'warranty_management', tempName)[1]
        if templXmlId:
            today = datetime.now()
            month = today.strftime("%B")
            day = today.day
            year = today.year
            shipDate = "{} {}, {}".format(month, day, year)
            baseUrl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            lineId = wrntObj.order_line.id
            regLink = baseUrl + "/warranty/register/{}/{}".format(lineId, wrntObj.id)
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            ctx = {
                'wkdate' : shipDate,
                'warrantyref': wrntObj.name,
                'reglink' : regLink,
            }
            mailTmplObj.with_context(
                **ctx).send_mail(wrntObj.id, force_send=True)
        return True