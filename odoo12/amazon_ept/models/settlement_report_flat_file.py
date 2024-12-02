from odoo import models, fields, api, _
from io import StringIO
import base64
import csv
from datetime import datetime
import time
from collections import defaultdict
from odoo.addons.iap.models import iap
from ..endpoint import DEFAULT_ENDPOINT
import dateutil.parser
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
class settlement_report_ept(models.Model):
    _inherit = "settlement.report.ept"

    def prepare_merchant_report_dict(self, seller, account, dbuuid, emipro_api):
        """
        @author: Deval Jagad (30/01/2020)
        :return: This method will prepare merchant' informational dictionary which will
                 passed to  amazon api calling method.
        """

        return {
            'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
            'auth_token': seller.auth_token and str(seller.auth_token) or False,
            'app_name': 'amazon_ept',
            'account_token': account.account_token,
            'emipro_api': emipro_api,
            'dbuuid': dbuuid,
            'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                       seller.country_id.code,
        }

    def prepare_attachments(self, data, marketplace, start_date, end_date, currency_rec):
        """
        :param data: Attachment data.
        :param marketplace: Market place.
        :param start_date: Selected start date in specific format.
        :param end_date: Selected end date in specific format.
        :param currency_rec: Currency from amazon.
        :return: This method will create attachments, attach it to settlement report's record and create a log an note.
        @:author: Deval Jagad (30/01/2020)
        """
        instance = self.env['amazon.marketplace.ept'].find_instance(self.seller_id, marketplace)

        data = data.encode('utf-8')
        result = base64.b64encode(data)
        file_name = "Settlement_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.csv'
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname':file_name,
            'res_model': 'mail.compose.message',
        })
        self.message_post(body=_("<b>Settlement Report Downloaded</b>"),
                          attachment_ids=attachment.ids)
        self.write({'attachment_id': attachment.id,
                    'start_date': start_date and start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date and end_date.strftime('%Y-%m-%d'),
                    'currency_id': currency_rec and currency_rec[0].id or False,
                    'instance_id': instance and instance[0].id or False
                    })

    def prepare_settlement_report_attachments_csv(self, response):
        """
        :param response: Create csv file attachment from response
        :author : Deval Jagad (30/01/2020)
        """
        data = response.get('data')
        if data:
            reader = csv.DictReader(data.splitlines(), delimiter='\t')
            start_date = ''
            end_date = ''
            currency_id = False
            marketplace = ''
            for row in reader:
                if marketplace:
                    break
                if not start_date:
                    start_date = dateutil.parser.parse(row.get('settlement-start-date'), dayfirst=True)
                if not end_date:
                    end_date = dateutil.parser.parse(row.get('settlement-end-date'), dayfirst=True)
                if not currency_id:
                    currency_id = self.env['res.currency'].search([('name', '=', row.get('currency'))])
                if not marketplace:
                    marketplace = row.get('marketplace-name')

            self.prepare_attachments(data, marketplace, start_date, end_date, currency_id)
        return True

    def get_report(self):
        """
        This method will get settlement report's attachment data from amazon and attach it with it's
        related settlement report.
        @author: Deval Jagad (30/01/2020)
        """
        self.ensure_one()
        if self.report_type=='_GET_V2_SETTLEMENT_REPORT_DATA_XML_':
            res = super(settlement_report_ept, self).get_report()
            return res
        seller = self.seller_id
        if not seller:
            raise Warning('Please select seller')

        if not self.report_id:
            return True

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

        kwargs = self.sudo().prepare_merchant_report_dict(seller, account, dbuuid,
                                                          emipro_api='amazon_settlement_report_v13')
        kwargs.update({'report_id': self.report_id, 'name': self.name})

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            self.prepare_settlement_report_attachments_csv(response)
        return True

    @api.multi
    def check_instance_configuration_and_attachment_file(self):
        """
        This method check in settlement report attachment exist or not
        Also check configuration of instance, Settlement Report Journal and Currency
        @author: Deval Jagad (30/01/2020)
        """
        if not self.attachment_id:
            raise Warning("There is no any report are attached with this record.")

        if not self.instance_id:
            raise Warning("Please select the Instance in report.")
        if not self.instance_id.settlement_report_journal_id:
            raise Warning(
                "You have not configured Settlement report Journal in Instance. "
                "\nPlease configured it first.")
        currency_id = self.instance_id.settlement_report_journal_id.currency_id.id or \
                      self.seller_id.company_id.currency_id.id or False
        if currency_id != self.currency_id.id:
            raise Warning(
                "Report currency and Currency in Instance Journal are different. "
                "\nMake sure Report currency and Instance Journal currency must be same.")

    def check_settlment_report_exist(self, settlement_id):

        """
        Process check bank statement record and settlement record exist or not
        @:param - settlement_id - unique id from csv file
        @author: Deval Jagad (30/01/2020)
        """

        bank_statement_obj = self.env['account.bank.statement']
        bank_statement_exist = bank_statement_obj.search(
            [('settlement_ref', '=', settlement_id)])
        if bank_statement_exist:
            settlement_exist = self.search([('statement_id', '=', bank_statement_exist.id)])
            if settlement_exist:
                self.write({'already_processed_report_id': settlement_exist.id,
                            'state': 'processed'})
            else:
                self.write({'statement_id': bank_statement_exist.id, 'state': 'processed'})
            return bank_statement_exist
        return False

    def create_settlement_report_bank_statement_line(self, total_amount, settlement_id,
                                                     bank_statement, deposit_date):

        """
        Process create and reconcile 'Total amount' bank statement line
        @:param - total amount - total amount of settlement report
        @:param - settlement_id - unique id from csv file
        @:param - bank_statement - account.bank.statement record create for settlement report
        @:param - deposite_date - deposite date of settlement report
        @author: Deval Jagad (30/01/2020)
        """

        bank_statement_line_obj = self.env['account.bank.statement.line']
        if self.instance_id.ending_balance_account_id and float(total_amount) != 0.0:
            bank_statement_line_obj = self.env['account.bank.statement.line']
            bank_line_vals = {
                'name': self.instance_id.ending_balance_description or "Ending Balance Description",
                'ref': settlement_id,
                'partner_id': False,
                'amount': -float(total_amount),
                'statement_id': bank_statement.id,
                'date': deposit_date,
                'amazon_code': self.instance_id.ending_balance_description or "Ending Balance Description",
                'sequence': 1000
            }
            line = bank_statement_line_obj.create(bank_line_vals)
            mv_dicts = {
                'name': self.instance_id.ending_balance_description or "Ending Balance Description",
                'account_id': self.instance_id.ending_balance_account_id.id,
                'credit': 0.0,
                'debit': 0.0,
            }
            if float(total_amount) < 0.0:
                mv_dicts.update({'credit': -float(total_amount)})
            else:
                mv_dicts.update({'debit': float(total_amount)})
            line.process_reconciliation(new_aml_dicts=[mv_dicts])

    def create_settlement_report_bank_statement(self, row, journal, settlement_id):

        """
        Process first check bank statement exist or not
        If not exist then create bank statement and
        create and reconcile 'Total amount' bank statement line
        @:param - row - whole row of csv file
        @:param - journal - configure in Amazon Marketplace
        @:param - settlement_id - unique id from csv file
        @author: Deval Jagad (30/01/2020)
        """
        bank_statement_obj = self.env['account.bank.statement']
        str_deposit_date = row.get('deposit-date')
        try:
            deposit_date = datetime.strptime(str_deposit_date, '%d.%m.%Y %H:%M:%S UTC')
        except:
            deposit_date = datetime.strptime(str_deposit_date, '%Y-%m-%d %H:%M:%S UTC')
        total_amount = float(row.get('total-amount').replace(',', '.'))
        start_date = self.start_date
        end_date = self.end_date

        bank_statement_exist = self.check_settlment_report_exist(settlement_id)
        if bank_statement_exist:
            return False

        name = '%s %s to %s ' % (self.instance_id.marketplace_id.name, start_date, end_date)
        vals = {
            'settlement_ref': settlement_id,
            'journal_id': journal.id,
            'date': self.end_date,
            'name': name,
            'balance_end_real': total_amount,
        }
        if self.instance_id.ending_balance_account_id:
            vals.update({'balance_end_real': 0.0})
        bank_statement = bank_statement_obj.create(vals)

        self.create_settlement_report_bank_statement_line(total_amount, settlement_id,
                                                          bank_statement, deposit_date)
        return bank_statement

    def make_amazon_fee_entry_csv(self,bank_statement,fees_type_dict):
        """
        :param bank_statement: settlement report bank statement
        :param fees_type_dict: dictionary for creating fees statement line
        :author: Deval Jagad (30/01/2020)
        """
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for fee_key, feed_type in fees_type_dict.items():
            for key,value in feed_type.items():
                name ="%s-%s" % (fee_key[0],key)
                bank_line_vals = {
                    'name': name,
                    'ref': bank_statement.settlement_ref,
                    'amount': value,
                    'statement_id': bank_statement.id,
                    'date': fee_key[1],
                    'amazon_code': key
                }
                bank_statement_line_obj.create(bank_line_vals)
        return True

    @api.model
    def convert_move_amount_currency_csv(self, bank_statement, moveline, amount, date):
        """This function is used to convert currency
            @author: Dimpal added on 14/oct/2019
        """
        amount_currency = 0.0
        if moveline.company_id.currency_id.id != bank_statement.currency_id.id:
            amount_currency = moveline.currency_id._convert(moveline.amount_currency,
                                                            bank_statement.currency_id,
                                                            bank_statement.company_id,
                                                            date)
        elif (moveline.invoice_id and moveline.invoice_id.currency_id.id != bank_statement.currency_id.id):
            amount_currency = moveline.invoice_id.currency_id._convert(amount,bank_statement.currency_id,
                                                                       bank_statement.company_id,
                                                                       date)
        currency = moveline.currency_id.id
        return currency, amount_currency

    def make_amazon_other_transactions_csv(self,seller, bank_statement, other_transactions):
        """
        :param seller: Seller set in settlement report
        :param bank_statement: settlement report bank statement
        :param other_transactions: dictionary for creating statement line for other transaction
        :author: Deval Jagad (30/01/2020)
        """
        transaction_obj = self.env['amazon.transaction.line.ept']
        account_invoice_obj = self.env['account.invoice']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        reimbursement_invoice = False
        reimbursement_invoices = []
        invoice_amount_line_dict = {}
        tran_type_inv = {}
        fees_transaction_list = {}
        trans_line_ids = transaction_obj.search([('seller_id', '=', seller.id)])

        for trans_line_id in trans_line_ids:
            transaction_type_id = trans_line_id.transaction_type_id
            fees_transaction_list.update({transaction_type_id.amazon_code:trans_line_id.id})
        for transaction,amount in other_transactions.items():
            trans_type =transaction[2]
            trans_id = transaction[2]
            date_posted = transaction[1]

            trans_type = trans_id if trans_type in ['other-transaction', 'FBA Inventory Reimbursement'] else trans_type
            trans_type_line_id = fees_transaction_list.get(trans_type) or fees_transaction_list.get(trans_id)
            trans_line = trans_type_line_id and transaction_obj.browse(trans_type_line_id)  ##[0]
            # trans_type_line_id = fees_transaction_list.get(trans_type)
            # trans_line = trans_type_line_id and transaction_obj.browse(trans_type_line_id)
            if trans_type:
                name = "%s/%s" % (trans_type, trans_id)
            if (not trans_line) or (
                    trans_line and not trans_line.transaction_type_id.is_reimbursement):
            # if trans_line and not trans_line.transaction_type_id.is_reimbursement:
                bank_line_vals = {
                    'name': name,
                    'ref': bank_statement.settlement_ref,
                    'amount': amount,
                    'statement_id': bank_statement.id,
                    'date': date_posted,
                    'amazon_code': trans_type
                }
                bank_statement_line_obj.create(bank_line_vals)
            elif trans_line and trans_line.transaction_type_id.is_reimbursement and \
                    trans_line.account_id:
                invoice_type = 'out_refund' if amount < 0.00 else 'out_invoice'
                reimbursement_invoice = account_invoice_obj.search([('id', 'in',reimbursement_invoices),
                                                                    ('date_invoice', '=', str(date_posted)),
                                                                    ('type', '=', invoice_type)],
                                                                   limit=1)
                if not reimbursement_invoice:
                    reimbursement_invoice = self.create_amazon_reimbursement_invoice(bank_statement, seller, str(date_posted),invoice_type)
                    reimbursement_invoices.append(reimbursement_invoice.id)
                amt = invoice_amount_line_dict.get(reimbursement_invoice, 0.0)
                # invoice_amount_line_dict.update({reimbursement_invoice: (amt + abs(amount),trans_type)})
                invoice_amount_line_dict.update({reimbursement_invoice:amt + amount})
                self.create_amazon_reimbursement_invoice_line(bank_statement, seller,
                                                              reimbursement_invoice, name, amount,
                                                              trans_line)
                tran_type_inv.update({reimbursement_invoice: trans_type})
        reimbursement_line = False
        reimbursement_invoices and self.write({'reimbursement_invoice_ids': [(6, 0, reimbursement_invoices)]})
        for invoice, amount in invoice_amount_line_dict.items():
            name = tran_type_inv.get(invoice)
            if not name:
                name = '%s-%s' % (invoice.id, 'Reimbursement')
            reimbursement_line = self.make_amazon_reimbursement_line_entry(bank_statement,
                                                                           invoice.date_invoice,
                                                                           {name: amount})
            self.reconcile_reimbursement_invoice(invoice, reimbursement_line, bank_statement)
        return True

    def check_or_create_invoice_if_not_exist(self, amz_order):
        """
        Check and create invoice for amz_order
        :param amz_order: amazon order set in statement line of settlement report
        "author: Deval Jagad (30/01/2020)
        """
        for order in amz_order:
            """default_fba_partner_id is fetched according to seller wise."""
            if order.amz_instance_id.seller_id.def_fba_partner_id.id == order.partner_id.id:
                continue

            if order.state == 'sale' and order.invoice_status == 'to invoice':
                try:
                    order._create_invoices()
                except:
                    pass
                for invoice in order.invoice_ids:
                    if invoice.state == 'draft' and invoice.type == 'out_invoice':
                        invoice.action_post()
        return True

    def process_settlement_orders_csv(self, bank_statement, settlement_id, orders):
        """
        Process will create bank statement line for orders
        :param bank_statement: bank statement set in settlement report
        :param settlement_id: current record of settlement report
        :param orders: dictionary of orders for creating statement line
        :author: Deval Jagad (30/01/2020)
        """
        sale_order_obj = self.env['sale.order']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for order_key, invoice_total in orders.items():
            orders = sale_order_obj.browse(order_key[1])
            if order_key[4] != 'MFN':
                search_orders = orders.filtered(
                    lambda l:round(l.amount_total, 10) == round(invoice_total, 10))
                if not search_orders:
                    orders = orders and orders[0]
                if len(orders.ids) > 1:
                    amz_order = orders and orders[0]
                else:
                    amz_order = orders
            else:
                amz_order = orders

            date_posted = order_key[2]
            partner_id = order_key[4]

            statment_line_domain = [('statement_id','=', bank_statement.id),
                                    ('ref','=',settlement_id),
                                    ('name', '=', order_key[0])]

            if amz_order:
                statment_line_domain.extend([('sale_order_id','=', amz_order.id)])

            statement_line_ids = bank_statement_line_obj.search(statment_line_domain)

            statement_line_ids and statement_line_ids.write({'amount':statement_line_ids.amount +
                                                                      invoice_total})

            if invoice_total > 0.0 and not statement_line_ids:
                bank_line_vals = {
                    'name':order_key[0],
                    'ref':settlement_id,
                    'partner_id':partner_id,
                    'amount':invoice_total,
                    'statement_id':bank_statement.id,
                    'date':date_posted,
                    'sale_order_id':amz_order.id
                }

                bank_statement_line_obj.create(bank_line_vals)
            if amz_order:
                self.check_or_create_invoice_if_not_exist(amz_order)
        return True

    @api.model
    def process_settlement_refunds_csv(self, bank_statement_id, settlement_id, refunds):
        """
        Process will create bank statement line for refund orders
        :param bank_statement: bank statement set in settlement report
        :param settlement_id: current record of settlement report
        :param refunds: dictionary of refunds for creating statement line
        :author: Deval Jagad (30/01/2020)
        """
        bank_statement_line_obj = self.env['account.bank.statement.line']
        refund_invoice_dict = defaultdict(dict)
        for order_key,refund_amount in refunds.items():
            orders =order_key[1]
            if order_key[3] != 'MFN':
                if len(orders)>1:
                    amz_order =orders[0]
                else:
                    amz_order =orders
            else:
                amz_order = orders and orders[0]
            partner_id =order_key[4]
            date_posted = order_key[2]

            if not refund_amount:
                continue
            bank_line_vals = {
                'name': 'Refund_' + order_key[0],
                'ref': settlement_id,
                'partner_id': partner_id,
                'amount': refund_amount,
                'statement_id': bank_statement_id,
                'date': date_posted,
                'is_refund_line': True,
                'sale_order_id': amz_order
            }

            bank_statement_line_obj.create(bank_line_vals)
        return refund_invoice_dict

    @api.model
    def create_refund_invoices_csv(self, refund_list_item_price, bank_statement):
        """
        :param refund_list_item_price: Dictonary for create refund invoice for orders
        :param bank_statement: settlement report bank statement
        :author: Deval Jagad (30/01/2020)
        """
        obj_invoice_line = self.env['account.invoice.line']
        sale_order_obj = self.env['sale.order']
        obj_invoice = self.env['account.invoice']
        for order_key, product_amount in refund_list_item_price.items():
            if not order_key[1]:
                continue
            order = sale_order_obj.browse(order_key[1])
            if len(order.ids) > 1:
                order = order[0]
            date_posted = order_key[2]
            product_ids = list(product_amount.keys())
            refund_exist = order.invoice_ids.filtered(lambda l:l.type == 'out_refund' and l.state not in ('cancel'))
            if not refund_exist:
                invoices = order.invoice_ids.filtered(lambda l:l.type == 'out_invoice').mapped('invoice_line_ids').filtered(lambda l:l.product_id.id in product_ids).mapped('invoice_id')
                if not invoices:
                    self.check_or_create_invoice_if_not_exist(order)
                    invoices = order.invoice_ids.filtered(lambda l:l.type == 'out_invoice').mapped('invoice_line_ids').filtered(lambda l:l.product_id.id in product_ids).mapped('invoice_id')
                if not invoices:
                    continue
                refund_record = obj_invoice.browse()

                journal_id = invoices[0].journal_id.id
                refund_invoice = invoices[0].refund(str(date_posted), str(date_posted), invoices[0].name, journal_id)

                refund_invoice.write({'date_invoice':str(date_posted), 'origin':order.name})
                extra_invoice_lines = obj_invoice_line.search(
                        [('invoice_id', '=', refund_invoice.id),
                         ('product_id', 'not in', product_ids)])
                if extra_invoice_lines:
                    extra_invoice_lines.unlink()
                for product_id, amount in product_amount.items():
                    amount = abs(amount)
                    invoice_lines = refund_invoice.invoice_line_ids.filtered(
                        lambda x:x.product_id.id == product_id)
                    exact_line = False
                    if len(invoice_lines.ids) > 1:
                        exact_line = refund_invoice.invoice_line_ids.filtered(lambda x:x.product_id.id == product_id)[0]
                        if exact_line:
                            other_lines = refund_invoice.invoice_line_ids.filtered(
                                    lambda
                                        x:x.product_id.id == product_id and x.id != exact_line.id)
                            other_lines.unlink()
                            exact_line.write({'quantity':1, 'price_unit':amount})
                    else:
                        invoice_lines.write({'quantity':1, 'price_unit':amount})

                refund_invoice.compute_taxes()
                refund_invoice.action_invoice_open()
            else:
                if refund_exist.state == 'draft':
                    refund_invoice.compute_taxes()
                    refund_invoice.action_invoice_open()
                refund_invoice = refund_exist
            lines = bank_statement.mapped('line_ids').filtered(lambda l:l.sale_order_id.id == order.id and not l.refund_invoice_id and l.is_refund_line and round(
                abs(l.amount), 10) == round(refund_invoice.amount_total, 10))
            lines and lines[0].write({'refund_invoice_id':refund_invoice.id})
        return True

    @api.multi
    def process_settlement_report_file(self):
        """
        Process the settlement report
        Create bank statement and statement line from flat file of attachment
        :author: Deval Jagad (30/01/2020)
        """
        self.ensure_one()
        if self.report_type=='_GET_V2_SETTLEMENT_REPORT_DATA_XML_':
            res = super(settlement_report_ept, self).process_settlement_report_file()
            return res
        self.check_instance_configuration_and_attachment_file()
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        content = imp_file.read()
        settlement_reader = csv.DictReader(content.splitlines(), delimiter='\t')
        journal = self.instance_id.settlement_report_journal_id
        seller = self.seller_id
        bank_statement = False
        settlement_id = ''
        order_list_item_price = {}
        order_list_item_fees = {}

        refund_list_item_price = {}
        create_or_update_refund_dict = {}
        amazon_product_obj = self.env['amazon.product.ept']
        sale_order_obj = self.env['sale.order']
        partner_obj = self.env['res.partner']
        amazon_other_transaction_list = {}
        product_dict = {}
        order_dict = {}
        for row in settlement_reader:
            settlement_id = row.get('settlement-id')
            if not bank_statement:
                bank_statement = self.create_settlement_report_bank_statement(row, journal,
                                                                              settlement_id)
                if not bank_statement:
                    break
            if not row.get('transaction-type'):
                continue
            order_ref = row.get('order-id')
            shipment_id = row.get('shipment-id')
            order_item_code = row.get('order-item-code')
            posted_date = row.get('posted-date')
            fulfllment_by = row.get('fulfillment-id')
            try:
                posted_date = datetime.strptime(posted_date, '%d.%m.%Y')
            except:
                posted_date = datetime.strptime(posted_date, '%Y-%m-%d')
            amount =float(row.get('amount').replace(',','.'))
            if row.get('transaction-type') in ['Order', 'Refund']:

                if row.get('amount-description').__contains__('MarketplaceFacilitator') or row.get(
                        'amount-type') == 'ItemFees':
                    key = (order_ref, posted_date, row.get('amount-description'))
                    if not order_list_item_fees.get(key):
                        order_list_item_fees.update({key:{row.get('amount-description'):amount}})
                    else:
                        existing_amount = order_list_item_fees.get(key).get(
                            row.get('amount-description'), 0.0)
                        order_list_item_fees.get(key).update(
                                {row.get('amount-description'):existing_amount + amount})
                    continue
                order_ids = order_dict.get((order_ref, shipment_id, order_item_code))
                if not order_ids:
                    if fulfllment_by == 'MFN':
                        amz_order = sale_order_obj.search([('amazon_reference', '=', order_ref),
                                                           ('amz_instance_id', '=',self.instance_id.id),
                                                           ('amz_fulfillment_by', '=', 'MFN'),
                                                           ('state', '!=', 'cancel')])
                    else:
                        domain = [
                            ('amz_instance_id', '=', self.instance_id.id),
                            ('amazon_reference', '=', order_ref),
                            ('amz_fulfillment_by','=',fulfllment_by),
                            ('state', '!=', 'cancel')
                        ]
                        if shipment_id:
                            domain.append(('picking_ids.amazon_shipment_id', '=', shipment_id))
                        amazon_order = sale_order_obj.search(domain)
                        amz_order = amazon_order and amazon_order.mapped('order_line').filtered(lambda x:x.amazon_order_item_id==order_item_code).mapped('order_id')
                        if not amz_order:
                            amz_order = amazon_order and amazon_order.mapped('order_line').filtered(lambda x:x.amazon_order_item_id == order_item_code[1:]).mapped('order_id')

                    order_ids = tuple(amz_order.ids)
                    order_dict.update({(order_ref, shipment_id, order_item_code):order_ids})

                partner = partner_obj._find_accounting_partner(amz_order.mapped('partner_id'))

                if row.get('transaction-type') == 'Order':

                    key = (order_ref, order_ids, posted_date, fulfllment_by, partner.id)
                    if not order_list_item_price.get(key):
                        order_list_item_price.update({key:amount})
                    else:
                        existing_amount = order_list_item_price.get(key, 0.0)
                        order_list_item_price.update({key:existing_amount + amount})

                elif row.get('transaction-type') == 'Refund':

                    product_id = product_dict.get(row.get('sku'))
                    if not product_id:
                        amazon_product = amazon_product_obj.search(
                                [('seller_sku', '=', row.get('sku')),
                                 ('instance_id', '=', self.instance_id.id)], limit=1)
                        product_id = amazon_product.product_id.id
                        product_dict.update({row.get('sku'):amazon_product.product_id.id})
                    key = (order_ref, order_ids, posted_date, fulfllment_by, partner.id)
                    if not refund_list_item_price.get(key):
                        refund_list_item_price.update({key:amount})
                    else:
                        existing_amount = refund_list_item_price.get(key, {})
                        refund_list_item_price.update({key:existing_amount + amount})

                    if not create_or_update_refund_dict.get(key):
                        create_or_update_refund_dict.update({key:{product_id:amount}})
                    else:
                        existing_amount = create_or_update_refund_dict.get(key).get(product_id, 0.0)
                        create_or_update_refund_dict.get(key).update(
                                {product_id:existing_amount + amount})

            else:
                key = (row.get('amount-type'), posted_date, row.get('amount-description'))
                existing_amount = amazon_other_transaction_list.get(key, 0.0)
                amazon_other_transaction_list.update({key:existing_amount + amount})
        if not bank_statement:
            return True

        self.make_amazon_fee_entry_csv(bank_statement,order_list_item_fees)

        amazon_other_transaction_list and self.make_amazon_other_transactions_csv(seller, bank_statement,
                                                                              amazon_other_transaction_list)

        order_list_item_price and self.process_settlement_orders_csv(bank_statement, settlement_id,
                                                                 order_list_item_price) or {}

        refund_list_item_price and self.process_settlement_refunds_csv(bank_statement.id, settlement_id,
                                                                   refund_list_item_price)

        # Create manually refund in ERP whose returned not found in the system
        if create_or_update_refund_dict:
            self.create_refund_invoices_csv(create_or_update_refund_dict, bank_statement)

        vals = {'statement_id':bank_statement.id, 'state':'imported'}
        self.write(vals)
        return True
    @api.model
    def remaining_order_refund_lines(self):
        """
        This function is used to get remaining order lines for reconciliation
        @author: Deval Jagad (30/01/2020)
        """
        sale_order_obj = self.env['sale.order']
        amazon_product_obj = self.env['amazon.product.ept']
        partner_obj = self.env['res.partner']
        """Case 1 : When sale order is imported at that time sale order is in quotation state,
        so after Importing Settlement report it will receive payment line for that invoice,
        system will not reconcile invoice of those orders, because pending quotation."""

        order_statement_lines = self.statement_id.mapped('line_ids').filtered(lambda x:not x.is_refund_line and not x.sale_order_id and not x.amazon_code and not x.journal_entry_ids)
        order_names = order_statement_lines.mapped('name')

        refund_lines = self.statement_id.mapped('line_ids').filtered(lambda x:x.is_refund_line and not x.amazon_code and not x.journal_entry_ids and x.sale_order_id)
        refund_names = refund_lines.mapped('name')
        refund_name_list = []
        for refund_name in refund_names:
            refund_name_list.append(refund_name.replace('Refund_', ''))
        if not order_names and not refund_names:
            return True

        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        content = imp_file.read()
        settlement_reader = csv.DictReader(content.splitlines(), delimiter='\t')
        order_dict = {}
        product_dict = {}
        create_or_update_refund_dict = {}
        for row in settlement_reader:
            if row.get('amount-type') != 'ItemPrice':
                continue
            order_ref = row.get('order-id')
            if order_ref not in order_names and order_ref not in refund_name_list:
                continue
            shipment_id = row.get('shipment-id')
            order_item_code = row.get('order-item-code')

            posted_date = row.get('posted-date')
            fulfllment_by = row.get('fulfillment-id')
            try:
                posted_date = datetime.strptime(posted_date, '%d.%m.%Y')
            except:
                posted_date = datetime.strptime(posted_date, '%Y-%m-%d')

            amount = float(row.get('amount').replace(',', '.'))
            order_ids = order_dict.get((order_ref, shipment_id, order_item_code))
            amz_order = False
            if not order_ids:
                if fulfllment_by == 'MFN':
                    amz_order = sale_order_obj.search([('amazon_reference', '=', order_ref),
                                                       ('amz_fulfillment_by', '=', 'MFN'),
                                                       ('state', '!=', 'cancel')])
                else:
                    domain = [
                        ('amz_instance_id', '=', self.instance_id.id),
                        ('amazon_reference', '=', order_ref),
                        ('amz_fulfillment_by', '=', fulfllment_by),
                        ('state', '!=', 'cancel')
                    ]
                    if shipment_id:
                        domain.append(('picking_ids.amazon_shipment_id', '=', shipment_id))
                    amazon_order = sale_order_obj.search(domain)
                    amz_order = amazon_order and amazon_order.mapped('order_line').filtered(lambda x:x.amazon_order_item_id == order_item_code).mapped('order_id')
                    if not amz_order:
                        amz_order = amazon_order and amazon_order.mapped('order_line').filtered(lambda x:x.amazon_order_item_id == order_item_code[1:]).mapped('order_id')
                    order_ids = tuple(amz_order.ids)
                    order_dict.update({(order_ref, shipment_id, order_item_code):order_ids})
            else:
                amz_order = sale_order_obj.browse(order_ids[0])
            if not amz_order:
                continue
            if amz_order.mapped('invoice_ids').filtered(lambda l:l.type=='out_refund'):
                continue
            partner = partner_obj._find_accounting_partner(amz_order.mapped('partner_id'))

            if order_ref in order_names and amz_order and row.get('transaction-type') == 'Order':
                order_statement_lines.filtered(lambda l:l.name == order_ref and not l.sale_order_id).write({'sale_order_id':amz_order.ids[0]})

            elif order_ref in refund_name_list and amz_order and row.get('transaction-type') == 'Refund':
                product_id = product_dict.get(row.get('sku'))
                if not product_id:
                    amazon_product = amazon_product_obj.search([('seller_sku', '=', row.get('sku')),
                                                                ('instance_id', '=',
                                                                 self.instance_id.id)], limit=1)
                    product_id = amazon_product.product_id.id
                    product_dict.update({row.get('sku'):amazon_product.product_id.id})
                key = (order_ref, order_ids, posted_date, fulfllment_by, partner.id)

                if not create_or_update_refund_dict.get(key):
                    create_or_update_refund_dict.update({key:{product_id:amount}})
                else:
                    existing_amount = create_or_update_refund_dict.get(key).get(product_id, 0.0)
                    create_or_update_refund_dict.get(key).update(
                            {product_id:existing_amount + amount})
                refund_lines.filtered(
                    lambda l:l.name == 'Refund_' + order_ref and not l.sale_order_id).write(
                        {'sale_order_id':amz_order.ids[0]})
        create_or_update_refund_dict and self.create_refund_invoices_csv(create_or_update_refund_dict,
                                                                     self.statement_id)
        return True


    def reconcile_reimbursement_lines(self, seller, bank_statement,statement_lines,fees_transaction_list):
        """
        :param seller: settlement report seller
        :param bank_statement: settlement report bank statement
        :param statement_lines: reimbursement line remainaing for reconcile
        :param fees_transaction_list: dictonary of transaction type and ids
        :author: Deval Jagad (30/01/2020)
        """
        transaction_obj = self.env['amazon.transaction.line.ept']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        account_invoice_obj = self.env['account.invoice']

        reimbursement_invoice = False
        invoice_amount_line_dict = {}
        rem_line_ids = []
        date_posted = False
        reimbursement_invoice_ids = self.reimbursement_invoice_ids.filtered(lambda l:l.state =='draft').ids
        statement_lines = bank_statement_line_obj.browse(statement_lines)
        for line in statement_lines:
            trans_line_id = fees_transaction_list.get(line.amazon_code)
            trans_line = transaction_obj.browse(trans_line_id)
            rem_line_ids.append(line.id)
            date_posted = line.date
            invoice_type = 'out_refund' if line.amount < 0.00 else 'out_invoice'
            reimbursement_invoice = account_invoice_obj.search(
                [('state', '=', 'draft'), ('id', 'in', reimbursement_invoice_ids),
                 ('date_invoice', '=', str(date_posted)),('type', '=', invoice_type)], limit=1)
            if not reimbursement_invoice:
                reimbursement_invoice = self.create_amazon_reimbursement_invoice(bank_statement, seller,
                                                                                 str(date_posted), invoice_type)
                self.write({'reimbursement_invoice_ids': [(4, reimbursement_invoice.id)]})
                reimbursement_invoice_ids.append(reimbursement_invoice.id)
            amt = invoice_amount_line_dict.get(reimbursement_invoice, 0.0)
            invoice_amount_line_dict.update({reimbursement_invoice: amt + line.amount})
            self.create_amazon_reimbursement_invoice_line(bank_statement, seller,
                                                          reimbursement_invoice, line.name,
                                                          line.amount, trans_line)

        rem_line_ids and bank_statement_line_obj.browse(rem_line_ids).unlink()
        for invoice, amount in invoice_amount_line_dict.items():
            name = '%s-%s' % (invoice.id, 'Reimbursement')
            reimbursement_line = self.make_amazon_reimbursement_line_entry(bank_statement,
                                                                           invoice.date_invoice,
                                                                           {name: amount})
            self.reconcile_reimbursement_invoice(invoice, reimbursement_line, bank_statement)
        return True

    def reconcile_orders(self, statement_lines):
        """
        This function is used to reconcile orders statement line which is generated from settlement
        report
        :author: Deval Jagad (30/01/2020)
        """
        statement_line_obj = self.env['account.bank.statement.line']
        invoice_obj = self.env['account.invoice']
        bank_statement = self.statement_id
        account_payment_obj = self.env['account.payment']
        for statement_line_id in statement_lines:
            statement_line = statement_line_obj.browse(statement_line_id)
            _logger.info(statement_line)
            invoices = invoice_obj.browse()
            order = statement_line.sale_order_id
            invoices = order.invoice_ids.filtered(lambda record: record.type == 'out_invoice')
            _logger.info(invoices)
            if not invoices:
                continue
            paid_invoices = invoices.filtered(lambda record : record.payment_ids.filtered(lambda l:l.state =='reconciled'))
            unpaid_invoices = invoices.filtered(lambda record :not record.payment_ids.filtered(lambda l:l.state =='reconciled'))
            _logger.info(paid_invoices)
            _logger.info(unpaid_invoices)

            mv_line_dicts = []
            move_line_total_amount = 0.0
            currency_ids = []
            paid_move_lines = False

            if paid_invoices:
                payment_id = account_payment_obj.search([('invoice_ids','in',paid_invoices.ids)])
                paid_move_lines = payment_id.mapped('move_line_ids').filtered(lambda x:x.debit!=0.0)
                for moveline in paid_move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency_csv(
                                bank_statement, moveline, amount, statement_line.date)
                        if currency:
                            currency_ids.append(currency)

                    if amount_currency:
                        amount = amount_currency

                    move_line_total_amount += amount
            if unpaid_invoices:
                move_lines = unpaid_invoices.mapped('move_id').mapped('line_ids').filtered(lambda l:l.account_id.user_type_id.type == 'receivable' and not l.reconciled)
                for moveline in move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency_csv (
                                bank_statement, moveline, amount , statement_line.date)
                        if currency:
                            currency_ids.append(currency)

                    if amount_currency:
                        amount = amount_currency
                    mv_line_dicts.append({
                        'credit':abs(amount) if amount > 0.0 else 0.0,
                        'name':moveline.move_id.name,
                        'move_line':moveline,
                        'debit':abs(amount) if amount < 0.0 else 0.0
                    })
                    move_line_total_amount += amount

            _logger.info(statement_line.amount)
            _logger.info(move_line_total_amount)
            
            if round(statement_line.amount, 10) == round(move_line_total_amount, 10) and (
                    not statement_line.currency_id or statement_line.currency_id.id == bank_statement.currency_id.id):
                if currency_ids:
                    currency_ids = list(set(currency_ids))
                    if len(currency_ids) == 1:
                        vals = {'amount_currency':move_line_total_amount}
                        statement_currency = statement_line.journal_id.currency_id and statement_line.journal_id.currency_id.id or statement_line.company_id.currency_id and statement_line.company_id.currency_id
                        if not currency_ids[0] == statement_currency:
                            vals.update({'currency_id':currency_ids[0]})
                        statement_line.write(vals)
                _logger.info("GO FOR RECONCILE")
                statement_line.process_reconciliation(mv_line_dicts,payment_aml_rec=paid_move_lines)
    def reconcile_refunds(self, statement_lines):
        """
        This function is used to reconcile refund's orders statement line which is generated from settlement report
        :author: Deval Jagad (30/01/2020)
        """
        statement_line_obj = self.env['account.bank.statement.line']
        mv_line_dicts = []
        move_line_total_amount = 0.0
        currency_ids = []
        paid_move_lines = False
        bank_statement = self.statement_id
        account_payment_obj = self.env['account.payment']

        for statement_line_id in statement_lines:
            statement_line = statement_line_obj.browse(statement_line_id)
            move_line_total_amount = 0.0
            mv_line_dicts = []
            if statement_line.refund_invoice_id.payment_ids.filtered(lambda l:l.state =='reconciled'):
                payment_id = account_payment_obj.search(
                        [('invoice_ids', 'in', statement_line.refund_invoice_id.ids),('state','=','reconciled')])
                paid_move_lines = payment_id.mapped('move_line_ids').filtered(
                    lambda x:x.debit != 0.0)

                for moveline in paid_move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency_csv(
                                bank_statement, moveline, amount, statement_line.date)
                        if currency:
                            currency_ids.append(currency)

                    if amount_currency:
                        amount = amount_currency

                    move_line_total_amount += amount
            else:
                unpaid_move_lines = statement_line.refund_invoice_id.mapped('move_id').mapped('line_ids').filtered(
                    lambda l:l.account_id.user_type_id.type == 'receivable' and not l.reconciled)

                for moveline in unpaid_move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency_csv(
                                bank_statement, moveline, amount, statement_line.date)
                        if currency:
                            currency_ids.append(currency)
                    if amount_currency:
                        amount = amount_currency
                    mv_line_dicts.append({
                        'credit':abs(amount) if amount > 0.0 else 0.0,
                        'name':moveline.move_id.name,
                        'move_line':moveline,
                        'debit':abs(amount) if amount < 0.0 else 0.0
                    })
                    move_line_total_amount += amount
            if round(statement_line.amount, 10) == round(move_line_total_amount, 10) and (
                    not statement_line.currency_id or statement_line.currency_id.id == bank_statement.currency.id):
                if currency_ids:
                    currency_ids = list(set(currency_ids))
                    if len(currency_ids) == 1:
                        statement_line.write({'amount_currency':move_line_total_amount,
                                              'currency_id':currency_ids[0]})
                statement_line.process_reconciliation(mv_line_dicts,
                                                      payment_aml_rec=paid_move_lines)
        return True

    def reconcile_remaining_transactions(self):
        """
        This function is used to reconcile remaining transaction of settlement report
        @author: Deval Jagad (30/01/2020)
        """
        statement_line_obj = self.env['account.bank.statement.line']
        _logger.info("=========================================Start Process=========================")
        if self.report_type=='_GET_V2_SETTLEMENT_REPORT_DATA_XML_':
            res = super(settlement_report_ept, self).reconcile_remaining_transactions()
            return res
        transaction_obj = self.env['amazon.transaction.line.ept']
        account_statement = self.statement_id
        if account_statement.state != 'open':
            return True
        _logger.info("=========================================check Refund lines=========================")
        self.remaining_order_refund_lines()
        self._cr.commit()
        fees_transaction_list = {}
        trans_line_ids = transaction_obj.search([('seller_id', '=', self.seller_id.id)])

        _logger.info("=========================================Reconcile Other lines=========================")
 
        for trans_line_id in trans_line_ids:
            transaction_type_id = trans_line_id.transaction_type_id
            if trans_line_id in fees_transaction_list:
                fees_transaction_list[transaction_type_id.amazon_code].append(
                        trans_line_id.id)
            else:
                fees_transaction_list.update({transaction_type_id.amazon_code:[trans_line_id.id]})

        statement_lines = self.statement_id.line_ids.filtered(lambda x:not x.journal_entry_ids
                                                                       and x.amazon_code != False).ids
        _logger.info(statement_lines)

        rei_lines = []
        for x in range(0, len(statement_lines), 10):
            lines = statement_lines[x:x + 10]
            for line_id in lines:
                line = statement_line_obj.browse(line_id)
                _logger.info(line)
                trans_line_id = fees_transaction_list.get(line.amazon_code)
                _logger.info(line.amazon_code)
                _logger.info(trans_line_id)
                if not trans_line_id:
                    continue                
                trans_line = transaction_obj.browse(trans_line_id)
                if trans_line[0].transaction_type_id.is_reimbursement:
                    rei_lines.append(line.id)
                    continue
                if trans_line and trans_line[0].account_id:
                    account_id = trans_line[0].account_id.id
                    mv_dicts = {
                        'name': line.name,
                        'account_id': account_id,
                        'debit': line.amount < 0 and -line.amount or 0.0,
                        'credit': line.amount > 0 and line.amount or 0.0,
                        'tax_ids': trans_line.tax_id and trans_line.tax_id.ids or []
                    }
                    line.process_reconciliation(new_aml_dicts=[mv_dicts])
            self._cr.commit()

        if rei_lines:
            self.reconcile_reimbursement_lines(self.seller_id, self.statement_id, rei_lines,fees_transaction_list)
        statement_lines = self.statement_id.line_ids.filtered(lambda x:x.journal_entry_ids.ids == [] and x.amazon_code == False and not x.is_refund_line and x.sale_order_id)

        _logger.info("=========================================Reconcile Order lines=========================")

        for x in range(0, len(statement_lines), 10):
            lines = statement_lines[x:x + 10]
            self.reconcile_orders(lines.ids)
            self._cr.commit()

        statement_lines = self.statement_id.line_ids.filtered(lambda x:x.journal_entry_ids.ids == []
                                                                       and x.amazon_code == False and x.is_refund_line and x.refund_invoice_id)
        _logger.info("=========================================Reconcile Refund lines=========================")

        for x in range(0, len(statement_lines), 10):
            lines = statement_lines[x:x + 10]
            self.reconcile_refunds(lines.ids)
            self._cr.commit()

        if not self.statement_id.line_ids.filtered(lambda x:x.journal_entry_ids.ids == []):
            self.write({'state': 'processed'})
        else:
            self.statement_id.line_ids.filtered(lambda x:x.journal_entry_ids.ids != [])
            if self.state != 'partially_processed':
                self.write({'state': 'partially_processed'})
        return True
