# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class PreorderNotification(models.TransientModel):
    _name="preorder.notification.wizard"


    @api.model
    def default_get(self,default_fields):
        res = super(PreorderNotification,self).default_get(default_fields)
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        line_ids = order_id.order_line.filtered(lambda r: r.is_preorder and not r.preorder_notify)
        res['line_ids'] = line_ids.ids
        return res


    line_ids = fields.Many2many("sale.order.line")
    empty_line = fields.Boolean()

    @api.multi
    def send_perorder_stock_mail(self):
        for rec in self:
            for line in rec.line_ids:
                if not line.preorder_notify:
                    template = self.env['ir.model.data'].xmlid_to_object(
                        'website_preorder.pre_order_email_template_edi_sale')
                    if template:
                        mail_id = template.send_mail(
                            line.id, True)
                        line.preorder_notify = True
                        if mail_id:
                            mail_obj = self.env["mail.mail"].browse(mail_id)
                            _logger.info("========mail_obj====%r=====================",mail_obj.body_html)
                            line.order_id.message_post(body=mail_obj.body_html)



    @api.onchange('line_ids')
    def delete_notify_line(self):
        if len(self.line_ids.ids) == 0:
            self.empty_line = True
