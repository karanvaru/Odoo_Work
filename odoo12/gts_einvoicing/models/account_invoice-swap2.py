from odoo import fields, models, api, _
import requests
import json
import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import base64
from num2words import num2words
import logging
_logger = logging.getLogger("_____")

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    irn_no = fields.Char(string='IRN-No',copy=False)
    invoice_origin = fields.Many2one('account.invoice',string='Invoice')
    gen_einvoice = fields.Boolean('Generate E-Invoice?',copy=False)
    sup_type = fields.Selection([
        ('B2B', 'B2B'),
        ('SEZWP', 'SEZWP'),
        ('SEZWOP', 'SEZWOP'),
        ('EXPWP', 'EXPWP'),
        ('EXPWOP', 'EXPWOP'),
        ('DEXP', 'DEXP'),
    ], string="SUP-TYPE")
    doc_type = fields.Selection([
        ('INV', 'INV'),
        ('CRN', 'CRN'),
        ('DBN', 'DBN'),
    ], string="Doc-Type")
    is_service = fields.Selection([('Y', 'Yes'), ('N', 'No')], string='IS-Service')
    ackdt_no = fields.Char('Acknowledge Date',copy=False)
    ack_no = fields.Char('Acknowledge Number',copy=False)
    signed_invoice = fields.Char('Invoice Signed Data')
    inv_barcode = fields.Char('Bracode Data')
    trans_id = fields.Char('Transporter')
    trans_name = fields.Char('Transporter Name')
    veh_no = fields.Char('Vehicle Number')
    veh_type = fields.Selection([('O', 'ODC'), ('R', 'Regular')], string='vehicle Type')
    distance = fields.Integer('Distance')
    transMode = fields.Selection([('1', 'Road'), ('2', 'Rail'), ('3', 'Air'), ('4', 'Ship')], string='Transporter Mode')
    transporter_docno = fields.Char('Transporter Doc-No')
    transporter_docdt = fields.Date('Transporter Doc-Date')
    eway_bill_gen = fields.Boolean('Generate Eway Bill?',copy=False)
    eway_bill_no = fields.Char('Eway Bill No',copy=False)
    eway_valid_date = fields.Char('Eway Bill Valid Till',copy=False)
    eway_date = fields.Char('Eway Bill Date',copy=False)
    eway_bill_status = fields.Selection([('generated', 'Generated'), ('not generated', 'Not Generated'), ('cancel', 'Cancelled')],string='Eway Bill Status', default='not generated',copy=False)
    qr_image = fields.Binary('Qr-Code', store=True,copy=False)
    name = fields.Char()
    eway_cancel_date = fields.Char('Eway Bill Cancel Date',copy=False)
    irn_cancel_date = fields.Char('IRN Number Cancel Date',copy=False)
    transaction_type = fields.Selection([('1', 'Regular'),
                                         ('2', 'Bill To - Ship To'),
                                         ('3', 'Bill From - Dispatch From'),
                                         ('4', 'Combination of 2 and 3')], string="Transaction Type", copy=False,tracking=2, default='1')




    def get_warehouse(self):
        delivery = self.env['stock.picking'].search([('origin', '=', self.origin),
                                                     ('company_id', '=', self.env.user.company_id.id)], limit=1)

        if delivery:
            warehouse = delivery.picking_type_id.warehouse_id
            return warehouse
        if not delivery:
            so_delivery = self.env['sale.order'].search([('name', '=', self.origin),('company_id', '=', self.env.user.company_id.id)], limit=1)

            if so_delivery:
                warehouse = so_delivery.warehouse_id
                return warehouse

        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        if warehouse:
            return warehouse

            


    @api.onchange('transporter_id', 'vehicle_no')
    def onchange_ewaybill_details(self):
        if self.transporter_id:
            self.trans_id = self.transporter_id.name
        if self.vehicle_no:
            self.veh_no = self.vehicle_no

    @api.multi
    def create_einvoicing(self):
        print("create einvoice===")
        item_list = []
        einvoicing = self.env['einvoicing.configuration'].search([], limit=1)
        warehouse = self.get_warehouse()
        # print("warehouse---------------",warehouse)
        data = einvoicing.handle_einvoicing_auth_token(warehouse)
        if not warehouse:
            raise UserError(_('No Warehouse found for this invoice'))

        if not einvoicing:
            raise UserError(_('No Configurations details found in the system for E-Invoicing.'))
        if not warehouse.auth_token:
            raise UserError(_('Please Check Auth Token in E-Invoicing Configuration is Expired or Null.'))
        if not einvoicing.testing:
            raise UserError(_('Please Set Url Type in E-Invoicing Configuration.'))
        if not einvoicing.asp_id:
            raise UserError(_('Please Enter ASP-ID in E-Invoicing Configurations.'))
        if not einvoicing.asp_password:
            raise UserError(_('Please Enter ASP Password in E-Invoicing Configurations.'))
        if not warehouse.gst_no:
            raise UserError(_('Please Enter Registered GSTIN in E-Invoicing Configurations.'))
        if not warehouse.user_password:
            raise UserError(_('Please Enter User Password in E-Invoicing Configurations.'))
        if not warehouse.user_name:
            raise UserError(_('Please Enter User Name in E-Invoicing Configurations.'))
        if not self.sup_type:
            raise UserError(_('Please Select Sub-Type.'))
        if not self.doc_type:
            raise UserError(_('Please Select Doc-Type.'))
        if not self.display_name:
            raise UserError(_('Invoice Number is not present.'))
        if not self.company_id.vat:
            raise UserError(_('Company GSTIN Number is not present or Enter Registered GSTIN Numnber Only.'))
        if not self.company_id.street:
            raise UserError(_('Company Address line 1 is not present.'))
        if not self.company_id.street2:
            raise UserError(_('Company Address line 2 is not present.'))
        if not self.company_id.zip:
            raise UserError(_('Company Pincode is not present.'))
        if not self.company_id.city:
            raise UserError(_('Company City is not present.'))
        if not self.company_id.state_id.code:
            raise UserError(_('Company State Code is not present.'))
        if not self.date_invoice:
            raise UserError(_('Please Enter Invoice Date'))
        if not self.partner_id.name:
            raise UserError(_('Please Enter Buyer Name'))
        if not self.partner_id.state_id.code:
            raise UserError(_('Please Enter Buyer State Code'))
        if not self.partner_id.city:
            raise UserError(_('Please Enter Buyer City'))
        if not self.partner_id.street:
            raise UserError(_('Please Enter Buyer Address line 1.'))
        if not self.partner_id.zip:
            raise UserError(_('Please Enter Buyer Pincode'))
        if not self.date_invoice:
            raise UserError(_('Please Enter Invoice Date'))
        if not self.partner_id.name:
            raise UserError(_('Please Enter warehouse Name'))
        # if not self.partner_id.state_id.code:
        #     raise UserError(_('Please Enter warehouse State Code'))
        if not self.partner_id.city:
            raise UserError(_('Please Enter warehouse City'))
        if not self.partner_id.street:
            raise UserError(_('Please Enter warehouse Address line 1.'))
        if not self.partner_id.zip:
            raise UserError(_('Please Enter warehouse Pincode'))
        if not self.date_invoice:
            raise UserError(_('Please Enter warehouse Date'))

        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if not line.product_id.l10n_in_hsn_code or len(line.product_id.l10n_in_hsn_code) > 8 or len(line.product_id.l10n_in_hsn_code) < 4:
                    raise UserError(_('HSN code should be 4 to 8 digit!'))
                if not line.invoice_line_tax_ids:
                    raise UserError(_('Please select Tax'))

        date1 = datetime.strptime(str(self.date_invoice), '%Y-%m-%d').strftime('%d/%m/%Y')
        if not self.date_due:
            date2 = datetime.strptime(str(self.date_invoice), '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            date2 = datetime.strptime(str(self.date_due), '%Y-%m-%d').strftime('%d/%m/%Y')
        # print("-----------display_name---------------display_name----------",self.reference.replace("/",""),self.sequence_number_next)

        if not self.number:
            data = {
                "Version": "1.1",
                "TranDtls": {
                    "TaxSch": "GST",
                    "SupTyp": self.sup_type,
                },
                "DocDtls": {
                    "Typ": self.doc_type,
                    "No": self.origin.replace("/",""),
                    "Dt": date1
                },
                "RefDtls": {
                    "DocPerdDtls": {
                        "InvStDt": date1,
                        "InvEndDt": date2
                    },
                    "PrecDocDtls": [
                        {
                            "InvNo": self.number.replace("/",""),
                            "InvDt": date1,
                        }
                    ],
                },
            }
            _logger.info("if============================data==%s",data)
        else:
            data = {
                "Version": "1.1",
                "TranDtls": {
                    "TaxSch": "GST",
                    "SupTyp": self.sup_type,
                },
                "DocDtls": {
                    "Typ": self.doc_type,
                    "No": self.number.replace("/",""),
                    "Dt": date1
                },
                "RefDtls": {
                    "DocPerdDtls": {
                        "InvStDt": date1,
                        "InvEndDt": date2
                    },
                    "PrecDocDtls": [
                        {
                            "InvNo": self.number.replace("/",""),
                            "InvDt": date1,
                        }
                    ],
                },
            }
            _logger.info("elsedata=====================%s===",data)

        SellerDtls = {
            "Gstin": self.company_id.vat,  # "34AACCC1596Q002",
            "LglNm": self.company_id.name,
            "Addr1": self.company_id.street,
            "Loc": self.company_id.city,
            # "TrdNm":'',
            "State": self.company_id.state_id.stcd,
            "Pin": int(self.company_id.zip),
            "Stcd": self.company_id.state_id.stcd,
        }
        _logger.info("sellalr============>>>>>>>>>>>>>>>%s>>>", SellerDtls)
        if self.partner_id.country_id.code != 'IN':
            # _logger.info("=====================tenure==%s=", self.partner_id.country_id.code)
            BuyerDtls = {
                "Gstin": self.partner_id.vat,
                "LglNm": self.partner_id.name,
                "Pos": self.partner_id.state_id.stcd,
                "Addr1": self.partner_id.street,
                "Loc": self.partner_id.city,
                "State": self.partner_id.state_id.stcd,
                "Pin": self.partner_id.zip,
                "Stcd": self.partner_id.state_id.stcd,
            }
            _logger.info("iffffffffff============>>>>>>>>>>>>>>>%s>>>", BuyerDtls)
        else:
            # if self.sup_type == 'B2COters':
            #     BuyerDtls = {
            #         "Gstin": 'URP',
            #         "LglNm": self.partner_id.name,
            #         "Pos": self.partner_id.state_id.code,
            #         "Addr1": self.partner_id.street,
            #         "Loc": self.partner_id.city,
            #         "Pin": int(self.partner_id.zip),
            #         "Stcd": self.partner_id.state_id.code, }
            # else:
            BuyerDtls = {
                "Gstin": self.partner_id.vat,
                "LglNm": self.partner_id.name,
                "Pos": self.partner_id.state_id.stcd,
                "Addr1": self.partner_id.street,
                "Loc": self.partner_id.city,
                "State":  self.partner_id.state_id.stcd,
                "Pin": int(self.partner_id.zip),
                "Stcd": self.partner_id.state_id.stcd, }
            _logger.info("name============>>>>>>>>>>>>>>>%s>>>", BuyerDtls)
            # print("BuyerDtls=================%s===",self.partner_id.state_id.code)

        DispDtls = {
                       "Nm": warehouse.partner_id.name,
                       "Addr1": warehouse.partner_id.street,
                       "Loc": warehouse.partner_id.city,
                       "Pin": int(warehouse.partner_id.zip),
                       "Stcd": warehouse.partner_id.state_id.stcd
                   }
        # if self.temp:
        #     ShipDtls = {
        #         "LglNm": self.contact_name,
        #         "Addr1": self.street,
        #         "Loc": self.city,
        #         "Pin": int(self.zip),
        #         "Stcd": self.state_id.code
        #     }
        # else:
        addr1 =''
        if self.partner_id.street:
            addr1= self.partner_id.street
        if self.partner_id.street and self.partner_id.street2:
            addr1= self.partner_id.street + ',' + self.partner_id.street2

        ShipDtls = {
            "LglNm": self.partner_id.name,
            "Addr1": addr1,
            "Loc": self.partner_id.city,
            "Pin": int(self.partner_id.zip),
            "Stcd": self.partner_id.state_id.stcd,
        }
        if self.transaction_type == '1':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['DispDtls'] = DispDtls
            data['ShipDtls'] = ShipDtls

        if self.transaction_type == '2':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['ShipDtls'] = ShipDtls

        if self.transaction_type == '3':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['DispDtls'] = DispDtls

        if self.transaction_type == '4':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['ShipDtls'] = ShipDtls
            data['DispDtls'] = DispDtls

        total_igst = 0.0
        total_igsts = 0.0
        total_cgst = 0.0
        total_cgsts = 0.0
        total_sgst = 0.0
        total_sgsts = 0.0
        total = 0.0
        total_amt = 0.0
        assmt = 0.0
        total_round, tcs_amount = 0.0, 0.0
        for idx, inv_line in enumerate(self.invoice_line_ids):
            if  not inv_line:
                if inv_line.price_subtotal > 5:
                    tcs_amount += inv_line.price_subtotal
                else:
                    total_round += inv_line.price_subtotal
        flag = False
        for idx, inv_line in enumerate(self.invoice_line_ids):
            if inv_line:
                total = total + inv_line.price_subtotal
                discount = 0.0
                if inv_line.discount:
                    discount = round((inv_line.price_unit * inv_line.quantity)*inv_line.discount/100 , 2)
                    print("discount=====", discount)

                tax_rate = 0
                if inv_line.invoice_line_tax_ids:
                    for tax in inv_line.invoice_line_tax_ids:
                        # if tax.gst_type in ('cgst', 'sgst', 'igst'):
                        if tax.amount_type == 'group':
                            print("group=======tax")
                            for child in tax.children_tax_ids:
                                if child.tax_group_id.name == "SGST":
                                    total_sgst=((inv_line.price_unit*inv_line.quantity)-(inv_line.price_unit * inv_line.quantity)*inv_line.discount/100)*child.amount/100
                                    total_sgsts += ((inv_line.price_unit*inv_line.quantity)-(inv_line.price_unit * inv_line.quantity)*inv_line.discount/100)*child.amount/100
                                    total_amt = round(inv_line.price_unit * inv_line.quantity, 2)
                                    assmt = round(inv_line.price_subtotal, 2)
                                if child.tax_group_id.name == "CGST":
                                    total_cgst = ((inv_line.price_unit*inv_line.quantity)-(inv_line.price_unit * inv_line.quantity)*inv_line.discount/100)*child.amount/100
                                    total_cgsts +=((inv_line.price_unit*inv_line.quantity)-(inv_line.price_unit * inv_line.quantity)*inv_line.discount/100)*child.amount/100
                                    total_amt = round(inv_line.price_unit * inv_line.quantity, 2)
                                    assmt = round(inv_line.price_subtotal, 2)


                                tax_rate += child.amount
                        if tax.amount_type != 'group':
                            print(" not group=======tax")
                            tax_rate += tax.amount
                            if tax.tax_group_id.name == "IGST" and not tax.price_include:
                                total_igst = ((inv_line.price_subtotal) * tax.amount)/100
                                total_igsts += ((inv_line.price_subtotal) * tax.amount)/100
                                total_amt = round(inv_line.price_unit * inv_line.quantity, 2)
                                assmt = round(inv_line.price_subtotal, 2)
                            elif tax.tax_group_id.name == "IGST" and tax.price_include:
                                total_igst = (inv_line.price_subtotal * tax.amount)/100
                                total_igsts += (inv_line.price_subtotal * tax.amount)/100
                                total_amt = round(inv_line.price_subtotal + discount, 2)
                                assmt = round(inv_line.price_subtotal, 2)





                            if tax.tax_group_id.name in ['cgst', 'CGST'] and not tax.price_include:

                                total_cgst = ((inv_line.price_subtotal) * tax.amount)/100
                                total_cgsts += ((inv_line.price_subtotal) * tax.amount)/100
                                total_amt = round(inv_line.price_unit * inv_line.quantity, 2)
                                assmt = round(inv_line.price_subtotal, 2)
                                # assmt = round(inv_line.price_subtotal - ((inv_line.price_unit * inv_line.quantity) - inv_line.price_subtotal),2)
                            if tax.tax_group_id.name in ['cgst', 'CGST'] and tax.price_include:
                                print("1127 CSGST SGST=======###")
                                total_cgst = (inv_line.price_subtotal * tax.amount)/100
                                total_cgsts += (inv_line.price_subtotal * tax.amount)/100
                                total_amt = round(inv_line.price_subtotal + discount, 2)
                                assmt = round(inv_line.price_subtotal, 2)
                                # assmt = inv_line.price_subtotal


                            if tax.tax_group_id.name in ['sgst', 'SGST'] and not tax.price_include:

                                total_sgst = ((inv_line.price_subtotal) * tax.amount)/100
                                total_sgsts += ((inv_line.price_subtotal) * tax.amount)/100
                                total_amt = round(inv_line.price_unit * inv_line.quantity, 2)
                                assmt = round(inv_line.price_subtotal, 2)
                                # assmt = round(inv_line.price_subtotal - ((inv_line.price_unit * inv_line.quantity) - inv_line.price_subtotal),2)
                            if tax.tax_group_id.name in ['sgst', 'SGST'] and tax.price_include:
                                print("===SGST========")
                                total_sgst = (inv_line.price_subtotal * tax.amount)/100
                                total_sgsts += (inv_line.price_subtotal * tax.amount)/100
                                total_amt = round(inv_line.price_subtotal + discount, 2)
                                assmt = round(inv_line.price_subtotal, 2)
                                # assmt = inv_line.price_subtotal



                else:
                    tax_rate = 0.0
                    total_cgst = 0.0
                    total_sgst = 0.0
                    total_igst = 0.0
                total_tax = total_igst+total_cgst+total_sgst
                # print("=-=-=->>>>>>>>>>>>>>>>>>>>sakdjfdsdf======",total_cgsts,total_sgst)

                item_dict = {
                    "SlNo": str(idx + 1),
                    "IsServc": 'Y' if inv_line.product_id and inv_line.product_id.type == 'service' else 'N',
                    "HsnCd": inv_line.product_id.l10n_in_hsn_code,
                    "PrdDesc": inv_line.product_id.name,
                    "Qty": inv_line.quantity,
                    "UnitPrice": round(inv_line.price_unit, 2),
                    "Unit": 'UNT',
                    "TotAmt": total_amt,
                    "Discount": discount,
                    "AssAmt": assmt,
                    "SgstAmt": round(total_sgst, 2),
                    "CgstAmt": round(total_cgst, 2),
                    "IgstAmt": round(total_igst, 2),
                    "GstRt": tax_rate,
                    "TotItemVal": round(inv_line.price_subtotal + total_tax,2)}
                item_list.append(item_dict)

                print("item_dict===========================",total_igst,item_list)

        data['ItemList'] = item_list
        values = {
            "AssVal": round(total, 2),
            "RndOffAmt": round(total_round, 2),
            "Othchrg": round(tcs_amount, 2),
            "TotInvVal": round(self.amount_total,2),
            "IgstVal": round(total_igsts, 2),
            "CgstVal": round(total_cgsts, 2),
            "SgstVal": round(total_sgsts, 2),
        }
        print("valuesvalues--------values---->>>>>>>>>>>",values)
        data['ValDtls'] = values
        if self.eway_bill_gen:
            if not self.trans_id:
                raise UserError(_('Please Enter Transporter ID'))
            if not self.trans_name:
                raise UserError(_('Please Enter Transporter Name'))
            if not self.distance:
                raise UserError(_('Please Enter Distance'))
            if not self.transporter_docno:
                raise UserError(_('Please Enter Transporter Documnet Number'))
            if not self.transporter_docdt:
                raise UserError(_('Please Enter Transporter Document Date'))
            if not self.veh_no:
                raise UserError(_('Please Enter Transport Vehicle Number'))
            if not self.veh_type:
                raise UserError(_('Please Enter Transport Vehicle Type'))
            if not self.transMode:
                raise UserError(_('Please Enter Transport Mode'))
            eway_dict = {
                "Irn": self.irn_no,
                "Distance": self.distance,
                "TransMode": self.transMode,
                "TransId": self.trans_id,  # "12AWGPV7107B1Z1",
                "TransName": self.trans_name,
                "TrnDocDt": self.transporter_docdt.strftime("%m/%d/%Y"),
                "TrnDocNo": self.transporter_docno,
                "docNo": self.transporter_docno,
                "docDate": self.transporter_docdt.strftime("%m/%d/%Y"),
                "VehNo": self.veh_no,
                "VehType": self.veh_type,
                'TransporterId': self.trans_id or '',

            }
            data['EwbDtls'] = eway_dict

            dsdasdasdasdsad
        if einvoicing.testing == 't':
            url = 'http://gstsandbox.charteredinfo.com/eicore/dec/v1.03/Invoice?aspid=' + einvoicing.asp_id + '&password=' + einvoicing.asp_password + '&Gstin=' + warehouse.gst_no + '&AuthToken=' + warehouse.auth_token + '&user_name=' + warehouse.user_name + '&QRCodeSize=330'

        if einvoicing.testing == 'p':
            url = 'https://einvapi.charteredinfo.com/eicore/dec/v1.03/Invoice?aspid=' + einvoicing.asp_id + '&password=' + einvoicing.asp_password + '&Gstin=' + warehouse.gst_no + '&AuthToken=' + warehouse.auth_token + '&user_name=' + warehouse.user_name + '&QRCodeSize=330'

        headers = {'Content-Type':'application/json;charset=utf-8'}


        

        _logger.info("=====================tenure=%s=",url)
        _logger.info("=====================data====%s",data)
        response = requests.post(url, data=json.dumps(data), headers=headers)

        res = response.content
        # _logger.info('response============================%s',response)
        # print('==============headers====================>>>>>',res)

        _logger.info("=====================tenure==%s=",  res)
        res_dict = json.loads(res)
        # print("res_dict===>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",res_dict)
        _logger.info("respose True Or False=====================tenure==%s=", res_dict)
        if res_dict.get('Status') == '1':
            a = res_dict['Data']
            n = json.loads(a)
            qr_code = n['QrCodeImage']
            ackdt_no = n['AckDt']
            ack_no = n['AckNo']
            irn_no = n['Irn']
            ewbno = n['EwbNo']
            ewb_valid_till = n['EwbValidTill']
            ewb_date = n['EwbDt']
            self.qr_image = qr_code
            self.irn_no = irn_no
            self.ackdt_no = ackdt_no
            self.ack_no = ack_no
            self.invoice_number = ack_no
            # self.signed_invoice = qr_code
            self.inv_barcode = qr_code
            self.eway_bill_no = ewbno
            self.eway_valid_date = ewb_valid_till
            self.eway_date = ewb_date
            if self.eway_bill_no:
                self.env.user.notify_info(message='IRN Number and Eway Bill Created Successfully !')
            self.env.user.notify_info(message='IRN Number Created Successfully !')
        if res_dict.get('Status') == '0':
            raise UserError(_(res_dict.get('ErrorDetails')))

    def num_to_word_convert(self):
        number = int(self.amount_total)
        words = num2words(number)
        return words

    @api.multi
    def create_eway_bill(self):
        einvoicing = self.env['einvoicing.configuration'].search([], limit=1)
        warehouse = self.get_warehouse()
        _logger.info("=================%s",warehouse)
        data = einvoicing.handle_einvoicing_auth_token()
        # print('data----------->>>>>>>>>>>>>>.', data)
        if not warehouse.auth_token:
            raise UserError(_('Please Check Auth Token in E-Invoicing Configuration is Expired or Null.'))
        if not einvoicing.testing:
            raise UserError(_('Please Set Url Type in E-Invoicing Configuration.'))
        if not einvoicing.asp_id:
            raise UserError(_('Please Enter ASP-ID in E-Invoicing Configurations.'))
        if not einvoicing.asp_password:
            raise UserError(_('Please Enter ASP Password in E-Invoicing Configurations.'))
        if not warehouse.gst_no:
            raise UserError(_('Please Enter Registered GSTIN in E-Invoicing Configurations.'))
        if not warehouse.user_password:
            raise UserError(_('Please Enter User Password in E-Invoicing Configurations.'))
        if not warehouse.user_name:
            raise UserError(_('Please Enter User Name in E-Invoicing Configurations.'))
        if not self.sup_type:
            raise UserError(_('Please Select Sub-Type.'))
        if not self.doc_type:
            raise UserError(_('Please Select Doc-Type.'))
        if not self.distance:
            raise UserError(_('Please Enter Distance.'))
        if not self.transMode:
            raise UserError(_('Please Enter Transporter Mode.'))
        if not self.trans_name:
            raise UserError(_('Please Enter Transporter Name.'))
        if not self.transporter_docdt:
            raise UserError(_('Please Enter Transporter Document Date.'))
        if not self.transporter_docno:
            raise UserError(_('Please Enter Transporter Document Number.'))
        if not self.veh_no:
            raise UserError(_('Please Enter Vehicle Number.'))
        if not self.irn_no:
            raise UserError(_('IRN Number is not Generated.'))
        if not self.veh_type:
            raise UserError(_('Please Enter Vehicle Type.'))

        if not self.partner_id.name:
            raise UserError(_('Please Enter Buyer Name'))
        # if not self.partner_id.state_id.code:
        #     raise UserError(_('Please Enter Buyer State Code'))
        if not self.partner_id.city:
            raise UserError(_('Please Enter Buyer City'))
        if not self.partner_id.street:
            raise UserError(_('Please Enter Buyer Address line 1.'))
        if not self.partner_id.street2:
            raise UserError(_('Please Enter Buyer Address line2.'))
        if not self.partner_id.zip:
            raise UserError(_('Please Enter Buyer Pincode'))

        data1 = {
            "Irn": self.irn_no,
            "Distance": self.distance,
            "TransMode": self.transMode,
            "TransId": self.trans_id,
            "TransName": self.trans_name,
            "TrnDocDt": self.transporter_docdt.strftime("%m/%d/%Y"),
            "TrnDocDt": self.transporter_docno,
            "VehNo": self.veh_no,
            "docNo": self.transporter_docno,
            "docDate": self.transporter_docdt.strftime("%m/%d/%Y"),
            "VehType": self.veh_type,
            # 'TransporterId': self.trans_id or '',
        }

        SellerDtls = {
            "Gstin": self.company_id.vat,
            "LglNm": self.company_id.name,
            "Addr1": self.company_id.street,
            "Loc": self.company_id.city,
            # "TrdNm":'',
            "Pin": int(self.company_id.zip),
            "Stcd": self.company_id.state_id.code,
        }
        if self.partner_id.country_id.code != 'IN':
            BuyerDtls = {
                "Gstin": 'URP',
                "LglNm": self.partner_id.name,
                "Pos": str(96),
                "Addr1": self.partner_id.street,
                "Loc": self.partner_id.city,
                "Pin": int(999999),
                "Stcd": str(96)
            }
        else:
            BuyerDtls = {
                "Gstin": self.partner_id.vat,
                "LglNm": self.partner_id.name,
                "Pos": self.partner_id.state_id.code,
                "Addr1": self.partner_id.street,
                "Loc": self.partner_id.city,
                "Pin": int(self.partner_id.zip),
                "Stcd": self.partner_id.state_id.code, }

        DispDtls = {
                       "Nm": warehouse.partner_id.name,
                       "Addr1": warehouse.partner_id.street,
                       "Loc": warehouse.partner_id.city,
                       "Pin": int(warehouse.partner_id.zip),
                       "Stcd": warehouse.partner_id.state_id.stcd
                   },
        # if self.temp:
        #     ShipDtls = {
        #         "LglNm": self.contact_name,
        #         "Addr1": self.street,
        #         "Loc": self.city,
        #         "Pin": int(self.zip),
        #         "Stcd": self.state_id.code
        #     }
        # else:
        ShipDtls = {
            "LglNm": self.partner_id.name,
            "Addr1": self.partner_shipping_id.street + ','+ self.partner_shipping_id.street2,
            "Loc": self.partner_shipping_id.city,
            "Pin": int(self.partner_shipping_id.zip),
            "Stcd": self.partner_shipping_id.state_id.code
        }
        if self.transaction_type == '1':
            data1['SellerDtls'] = SellerDtls
            data1['BuyerDtls'] = BuyerDtls

        if self.transaction_type == '2':
            data1['SellerDtls'] = SellerDtls
            data1['BuyerDtls'] = BuyerDtls
            data1['ShipDtls'] = ShipDtls
        if self.transaction_type == '3':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['DispDtls'] = DispDtls

        if self.transaction_type == '4':
            data['SellerDtls'] = SellerDtls
            data['BuyerDtls'] = BuyerDtls
            data['ShipDtls'] = ShipDtls
            data['DispDtls'] = DispDtls

        if einvoicing.testing == 't':
            url = 'https://gstsandbox.charteredinfo.com/eiewb/dec/v1.03/ewaybill?aspid=' + einvoicing.asp_id + '&password=' + einvoicing.asp_password + '&Gstin=' + warehouse.gst_no + '&eInvPwd=' + warehouse.user_password + '&AuthToken=' + warehouse.auth_token + '&user_name=' + warehouse.user_name
        if einvoicing.testing == 'p':
            url = 'https://einvapi.charteredinfo.com/eiewb/dec/v1.03/ewaybill?aspid=' + einvoicing.asp_id + '&password=' + einvoicing.asp_password + '&Gstin=' + warehouse.gst_no + '&eInvPwd=' + warehouse.user_password + '&AuthToken=' + warehouse.auth_token + '&user_name=' + warehouse.user_name
        headers = {'Content-Type':'application/json;charset=utf-8'}
        response = requests.post(url, data=json.dumps(data1), headers=headers)

        res = response.content
        # _logger.info("=====================tenure==%s=",  res)
        res_dict = json.loads(res)
        if res_dict.get('Status') == '1':
            a = res_dict.get('Data')
            n = json.loads(a)
            eway_no = n['EwbNo']
            eway_date = n['EwbDt']
            eway_valid_till = n['EwbValidTill']
            self.eway_bill_no = eway_no
            self.eway_valid_date = eway_valid_till
            self.eway_bill_status = 'generated'
            self.eway_date = eway_date
            self.env.user.notify_info(message='Eway Bill Created Successfully !')
        if res_dict.get('Status') == '0':
            raise UserError(_(res_dict.get('ErrorDetails')))

        @api.onchange('eway_bill_no', 'eway_cancel_date')
        def onchange_ewaybill_status(self):
            if self.eway_bill_no:
                self.eway_bill_status = 'generated'

            if self.eway_bill_no and self.eway_cancel_date:
                self.eway_bill_status = 'cancel'

            if not self.eway_bill_no:
                self.eway_bill_status = 'not generated'

    @api.multi
    def print_eway_bill(self):
        Attachment = self.env['ir.attachment']
        details_response = self.get_eway_bill_details()
        det_response = details_response
        print_response = self.print_eway('printewb',det_response)
        attachment_data = {
            'name': 'EwayBill: ' + str(self.origin or '') + ':' + str(self.name),
            'datas_fname': 'EwayBill: ' + str(self.origin or '') + ':' + str(self.name)+'.pdf',
            'datas': base64.b64encode(print_response),
            'type': 'binary',
            'res_model': 'account.invoice',
            'res_id': self.id,
        }
        attachment = Attachment.create(attachment_data)
        self.env.user.notify_info(message='EwayBill Printed Successfully! Please check '
                                          'the attachments at the top.')
        return True


    def get_eway_details(self, action_name, ewaybill_no, warehouse):
        configuration = self.env['einvoicing.configuration'].search([], limit=1)
        # eway_url = configuration.eway_url_staging
        configuration.handle_einvoicing_auth_token()

        extra_url = 'aspid=' + configuration.asp_id + '&password=' + \
              configuration.asp_password + '&gstin=' + warehouse.gst_no + '&username=' + warehouse.user_name + \
              '&ewbpwd=' + warehouse.user_password + '&authtoken=' + warehouse.auth_token
        if configuration.testing == 't':
            resp = 'https://gstsandbox.charteredinfo.com/ewaybillapi/dec/v1.03/ewayapi?action=GetEwayBill' + '&' + extra_url + '&ewbNo=' + self.eway_bill_no
        if configuration.testing == 'p':
            resp = 'https://einvapi.charteredinfo.com/v1.03/dec/ewayapi?action=GetEwayBill' + '&' + extra_url + '&ewbNo=' + self.eway_bill_no
        return resp

    

    def get_eway_bill_details(self):
        configuration = self.env['einvoicing.configuration'].search([], limit=1)
        warehouse = self.get_warehouse()
        details_response = self.get_eway_details('GetEwayBill', self.eway_bill_no, warehouse)
        result = requests.get(details_response)
        return result.json()

    def print_eway(self, action_name, response):
        warehouse = self.get_warehouse()
        configuration = self.env['einvoicing.configuration'].search([], limit=1)
        full_print_url = 'https://einvapi.charteredinfo.com/aspapi/v1.0' + '/' + 'printewb' + '?aspid=' + configuration.asp_id +\
                             '&password=' + configuration.asp_password + '&Gstin=' + warehouse.gst_no 
        headers = {
            'Content-type': 'application/json'
        }
        resp = requests.post(full_print_url, data=json.dumps(response), headers=headers)
        return resp.content



class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    stcd = fields.Char('STCD')
