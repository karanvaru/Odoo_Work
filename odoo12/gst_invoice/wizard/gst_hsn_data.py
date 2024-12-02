#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models

class GstHsnData(models.TransientModel):
    _name = "gst.hsn.data"
    _description = "GST HSN data"

    def getHSNData(self, invoiceObj, count, hsnDict={}, hsnDataDict={}):
        mainData = []
        jsonData = []
        currency = invoiceObj.currency_id or None
        ctx = dict(self._context or {})
        for invoiceLineObj in invoiceObj.invoice_line_ids:
            price = invoiceLineObj.price_subtotal/invoiceLineObj.quantity
            taxedAmount,cgst,sgst,igst = 0.0, 0.0, 0.0, 0.0
            rateObjs = invoiceLineObj.invoice_line_tax_ids
            if rateObjs:
                taxData = self.env['gst.tax.data'].getTaxedAmount(rateObjs, price, currency, invoiceLineObj, invoiceObj)
                rateAmount = taxData[1]
                taxedAmount = taxData[0]
                if currency.name != 'INR':
                    taxedAmount = taxedAmount * currency.rate
                taxedAmount = round(taxedAmount, 2)
                # if invoiceObj.partner_id.country_id.code == 'IN':
                for rateObj in rateObjs:
                    if rateObj.amount_type == "group":
                        cgst,sgst = round(taxedAmount/2, 2),round(taxedAmount/2, 2)
                    else:
                        igst = round(taxedAmount, 2)
            invUntaxedAmount = round(invoiceLineObj.price_subtotal, 2)
            if currency.name != 'INR':
                invUntaxedAmount = round(invoiceLineObj.price_subtotal * currency.rate, 2)
            productObj = invoiceLineObj.product_id
            hsnVal = productObj.l10n_in_hsn_code or 'False'
            hsnName = productObj.name or 'name'
            uqc = 'OTH'
            if productObj.uom_id:
                uom = productObj.uom_id.id
                uqcObj = self.env['uom.mapping'].search([('uom', '=', uom)])
                if uqcObj:
                    uqc = uqcObj[0].name.code
            invQty = invoiceLineObj.quantity
            invAmountTotal = invUntaxedAmount + taxedAmount
            if hsnDataDict.get(hsnVal):
                if hsnDataDict.get(hsnVal).get(hsnName):
                    if hsnDataDict.get(hsnVal).get(hsnName).get('qty'):
                        invQty = hsnDataDict.get(hsnVal).get(hsnName).get('qty') + invQty
                        hsnDataDict.get(hsnVal).get(hsnName)['qty'] = invQty
                    else:
                        hsnDataDict.get(hsnVal).get(hsnName)['qty'] = invQty
                    if hsnDataDict.get(hsnVal).get(hsnName).get('val'):
                        invAmountTotal = round(hsnDataDict.get(hsnVal).get(hsnName).get('val') + invAmountTotal, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['val'] = invAmountTotal
                    else:
                        invAmountTotal = round(invAmountTotal, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['val'] = invAmountTotal
                    if hsnDataDict.get(hsnVal).get(hsnName).get('txval'):
                        invUntaxedAmount = round(hsnDataDict.get(hsnVal).get(hsnName).get('txval') + invUntaxedAmount, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['txval'] = invUntaxedAmount
                    else:
                        invUntaxedAmount = round(invUntaxedAmount, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['txval'] = invUntaxedAmount
                    if hsnDataDict.get(hsnVal).get(hsnName).get('iamt'):
                        igst = round(hsnDataDict.get(hsnVal).get(hsnName).get('iamt') + igst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['iamt'] = igst
                    else:
                        igst = round(igst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['iamt'] = igst
                    if hsnDataDict.get(hsnVal).get(hsnName).get('camt'):
                        cgst = round(hsnDataDict.get(hsnVal).get(hsnName).get('camt') + cgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['camt'] = cgst
                    else:
                        cgst = round(cgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['camt'] = cgst
                    if hsnDataDict.get(hsnVal).get(hsnName).get('samt'):
                        sgst = round(hsnDataDict.get(hsnVal).get(hsnName).get('samt') + sgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['samt'] = sgst
                    else:
                        sgst = round(sgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['samt'] = sgst
                else:
                    count = count + 1
                    hsnDataDict.get(hsnVal)[hsnName] = {
                                                        'num':count,
                                                        'hsn_sc':hsnVal,
                                                        'desc':hsnName,
                                                        'uqc':uqc,
                                                        'qty':invQty,
                                                        'val':invAmountTotal,
                                                        'txval':invUntaxedAmount,
                                                        'iamt':igst,
                                                        'camt':cgst,
                                                        'samt':sgst,
                                                        'csamt':0.0
                                                    }
            else:
                count = count + 1
                hsnDataDict[hsnVal] = {hsnName:{
                                                'num':count,
                                                'hsn_sc':hsnVal,
                                                'desc':hsnName,
                                                'uqc':uqc,
                                                'qty':invQty,
                                                'val':invAmountTotal,
                                                'txval':invUntaxedAmount,
                                                'iamt':igst,
                                                'camt':cgst,
                                                'samt':sgst,
                                                'csamt':0.0
                                            }}
            hsnData = [
                productObj.l10n_in_hsn_code, productObj.name, uqc, invQty,
                invAmountTotal, invUntaxedAmount, igst, cgst, sgst, 0.0
            ]
            if hsnDict.get(hsnVal):
                hsnDict.get(hsnVal)[hsnName] = hsnData
            else:
                hsnDict[hsnVal] = {hsnName:hsnData}
            mainData.append(hsnData)
        return [mainData, jsonData, hsnDict, hsnDataDict]
