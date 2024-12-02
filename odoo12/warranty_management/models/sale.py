# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty_ids = fields.One2many('warranty.registration', 'order_id', 'Warranty', readonly=True)


    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        res = super()._cart_update(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        lineId = res.get('line_id')
        if lineId not in self.sudo().order_line.ids:
            return res
        if lineId:
            lineObj = self.env['sale.order.line'].sudo().browse(lineId)
            if lineObj.to_renew_wrnty:
                product = self.env['product.product'].sudo().browse(product_id)
                prod = lineObj.to_renew_wrnty.product_id
                pu = prod.renewal_cost
                pu = self.env['account.tax'].sudo()._fix_tax_included_price_company(
                    pu, product.taxes_id, lineObj.tax_id, self.company_id)
                lineObj.price_unit = pu
        return res

    @api.multi
    def check_warranty(self):
        existWrnty = False
        for orderLine in self.order_line:
            wrntyObjs = self.env['warranty.registration'].search([
                ('order_line', '=', orderLine.id)])
            if wrntyObjs:
                existWrnty = True
                break
        return existWrnty



    @api.multi
    def _create_warranty(self):
        warrantyModel = self.env['warranty.registration']
        for order in self:
            warrantyIds = []
            orderLines = order.order_line
            orderLines = orderLines.filtered(
                lambda obj: obj.product_id.is_warranty)
            for orderLine in orderLines:
                proQty = int(orderLine.product_uom_qty)
                startDate = order.create_date
                endDate = warrantyModel.get_warranty_end_date(
                    orderLine.product_id, startDate)
                for _ in range(proQty):
                    vals = {
                        'partner_id': order.partner_id.id,
                        'product_id': orderLine.product_id.id,
                        'order_id': order.id,
                        'prod_qty' : 1,
                        'order_line': orderLine.id,
                        'warranty_end_date': endDate,
                    }
                    wrntId = warrantyModel.with_context(not_onchange=True).create(vals).id
                    warrantyIds.append(wrntId)
            if warrantyIds:
                order.warranty_ids = [(6, 0, warrantyIds)]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    to_renew_wrnty = fields.Many2one('warranty.registration', "To Renew")

    @api.one
    def get_warranty_details(self):
        prodObj = self.product_id
        warranty = {
            'wrnty': 0,
            'qty': int(self.product_uom_qty),
        }
        wrntyObjs = self.env['warranty.registration'].search([
            ('order_line', '=', self.id)])
        if wrntyObjs:
            wrntyStates = wrntyObjs.mapped('state')
            warranty['wrnty'] = 1
            warranty['line_name'] = wrntyStates.count('draft') == len(wrntyStates) and 'regsiter' or 'warranty'
            serialList = []
            for wrntyObj in wrntyObjs:
                daysLeft = self.days_difference(wrntyObj.warranty_end_date)
                isRenew = 'No'
                if prodObj.allow_renewal:
                    historyObjs = wrntyObj.warranty_history_ids
                    wrntyStates = wrntyObjs.mapped('state')
                    if wrntyObj.state == 'confirm' and daysLeft < 16 or wrntyObj.state == 'expired':
                        isRenew = 'Yes'
                    if len(historyObjs) > prodObj.max_renewal_times:
                        isRenew = 'No'
                serialN = wrntyObj.lot_id.name
                serialList.append({
                    'exp_date': wrntyObj.warranty_end_date,
                    'lot_num': serialN,
                    'wrnt_id': wrntyObj.id,
                    'crnt_state' : wrntyObj.state,
                    'ref' : wrntyObj.name,
                    'is_renew' : isRenew,
                })
            warranty['serial'] = serialList
        return warranty

    @api.model
    def days_difference(self, compare_to, compare_from=datetime.date.today()):
        dayesLeft = (compare_to - compare_from).days
        return dayesLeft


    @api.multi
    def get_wrnty_reg_info(self):
        self.ensure_one()
        prodQty = int(self.product_uom_qty)
        orderObj = self.order_id
        wrnty = orderObj.warranty_ids
        diffDict, diffList = {}, []
        for lineObj in wrnty:
            if lineObj.product_id == self.product_id:
                diffList.append(lineObj.lot_id.name)
        diffDict = {
            'serial': diffList,
            'left': int(prodQty)-len(diffList)
        }
        return diffDict

