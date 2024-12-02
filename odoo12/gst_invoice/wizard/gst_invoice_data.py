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

from odoo import api, models

class GstInvoiceData(models.TransientModel):
    _name = "gst.invoice.data"
    _description = "GST invoice data"

    def getGSTInvoiceData(self, invoiceObj, invoiceType, data, gstType=''):
        jsonItemData = []
        count = 0
        rateDataDict = {}
        rateDict = {}
        rateJsonDict = {}
        itcEligibility = 'Ineligible'
        ctx = dict(self._context or {})
        if gstType == 'gstr2':
            if ctx.get('gst_id'):
                resId = ctx.get('gst_id')
                resObj = self.env['gstr1.tool'].browse(resId)
                itcEligibility = resObj.itc_eligibility
            if itcEligibility == 'Ineligible':
                itcEligibility = invoiceObj.itc_eligibility
        for invoiceLineObj in invoiceObj.invoice_line_ids:
            if invoiceLineObj.product_id:
                if invoiceLineObj.product_id.type == 'service':
                    if invoiceType == 'impg':
                        continue
                else:
                    if invoiceType == 'imps':
                        continue
            else:
                if invoiceType == 'impg':
                    continue
            invoiceLineData = self.getInvoiceLineData(data, invoiceLineObj, invoiceObj, invoiceType)
            if invoiceLineData:
                rate = invoiceLineData[2]
                rateAmount = invoiceLineData[3]
                if invoiceLineData[1]:
                    invoiceLineData[1]['txval'] = rateAmount
                if gstType == 'gstr2':
                    igst = invoiceLineData[1].get('iamt') or 0.0
                    cgst = invoiceLineData[1].get('camt') or 0.0
                    sgst = invoiceLineData[1].get('samt') or 0.0
                    if rate not in rateDict.keys():
                        rateDataDict[rate] = {'taxval':rateAmount, 'igst':igst, 'cgst':cgst, 'sgst':sgst, 'cess':0.0}
                    else:
                        rateDataDict[rate]['taxval'] = rateDataDict[rate]['taxval'] + rateAmount
                        rateDataDict[rate]['igst'] = rateDataDict[rate]['igst'] + igst
                        rateDataDict[rate]['cgst'] = rateDataDict[rate]['cgst'] + cgst
                        rateDataDict[rate]['sgst'] = rateDataDict[rate]['sgst'] + sgst
                        rateDataDict[rate]['cess'] = rateDataDict[rate]['cess'] + 0.0
                if gstType == 'gstr1':
                    if rate not in rateDict.keys():
                        rateDataDict[rate] = {'taxval':rateAmount, 'cess':0.0}
                    else:
                        rateDataDict[rate]['taxval'] = rateDataDict[rate]['taxval'] + rateAmount
                        rateDataDict[rate]['cess'] = rateDataDict[rate]['cess'] + 0.0
                if rate not in rateJsonDict.keys():
                    rateJsonDict[rate] = invoiceLineData[1]
                else:
                    for key in invoiceLineData[1].keys():
                        if key in ['rt', 'sply_ty', 'typ', 'elg']:
                            continue
                        if rateJsonDict[rate].get(key):
                            rateJsonDict[rate][key] = rateJsonDict[rate][key] + invoiceLineData[1][key]
                            rateJsonDict[rate][key] = round(rateJsonDict[rate][key], 2)
                        else:
                            rateJsonDict[rate][key] = invoiceLineData[1][key]
                invData = []
                if gstType == 'gstr1':
                    invData = invoiceLineData[0] + [rateDataDict[rate]['taxval']]
                if gstType == 'gstr2':
                    if invoiceType in ['imps', 'impg']:
                        invData = invoiceLineData[0] + [rateDataDict[rate]['taxval'], rateDataDict[rate]['igst']]
                    else:
                        invData = invoiceLineData[0] + [rateDataDict[rate]['taxval'], rateDataDict[rate]['igst'], rateDataDict[rate]['cgst'], rateDataDict[rate]['sgst']]
                if invoiceType == 'b2b':
                    if gstType == 'gstr1':
                        invData = invData + [0.0]
                    if gstType == 'gstr2':
                        if itcEligibility != 'Ineligible':
                            invData = invData + [0.0] + [itcEligibility] + [rateDataDict[rate]['igst']] + [rateDataDict[rate]['cgst']] + [rateDataDict[rate]['sgst']] + [rateDataDict[rate]['cess']]
                        else:
                            invData = invData + [0.0] + [itcEligibility] + [0.0] + [0.0] + [0.0] + [0.0]

                elif invoiceType == 'b2bur':
                    if itcEligibility != 'Ineligible':
                        invData = invData + [0.0] + [itcEligibility] + [rateDataDict[rate]['igst']] + [rateDataDict[rate]['cgst']] + [rateDataDict[rate]['sgst']] + [rateDataDict[rate]['cess']]
                    else:
                        invData = invData + [0.0] + [itcEligibility] + [0.0] + [0.0] + [0.0] + [0.0]
                elif invoiceType in ['imps', 'impg']:
                    if itcEligibility != 'Ineligible':
                        invData = invData + [0.0] + [itcEligibility] + [rateDataDict[rate]['igst']] + [rateDataDict[rate]['cess']]
                    else:
                        invData = invData + [0.0] + [itcEligibility] + [0.0] + [0.0]
                elif invoiceType in ['b2cs', 'b2cl']:
                    invData = invData + [0.0, '']
                    if invoiceType == 'b2cl':
                        invData = invData + [invoiceObj.bonded_wh]
                rateDict[rate] = invData
        mainData = rateDict.values()
        if rateJsonDict:
            for jsonData in rateJsonDict.values():
                count = count + 1
                if invoiceType == 'b2b' and gstType == 'gstr2':
                    jsonItemData.append({"num":count, 'itm_det':jsonData, "itc": {"elg": "no", "tx_i": 0.0, "tx_s": 0.0, "tx_c": 0.0, "tx_cs": 0.0}})
                elif invoiceType == 'b2bur':
                    jsonItemData.append({"num":count, 'itm_det':jsonData, "itc": {"elg": "no", "tx_i": 0.0, "tx_s": 0.0, "tx_c": 0.0, "tx_cs": 0.0}})
                elif invoiceType in ['imps', 'impg']:
                    jsonItemData.append({"num":count, 'itm_det':jsonData, "itc": {"elg": "no", "tx_i": 0.0, "tx_cs": 0.0}})
                else:
                    jsonItemData.append({"num":count, 'itm_det':jsonData})
        return [mainData, jsonItemData, rateDataDict, rateJsonDict]

    def getInvoiceLineData(self, invoiceLineData, invoiceLineObj, invoiceObj, invoiceType):
        lineData = []
        jsonLineData = {}
        taxedAmount = 0.0
        rate = 0.0
        rateAmount = 0.0
        currency = invoiceObj.currency_id or None
        price = invoiceLineObj.price_subtotal/invoiceLineObj.quantity if invoiceLineObj.quantity > 0 else 0.0
        rateObjs = invoiceLineObj.invoice_line_tax_ids
        if rateObjs:
            for rateObj in rateObjs:
                if rateObj.amount_type == "group":
                    for childObj in rateObj.children_tax_ids:
                        rate = childObj.amount*2
                        lineData.append(rate)
                        break
                else:
                    rate = rateObj.amount
                    lineData.append(rate)
                break
            taxData = self.env['gst.tax.data'].getTaxedAmount(rateObjs, price, currency, invoiceLineObj, invoiceObj)
            rateAmount = taxData[1]
            rateAmount = round(rateAmount, 2)
            taxedAmount = taxData[0]
            jsonLineData = self.env['gst.tax.data'].getGstTaxData(invoiceObj, invoiceLineObj, rateObjs, taxedAmount, invoiceType)
        else:
            rateAmount = invoiceLineObj.price_subtotal
            rateAmount = rateAmount
            if currency.name != 'INR':
                rateAmount = rateAmount * currency.rate
            rateAmount = round(rateAmount, 2)
            lineData.append(0)
            jsonLineData = self.env['gst.tax.data'].getGstTaxData(invoiceObj, invoiceLineObj, False, taxedAmount, invoiceType)
        data = invoiceLineData + lineData
        return [data, jsonLineData, rate, rateAmount]