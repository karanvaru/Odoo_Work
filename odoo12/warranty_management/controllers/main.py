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
import werkzeug

from odoo import http, tools, _
from odoo.http import content_disposition, request, serialize_exception

from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.sale.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class Binary(http.Controller):
    @http.route('/web/binary/wnty_dwnld', type='http', auth="public")
    def download_document(self, name, field, id, **kw):
        wrntyId = int(id)
        wrntyHistory = request.env['warranty.history'].sudo().browse(wrntyId)
        res = wrntyHistory.read([field])
        filecontent = base64.b64decode(res[0].get(field) or '')
        if not filecontent:
            return request.not_found()
        filename = name.replace("/", '_')
        return request.make_response(filecontent,
                    [('Content-Type', 'application/octet-stream'),
                        ('Content-Disposition', content_disposition(filename))])


class WebsiteSale(WebsiteSale):


    @http.route('/my/warranty/renew/<int:warranty_id>', type='http', auth="public", website=True)
    def warranty_renew(self, warranty_id=0, access_token=None, **kw):
        renwProdId = request.env['ir.config_parameter'].sudo().get_param(
            'warranty_management.renewal_prod'
        )
        warrantyId = int(warranty_id)
        wrntyModel = http.request.env['warranty.registration']
        warntObj = wrntyModel.sudo().browse(warrantyId)
        renewOrdr = request.website.sale_get_order(force_create=1)
        renewOrdr.origin = warntObj.name
        renewOrdr._cart_update(
            product_id=renwProdId and int(renwProdId),
            add_qty=1,
            )
        for orderLine in renewOrdr.order_line.sudo():
            if orderLine.product_id.id == int(renwProdId or 0):
                lineName = "Warranty ref #{} \nFor Product {}, Order ref#{}".format(
                    warntObj.name, warntObj.product_id.name, warntObj.order_id.name)
                orderLine.write({
                    'price_unit' : warntObj.product_id.renewal_cost,
                    'to_renew_wrnty' : warntObj.id,
                    'name' : "Warranty Renew:\n{}".format(lineName)
                })
                break
        return request.redirect("/shop/cart")


class CustomerPortal(CustomerPortal):


    @http.route(['/my/warranty/pdf/<int:warranty_id>'], type='http', auth="public", website=True)
    def print_my_warranty(self, warranty_id, access_token=None, **kw):
        pdf = request.env.ref('warranty_management.action_report_warranty').sudo(
        ).render_qweb_pdf([warranty_id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'attachment'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/warranty/modal/'], type='json', auth="user", methods=['POST'], website=True)
    def warranty_reg_modal(self, ol, modal):
        tempId = 'warranty_management.{}'.format(modal)
        lineObj = request.env['sale.order.line'].sudo().browse(ol)
        return request.env.ref(tempId).render({
            'orderline': lineObj,
        }, engine='ir.qweb')

    @http.route(['/check/serial/'], type='json', auth="user", methods=['POST'], website=True)
    def warranty_check_serial(self, serial_number, line_id):
        if not isinstance(serial_number, list):
            serial_number = [serial_number]
        lineObj = request.env['sale.order.line'].sudo().browse(int(line_id))
        stockMoves = lineObj.mapped('move_ids')
        stockMoveLines = stockMoves.mapped('move_line_ids')
        srNumbers = []
        if stockMoveLines:
            lotIds = stockMoveLines.mapped('lot_id')
            for serialN in serial_number:
                lotId = next(
                    (lot for lot in lotIds if lot.name == serialN), False)
                if lotId:
                    srNumbers.append(lotId.id)
        if len(srNumbers) == len(serial_number):
            return srNumbers
        else:
            return []

    @http.route(['/check/serial/more'], type='json', auth="user", methods=['POST'], website=True)
    def warranty_check_serial_more(self, serial_number, line_id):
        serailN = list(serial_number.values())
        res = self.warranty_check_serial(serailN, line_id)
        if res:
            classNames = serial_number.keys()
            classNames = [key.replace('lot_', 'validlot_') for key in classNames]
            vals = dict(zip(classNames, res))
            return vals
        return {}

    @http.route(['/register/warranty/'], type='http', auth="user", methods=['POST'], website=True)
    def register_warranty_with_serial(self, **post):
        validLot = [int(lot) for k,lot in post.items() if k.startswith('validlot_')]
        wrntReg = request.env['warranty.registration'].sudo()
        orderId = int(post.get("order_id"))
        prodId = int(post.get("product_id"))
        lineId = int(post.get("ol_id"))
        orderObj = request.env['sale.order'].sudo().browse(orderId)
        prodObj = request.env['product.product'].sudo().browse(prodId)
        startDate = orderObj.create_date
        endDate = wrntReg.get_warranty_end_date(
            prodObj, startDate)
        for lot in validLot:
            vals = {
                'partner_id': int(post.get("partner_id")),
                'product_id': prodId,
                'order_id': orderId,
                'lot_id': lot,
                'order_line': lineId,
                'warranty_end_date': endDate,
                'notes': 'Warranty Regsitred by customer'
            }
            wrntReg.with_context(not_onchange=True).create(vals)
        return werkzeug.utils.redirect(request.httprequest.referrer)

    @http.route(['/my/warranty/<int:orderline>'], type='http', auth="user", website=True)
    def warranty_followup(self, orderline=None, access_token=None, **kw):
        values = self.get_warranty_info(orderline, access_token, **kw)
        return request.render("warranty_management.wwm_page", values)

    def get_warranty_info(self, orderline, access_token, **kwargs):
        oline = request.env['sale.order.line'].sudo().browse(orderline)
        orderObj = oline.order_id
        totalQty = sum(
            ol.product_uom_qty for ol in orderObj.order_line if ol.product_id.is_warranty)
        return {
            'ol': oline,
            'order': orderObj,
            'total_qty': totalQty,
            'bootstrap_formatting': True,
            'report_type': 'html',
        }

    @http.route(['/register/now/<int:wrntid>'], type='http', auth="user", website=True)
    def register_now(self, wrntid=None, access_token=None, **kw):
        wrntyObj = request.env['warranty.registration'].sudo().browse(wrntid)
        wrntyObj.write({'state' : 'confirm'})
        wrntyObj.send_product_reg_mail(wrntyObj)
        orderline = wrntyObj.order_line
        values = self.get_warranty_info(orderline.id, access_token, **kw)
        return request.render("warranty_management.wwm_page", values)


    @http.route([
        '/warranty/register/<int:orderline>/<int:wrntid>'], type='http', auth="user", website=True)
    def register_product(self, orderline=None, wrntid=None, **kwargs):
        values = {'submit_msg' : 'no'}
        oline = request.env['sale.order.line'].sudo().browse(orderline)
        wrntyObj = request.env['warranty.registration'].sudo().browse(wrntid)
        values['wanty_ref'] = wrntyObj.name
        if wrntyObj.state != 'draft':
            if wrntyObj.state in ['confirm', 'done']:
                values['reg_msg'] = 'Requested Product is already registered!'
            else:
                values['reg_msg'] = 'Requested Product can not be registered!'

        if kwargs.get('submitted') == "1":
            values['submit_msg'] = 'yes'
            wrntyObj.write({'state' : 'confirm'})
            wrntyObj.send_product_reg_mail(wrntyObj)

        values.update({
            'oline': oline,
            'wrnty_obj' : wrntyObj,
        })
        return request.render("warranty_management.warranty_reg_form", values)


