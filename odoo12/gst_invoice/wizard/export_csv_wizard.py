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
import csv
import io
import base64

def _unescape(text):
    from urllib.parse import unquote_plus
    try:
        text = unquote_plus(text.encode('utf8'))
        return text
    except Exception as e:
        return text

class ExportCsvWizard(models.TransientModel):
    _name = "export.csv.wizard"
    _description = "Export CSV wizard"

    @api.model
    def exportCsv(self, active_ids, invoice_type, gstToolName, gstType):
        if invoice_type == 'import':
            impsData = self.getInvoiceData(active_ids, 'imps', gstType)
            mainData = impsData[0]
            impsAttachment = self.prepareCsv(mainData, 'imps', gstToolName, gstType)
            impsJsonData = impsData[1]
            impgData = self.getInvoiceData(active_ids, 'impg', gstType)
            mainData = impgData[0]
            impgAttachment = self.prepareCsv(mainData, 'impg', gstToolName, gstType)
            impgJsonData = impgData[1]
            return [[impsAttachment, impsJsonData], [impgAttachment, impgJsonData]]
        respData = self.getInvoiceData(active_ids, invoice_type, gstType)
        mainData = respData[0]
        jsonData = respData[1]
        attachment = self.prepareCsv(mainData, invoice_type, gstToolName, gstType)
        return [attachment, jsonData]

    def prepareCsv(self, mainData, invoice_type, gstToolName, gstType):
        attachment = False
        if mainData:
            fp = io.StringIO()
            writer = csv.writer(fp, quoting=csv.QUOTE_NONE, escapechar='\\')
            if invoice_type == 'b2b':
                columns = self.env['csv.column'].getB2BColumn(gstType)
                writer.writerow(columns)
            elif invoice_type == 'b2bur':
                columns = self.env['csv.column'].getB2BURColumn()
                writer.writerow(columns)
            elif invoice_type == 'b2cl':
                columns = self.env['csv.column'].getB2CLColumn()
                writer.writerow(columns)
            elif invoice_type == 'b2cs':
                columns = self.env['csv.column'].getB2CSColumn()
                writer.writerow(columns)
            elif invoice_type == 'imps':
                columns = self.env['csv.column'].getImpsColumn()
                writer.writerow(columns)
            elif invoice_type == 'impg':
                columns = self.env['csv.column'].getImpgColumn()
                writer.writerow(columns)
            elif invoice_type == 'export':
                columns = self.env['csv.column'].getExportColumn()
                writer.writerow(columns)
            elif invoice_type == 'hsn':
                columns = self.env['csv.column'].getHSNColumn()
                writer.writerow(columns)
            for lineData in mainData:
                writer.writerow([_unescape(name) for name in lineData])
            fp.seek(0)
            data = fp.read()
            fp.close()
            attachment = self.generateAttachment(data, invoice_type, gstToolName)
        return attachment

    def generateAttachment(self, data, invoice_type, gstToolName):
        attachment = False
        base64Data = base64.b64encode(data.encode('utf-8'))
        datas_fname = '{}_{}.csv'.format(invoice_type, gstToolName)
        try:
            resId = 0
            if self._context.get('gst_id'):
                resId = self._context.get('gst_id')
            attachment = self.env['ir.attachment'].create({
                'datas': base64Data,
                'type': 'binary',
                'res_model': 'gstr1.tool',
                'res_id': resId,
                'db_datas': datas_fname,
                'datas_fname': datas_fname,
                'name': datas_fname
                }
            )
        except ValueError:
            return attachment
        return attachment

    def getInvoiceData(self, active_ids, invoiceType, gstType):
        mainData = []
        jsonData = []
        count = 0
        ctx = dict(self._context or {})
        b2csDataDict = {}
        b2csJsonDataDict = {}
        b2clJsonDataDict = {}
        b2burDataDict = {}
        b2bDataDict = {}
        hsnDict = {}
        hsnDataDict = {}
        reverseChargeMain = 'N'
        if ctx.get('gst_id'):
            resId = ctx.get('gst_id')
            resObj = self.env['gstr1.tool'].browse(resId)
            if resObj.reverse_charge:
                reverseChargeMain = 'Y'
        for active_id in active_ids:
            invData = {}
            invoiceObj = self.env['account.invoice'].browse(active_id)
            reverseCharge = 'Y' if invoiceObj.reverse_charge else 'N' if reverseChargeMain == 'N' else reverseChargeMain
            invType = invoiceObj.gst_invoice_type or 'Regular'
            jsonInvType = 'R'
            if invType == 'SEZ supplies with payment':
                jsonInvType = 'SEWP'
            elif invType == 'SEZ supplies without payment':
                jsonInvType = 'SEWOP'
            elif invType == 'Deemed Exp':
                jsonInvType = 'DE'
            currency = invoiceObj.currency_id
            invoiceNumber = invoiceObj.number or ''
            if gstType == 'gstr2':
                invoiceNumber = invoiceObj.reference or ''
            if len(invoiceNumber) > 16:
                invoiceNumber = invoiceNumber[0:16]
            invoiceDate = invoiceObj.date_invoice
            invoiceJsonDate = invoiceDate.strftime('%d-%m-%Y')
            invoiceDate = invoiceDate.strftime('%d-%b-%Y')
            invoiceTotal = invoiceObj.amount_total
            if currency.name != 'INR':
                invoiceTotal = invoiceTotal * currency.rate
            invoiceObj.inr_total = invoiceTotal
            invoiceTotal = round(invoiceTotal, 2)
            state = invoiceObj.partner_id.state_id
            code = state.l10n_in_tin or 0
            code = _unescape(state.l10n_in_tin)
            sname = _unescape(state.name)
            stateName = "{}-{}".format(code, sname)
            data = []
            if invoiceType == 'b2b':
                customerName = invoiceObj.partner_id.name
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "pos": code,
                    "rchrg": reverseCharge,
                    "inv_typ": jsonInvType
                }
                if gstType == 'gstr1':
                    invData['etin'] = ""
                    invData['diff_percent'] = 0.0
                gstrData = [invoiceObj.x_vat, invoiceNumber, invoiceDate, invoiceTotal, stateName, reverseCharge, 'Regular']
                if gstType == 'gstr1':
                    gstrData = [invoiceObj.x_vat, customerName, invoiceNumber, invoiceDate, invoiceTotal, stateName, reverseCharge, 0.0, invType, '']
                data.extend(gstrData)
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2bDataDict.get(invoiceObj.x_vat):
                    b2bDataDict[invoiceObj.x_vat].append(invData)
                else:
                    b2bDataDict[invoiceObj.x_vat] = [invData]
            elif invoiceType == 'b2bur':
                sply_ty = 'INTER'
                sply_type = 'Inter State'
                if invoiceObj.partner_id.state_id.code != self.company_id.state_id.code:
                    sply_ty = 'INTRA'
                    sply_type = 'Intra State'
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "pos": code,
                    "sply_ty": sply_ty
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([supplierName, invoiceNumber, invoiceDate, invoiceTotal, stateName, sply_type])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2burDataDict.get(supplierName):
                    b2burDataDict[supplierName].append(invData)
                else:
                    b2burDataDict[supplierName] = [invData]

            elif invoiceType == 'b2cl':
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "etin": "",
                }
                if invoiceObj.bonded_wh == 'Y':
                    invData['inv_typ'] = 'CBW'
                invData['diff_percent'] = 0.0
                data.extend([invoiceNumber, invoiceDate, invoiceTotal, stateName, 0.0])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2clJsonDataDict.get(code):
                    b2clJsonDataDict[code].append(invData)
                else:
                    b2clJsonDataDict[code] = [invData]
            elif invoiceType == 'b2cs':
                invData = {
                    "pos": code
                }
                b2bData = ['OE', stateName]
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, b2bData, gstType)
                b2bData = respData[0]
                rateDataDict = respData[2]
                rateJsonDict = respData[3]
                if b2csDataDict.get(stateName):
                    for key in rateDataDict.keys():
                        if b2csDataDict.get(stateName).get(key):
                            for key1 in rateDataDict.get(key).keys():
                                if b2csDataDict.get(stateName).get(key).get(key1):
                                    b2csDataDict.get(stateName).get(key)[key1] = b2csDataDict.get(stateName).get(key)[key1] + rateDataDict.get(key)[key1]
                                else:
                                    b2csDataDict.get(stateName).get(key)[key1] = rateDataDict.get(key)[key1]
                        else:
                            b2csDataDict.get(stateName)[key] = rateDataDict[key]
                else:
                    b2csDataDict[stateName] = rateDataDict
                if b2csJsonDataDict.get(code):
                    for key in rateJsonDict.keys():
                        if b2csJsonDataDict.get(code).get(key):
                            for key1 in rateJsonDict.get(key).keys():
                                if b2csJsonDataDict.get(code).get(key).get(key1):
                                    if key1 in ['rt', 'sply_ty', 'typ']:
                                        continue
                                    b2csJsonDataDict.get(code).get(key)[key1] = b2csJsonDataDict.get(code).get(key)[key1] + rateJsonDict.get(key)[key1]
                                    b2csJsonDataDict.get(code).get(key)[key1] = round(b2csJsonDataDict.get(code).get(key)[key1], 2)
                                else:
                                    b2csJsonDataDict.get(code).get(key)[key1] = rateJsonDict.get(key)[key1]
                        else:
                            b2csJsonDataDict.get(code)[key] = rateJsonDict[key]
                else:
                    b2csJsonDataDict[code] = rateJsonDict
                if respData[1]:
                    invData.update(respData[1][0])
            elif invoiceType == 'imps':
                state = self.env['res.users'].browse(self._uid).company_id.state_id
                code = _unescape(state.l10n_in_tin) or 0
                sname = _unescape(state.name)            
                stateName = "{}-{}".format(code, sname)
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "ival": invoiceTotal,
                    "pos": code
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([invoiceNumber, invoiceDate, invoiceTotal, stateName])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                jsonData.append(invData)
            elif invoiceType == 'impg':
                companyGST = self.env['res.users'].browse(self._uid).company_id.vat
                portcode = ''
                if invoiceObj.portcode_id:
                    portcode = invoiceObj.portcode_id.name
                invData = {
                    "boe_num": invoiceNumber,
                    "boe_dt": invoiceJsonDate,
                    "boe_val": invoiceTotal,
                    "port_code": portcode,
                    "stin": companyGST,
                    'is_sez':'Y'
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([portcode, invoiceNumber, invoiceDate, invoiceTotal, 'Imports', companyGST])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                jsonData.append(invData)
            elif invoiceType == 'export':
                portcode = ''
                if invoiceObj.portcode_id:
                    portcode = invoiceObj.portcode_id.name
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "sbpcode": portcode,
                    "sbnum": "",
                    "sbdt": "",
                }
                invData['diff_percent'] = 0.0
                data.extend([invoiceObj.export, invoiceNumber, invoiceDate, invoiceTotal, portcode, '', '', 0.0])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                jsonData.append(invData)
            elif invoiceType == 'hsn':
                respData = self.env['gst.hsn.data'].getHSNData(invoiceObj, count, hsnDict, hsnDataDict)
                data = respData[0]
                jsonData.extend(respData[1])
                hsnDict = respData[2]
                hsnDataDict = respData[3]
                invoiceObj.gst_status = 'ready_to_upload'
            if data:
                mainData.extend(data)
        if b2csJsonDataDict:
            for pos,val in b2csJsonDataDict.items():
                for line in val.values():
                    line['pos'] = pos
                    line['diff_percent'] = 0.0
                    jsonData.append(line)
        if b2csDataDict:
            b2csData = []
            for state, data in b2csDataDict.items():
                for rate, val in data.items():
                    b2csData.append(['OE', state, 0.0, rate, round(val['taxval'], 2), round(val['cess'], 2), ''])
            mainData = b2csData

        if b2bDataDict:
            for ctin, inv in b2bDataDict.items():
                jsonData.append({
                    'ctin':ctin,
                    'inv':inv
                })
        if b2burDataDict:
            for ctin, inv in b2burDataDict.items():
                jsonData.append({
                    'inv':inv
                })
        if b2clJsonDataDict:
            for pos, inv in b2clJsonDataDict.items():
                jsonData.append({
                    'pos':pos,
                    'inv':inv
                })
        if hsnDict:
            vals = hsnDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            mainData = hsnMainData
        if hsnDataDict:
            vals = hsnDataDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            jsonData = hsnMainData
        return [mainData, jsonData]
