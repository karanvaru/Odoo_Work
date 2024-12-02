from datetime import datetime, timedelta
import time
import base64
from io import StringIO
import dateutil.parser
from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap
from ..models.api import DictWrapper

from ..endpoint import DEFAULT_ENDPOINT


class settlement_report_ept(models.Model):
    _name = "settlement.report.ept"
    _inherits = {"report.request.history": 'report_history_id'}
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = "Settlement Report"

    @api.multi
    def _get_reimbursement_invoices(self):
        for report in self:
            report.invoice_count = len(report.reimbursement_invoice_ids.ids)

    reimbursement_invoice_ids = fields.Many2many("account.invoice",
                                                 'amazon_rembursement_invoice_rel', 'report_id',
                                                 'invoice_id', string="Reimbursement Invoice")
    invoice_count = fields.Integer(compute="_get_reimbursement_invoices", string="Invoice Count")

    @api.multi
    def list_of_reimbursement_invoices(self):
        action = {
            'domain': "[('id', 'in', " + str(self.reimbursement_invoice_ids.ids) + " )]",
            'name': 'Reimbursement Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
        }
        return action

    def check_process_statement(self):
        for statement in self:
            if statement.statement_id and statement.statement_id.all_lines_reconciled:
                statement.is_processed = True
            else:
                statement.is_processed = False

    def _check_fee_exist(self):
        for record in self:
            is_fee = False
            unavailable_amazon_code = []
            state = record.state
            if state in ['imported', 'partially_processed', '_DONE_']:
                amazon_code_list = record.statement_id.line_ids.filtered(
                        lambda x: x.amazon_code != False and not x.journal_entry_ids).mapped(
                        'amazon_code')
                statement_amazon_code = amazon_code_list and list(set(amazon_code_list))
                transaction_amazon_code_list = record.seller_id.transaction_line_ids.filtered(
                        lambda x: x.amazon_code != False).mapped('amazon_code')
                missing_account_id_list = record.seller_id.transaction_line_ids.filtered(lambda l: not l.account_id).mapped('amazon_code')
                transaction_amazon_code = transaction_amazon_code_list and list(set(transaction_amazon_code_list))
                unavailable_amazon_code = [code for code in statement_amazon_code if
                                           code not in transaction_amazon_code or
                                           code in missing_account_id_list]

                if unavailable_amazon_code:
                    is_fee = True
            record.is_fees = is_fee

    name = fields.Char(size=256, string='Name', default='XML Settlement Report')
    report_history_id = fields.Many2one('report.request.history', string='Report', required=True,
                                        ondelete="cascade", index=True, auto_join=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    auto_generated = fields.Boolean('Auto Genrated Record ?', default=False)
    statement_id = fields.Many2one('account.bank.statement', string="Bank Statement")
    instance_id = fields.Many2one('amazon.instance.ept', string="Instance")
    currency_id = fields.Many2one('res.currency', string="Currency")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    is_processed = fields.Boolean("Processed ?", compute="check_process_statement", store=False)
    is_already_processed = fields.Boolean("Is already processed", default=False)
    already_processed_report_id = fields.Many2one("settlement.report.ept",
                                                  string="Already Processed Report")
    is_fees = fields.Boolean(string="Is Fee", compute='_check_fee_exist', store=False)

    @api.multi
    def closed_statement(self):
        self.statement_id.button_confirm_bank()
        return True

    @api.onchange('instance_id')
    def on_change_instnace(self):
        currency_id = False
        if self.instance_id and self.instance_id.settlement_report_journal_id:
            currency_id = self.instance_id and self.instance_id.settlement_report_journal_id and \
                          self.instance_id.settlement_report_journal_id.currency_id.id
        if not currency_id:
            currency_id = self.seller_id.company_id.currency_id.id
        self.currency_id = currency_id

    @api.onchange('seller_id')
    def on_change_seller_id(self):
        value = {}
        domain = {}
        if self.seller_id:
            seller = self.seller_id
            value.update(
                {'start_date': seller.settlement_report_last_sync_on, 'end_date': datetime.now()})
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
            domain['instance_id'] = [('id', 'in', instances.ids)]
        else:
            domain['instance_id'] = [('id', 'in', [])]
        return {'value': value, 'domain': domain}

    @api.multi
    def unlink(self):
        for report in self:
            if report.state == 'processed':
                raise Warning(_('You cannot delete processed report.'))
        return super(settlement_report_ept, self).unlink()

    @api.multi
    def find_unreconcile_lines(self, seller_id, bank_statement, amazon_code=False):
        transaction_obj = self.env['amazon.transaction.line.ept']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        amazon_seller_obj = self.env['amazon.seller.ept']
        seller = amazon_seller_obj.browse(seller_id)
        account_invoice_obj = self.env['account.invoice']

        other_lines_ids = []
        reimbursement_invoice = False
        invoice_amount_line_dict = {}
        tran_type_inv = {}
        rem_line_ids = []
        date_posted = False

        reimbursement_invoice_ids = self.reimbursement_invoice_ids.ids
        for invoice in self.reimbursement_invoice_ids:
            if invoice.state == 'open':
                invoice.action_invoice_cancel()
                invoice.action_invoice_draft()

        account_bank_statement_line_obj = self.env['account.bank.statement.line']
        if amazon_code:
            statement_lines = account_bank_statement_line_obj.search(
                [('statement_id', '=', self.statement_id.id), ('journal_entry_ids', '=', False),
                 ('amazon_code', '!=', False)])
        else:
            statement_lines = account_bank_statement_line_obj.search(
                [('statement_id', '=', self.statement_id.id), ('journal_entry_ids', '=', False),
                 ('amazon_code', '=', False)])

        for line in statement_lines:
            trans_line = transaction_obj.search(
                [('transaction_type_id.amazon_code', '=', line.amazon_code),
                 ('seller_id', '=', seller_id),
                 ('transaction_type_id.is_reimbursement', '=', True)])
            if trans_line:
                rem_line_ids.append(line.id)
                date_posted = line.date
            else:
                other_lines_ids.append(line.id)
            if trans_line:
                invoice_type = 'out_refund' if line.amount < 0.00 else 'out_invoice'
                reimbursement_invoice = account_invoice_obj.search(
                    [('state', '=', 'draft'), ('id', 'in', reimbursement_invoice_ids),
                     ('date_invoice', '=', date_posted),('type', '=', invoice_type)], limit=1)
                if not reimbursement_invoice:
                    reimbursement_invoice = self.create_amazon_reimbursement_invoice(bank_statement,
                                                                                     seller,
                                                                                     date_posted,
                                                                                     invoice_type)
                    self.write({'reimbursement_invoice_ids': [(4, reimbursement_invoice.id)]})
                    reimbursement_invoice_ids.append(reimbursement_invoice.id)
                amt = invoice_amount_line_dict.get(reimbursement_invoice, 0.0)
                invoice_amount_line_dict.update({reimbursement_invoice: amt + line.amount})
                self.create_amazon_reimbursement_invoice_line(bank_statement, seller,
                                                              reimbursement_invoice, line.name,
                                                              line.amount, trans_line)
                tran_type_inv.update({reimbursement_invoice.id:line.name})

        rem_line_ids and bank_statement_line_obj.browse(rem_line_ids).unlink()
        for invoice, amount in invoice_amount_line_dict.items():
            name = tran_type_inv.get(invoice.id)
            if not name:
                name = '%s-%s' % (invoice.id, 'Reimbursement')
            reimbursement_line = self.make_amazon_reimbursement_line_entry(bank_statement,
                                                                           invoice.date_invoice,
                                                                           {name: amount})
            self.reconcile_reimbursement_invoice(invoice, reimbursement_line, bank_statement)
        if other_lines_ids:
            return bank_statement_line_obj.browse(other_lines_ids)
        return []

    @api.multi
    def create_amazon_reimbursement_invoice_line(self, bank_statement, seller,
                                                 reimbursement_invoice,
                                                 name='REVERSAL_REIMBURSEMENT', amount=0.0,
                                                 trans_line=False):
        invoice_line_obj = self.env['account.invoice.line']
        reimbursement_product = seller.reimbursement_product_id
        # account_id=invoice_line_obj.get_invoice_line_account('out_invoice',
        # reimbursement_product,seller.reimbursement_customer_id.property_account_position_id
        # ,self.company_id)

        vals = {'product_id': reimbursement_product.id,
                'name': name,
                'invoice_id': reimbursement_invoice.id,
                #'account_id':account_id,
                'price_unit': amount,
                'quantity': 1,
                'uom_id': reimbursement_product.uom_id.id,
                }
        new_record = invoice_line_obj.new(vals)
        new_record._onchange_product_id()
        retval = invoice_line_obj._convert_to_write(
            {name: new_record[name] for name in new_record._cache})
        amount = abs(amount) if reimbursement_invoice.type=='out_refund' else amount
        retval.update({'price_unit': amount})
        trans_line and retval.update({'account_id': trans_line.account_id.id})
        if trans_line and trans_line.tax_id:
            tax_ids = [(6, 0, trans_line.tax_id.ids)]
            retval.update({'invoice_line_tax_ids': tax_ids})
        invoice_line_obj.create(retval)
        return True

    @api.multi
    def create_amazon_reimbursement_invoice(self, bank_statement, seller, date_posted, invoice_type):
        invoice_obj = self.env['account.invoice']
        partner_id = seller.reimbursement_customer_id.id
        account_id = seller.reimbursement_customer_id.property_account_receivable_id.id
        fiscal_position_id = seller.reimbursement_customer_id.property_account_position_id.id
        journal_id = seller.sale_journal_id.id
        invoice_vals = {
            'type': invoice_type,
            'reference': bank_statement.name,
            'account_id': account_id,
            'partner_id': partner_id,
            'journal_id': journal_id,
            'currency_id': self.currency_id.id,
            'amazon_instance_id': self.instance_id.id,
            'fiscal_position_id': fiscal_position_id,
            'company_id': self.company_id.id,
            'user_id': self._uid or False,
            'date_invoice': date_posted,
            'seller_id': self.instance_id and self.instance_id.seller_id and
                         self.instance_id.seller_id.id or False,
            # Comment added by twinkal[6-March] As field removed from the invoice
            # 'global_channel_id': self.instance_id and self.instance_id.seller_id and
            #                      self.instance_id.seller_id.global_channel_id and
            #                      self.instance_id.seller_id.global_channel_id.id or False,

        }
        reimbursement_invoice = invoice_obj.create(invoice_vals)
        return reimbursement_invoice

    @api.model
    def remaining_order_lines(self):
        sale_order_obj = self.env['sale.order']
        bank_statement_line_obj = self.env['account.bank.statement.line']

        """ Case 1 : When sale order is imported at that time sale order is in quotation state, 
        so after Importing Settlement report it will receive payment line for that invoice, 
        system will not reconcile invoice of those orders, because pending quotation."""

        domain = ['!', ('name', '=like', 'Refund_%'), ('journal_entry_ids', '=', False),
                  ('amazon_code', '=', False), ('statement_id', '=', self.statement_id.id)]
        order_statement_lines = bank_statement_line_obj.search(domain)
        for line in order_statement_lines:
            amz_orders = sale_order_obj.search(
                [('amazon_reference', '=', line.name), ('state', 'not in', ['draft', 'cancel'])])
            if amz_orders:
                if len(amz_orders) == 1:
                    line.write({'amazon_order_ids': [(4, amz_orders.id)]})
                else:
                    for amz_order in amz_orders:
                        if amz_order.amount_total == line.amount:
                            line.write({'amazon_order_ids': [(4, amz_order.id)]})
                            break
        return True

    @api.model
    def remianing_refund_lines(self):
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        refund_invoice_dict = defaultdict(dict)
        refund_stement_line_order_dict = {}
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        content = imp_file.read()
        response = DictWrapper(content, "Message")
        result = response.parsed
        settlement_reports = []
        fees_type_dict = {}
        if not isinstance(result.get('SettlementReport', []), list):
            settlement_reports.append(result.get('SettlementReport', []))
        else:
            settlement_reports = result.get('SettlementReport', [])

        refunds = []
        for report in settlement_reports:
            if not isinstance(report.get('Refund', {}), list):
                refunds.append(report.get('Refund', {}))
            else:
                refunds += report.get('Refund', [])

        domain = [('name', '=like', 'Refund_%'), ('journal_entry_ids', '=', False),
                  ('amazon_code', '=', False), ('statement_id', '=', self.statement_id.id)]
        refund_lines = bank_statement_line_obj.search(domain)

        refund_order_name = []
        refund_line_dict = {}
        for refund_line in refund_lines:
            if refund_line.amazon_order_ids:
                continue
            name = str(refund_line.name).replace('Refund_', '')
            refund_order_name.append(name)
            refund_line_dict.update({name: refund_line})
        if not refund_order_name:
            return True
        for refund in refunds:
            if not refund:
                continue
            order_ref = refund.get('AmazonOrderID', {}).get('value', '')
            if order_ref not in refund_order_name:
                continue
            statement_line = refund_line_dict.get(order_ref)
            fulfillment = refund.get('Fulfillment', {})

            item = fulfillment.get('AdjustedItem', {})
            date_posted = fulfillment.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            items = []
            amzon_orders = sale_order_obj.search(
                [('amazon_reference', '=', order_ref), ('state', '!=', 'cancel')], order="id")

            if not isinstance(item, list):
                items.append(item)
            else:
                items = item
            refund_total_amount = 0.0
            orders = sale_order_obj.browse()
            for item in items:
                order_item_code = item.get('AmazonOrderItemCode', {}).get('value', '')
                merchant_adjustment_item_id = item.get('MerchantAdjustmentItemID', {}).get('value',
                                                                                           '')
                order_line = sale_order_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                         ('amazon_order_item_id', '=',
                                                          order_item_code),
                                                         ('amz_merchant_adjustment_item_id', '=',
                                                          merchant_adjustment_item_id)
                                                         ])
                if not order_line:
                    order_line = sale_order_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                             ('amazon_order_item_id', '=',
                                                              order_item_code),
                                                             (
                                                                 'amz_merchant_adjustment_item_id', '=',
                                                                 False)
                                                             ])

                if not order_line:
                    order_line = sale_order_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                             ('amazon_order_item_id', '=',
                                                              order_item_code),
                                                             ])
                if order_line:
                    order_line = order_line[0]
                if order_line:
                    amz_order = order_line.order_id

                if not order_line:
                    continue
                item_price = item.get('ItemPriceAdjustments', {})
                component = item_price.get('Component', {})
                components = []
                if not isinstance(component, list):
                    components.append(component)
                else:
                    components = component
                product_total_amount = 0.0
                for component in components:
                    ttype = component.get('Type', {}).get('value', '')
                    if ttype and ttype.__contains__('MarketplaceFacilitator'):
                        fees_type_dict.update(
                            {ttype: float(component.get('Amount', {}).get('value', 0.0))})
                    else:
                        amount_refund = float(component.get('Amount', {}).get('value', 0.0))
                        product_total_amount += -amount_refund
                        refund_total_amount += amount_refund
                promotion_adjustment = item.get('PromotionAdjustment', {})
                promotions = []
                if promotion_adjustment and not isinstance(promotion_adjustment, list):
                    promotions.append(promotion_adjustment)
                else:
                    promotions = promotion_adjustment

                for promotion in promotions:
                    product_total_amount += - float(promotion.get('Amount', {}).get('value', 0.0))
                    refund_total_amount += float(promotion.get('Amount', {}).get('value', 0.0))

                #                 if order_line:
                if amz_order in refund_invoice_dict:
                    product_total_amount += refund_invoice_dict.get(amz_order, {}).get(
                        order_line.product_id.id, 0.0)
                    refund_invoice_dict.get(amz_order).update(
                        {order_line.product_id.id: product_total_amount})
                else:
                    refund_invoice_dict[amz_order].update(
                        {order_line.product_id.id: product_total_amount})
                if not 'date_posted' in refund_invoice_dict.get(amz_order, {}):
                    refund_invoice_dict.get(amz_order).update({'date_posted': date_posted})
                if amz_order not in orders:
                    orders += amz_order
                order_line.write({'amz_merchant_adjustment_item_id': merchant_adjustment_item_id})

            if not refund_total_amount:
                continue
            if orders:
                if orders in refund_stement_line_order_dict:
                    statement_line += refund_stement_line_order_dict.get(orders)
                refund_stement_line_order_dict.update({orders: statement_line})
                order_ids = []
                for line in statement_line:
                    order_ids += line.amazon_order_ids.ids + orders.ids
                statement_line.write({'amazon_order_ids': [(6, 0, list(set(order_ids)))]})

        """ Create manually refund in ERP whose returned not found in the system"""
        if refund_invoice_dict:
            self.create_refund_invoices(refund_invoice_dict, self.statement_id)
        return True

    @api.multi
    def process_configute_transactions(self, line, amazon_code, seller_id):
        transaction_obj = self.env['amazon.transaction.line.ept']
        trans_line = transaction_obj.search(
            [('amazon_code', '=', amazon_code), ('seller_id', '=', seller_id)], limit=1)
        if trans_line and trans_line[0].account_id:
            account_id = trans_line[0].account_id.id
            mv_dicts = {
                'account_id': account_id,
                'debit': line.amount < 0 and -line.amount or 0.0,
                'credit': line.amount > 0 and line.amount or 0.0,
                'tax_ids': trans_line.tax_id and trans_line.tax_id.ids or []
            }
            if line.amount < 0.0:
                mv_dicts.update({'debit': -line.amount})
            else:
                mv_dicts.update({'credit': line.amount})
            line.process_reconciliation(new_aml_dicts=[mv_dicts])
        return True

    @api.multi
    def reconcile_remaining_transactions(self):
        transaction_obj = self.env['amazon.transaction.line.ept']
        account_statement = self.statement_id
        if account_statement.state != 'open':
            return True

        self.remaining_order_lines()
        self.remianing_refund_lines()
        self._cr.commit()

        statement_lines = self.find_unreconcile_lines(self.seller_id.id, account_statement, True)
        for x in range(0, len(statement_lines), 20):
            lines = statement_lines[x:x + 20]
            for line in lines:
                trans_line = transaction_obj.search(
                    [('amazon_code', '=', line.amazon_code), ('seller_id', '=', self.seller_id.id)],
                    limit=1)
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
        statement_lines = self.find_unreconcile_lines(self.seller_id.id, account_statement, False)
        for x in range(0, len(statement_lines), 20):
            lines = statement_lines[x:x + 20]
            self.reconcile_bank_statement(lines)
            self._cr.commit()
        return True

    @api.multi
    def reconcile_bank_statement(self, statement_lines):
        statement_line_obj = self.env['account.bank.statement.line']
        move_line_obj = self.env['account.move.line']
        invoice_obj = self.env['account.invoice']
        bank_statement = self.statement_id
        for statement_line in statement_lines:
            if statement_line.amazon_order_ids and not statement_line.refund_invoice_ids:
                invoices = invoice_obj.browse()
                for order in statement_line.amazon_order_ids:
                    invoices += order.invoice_ids

                invoices = invoices.filtered(
                    lambda record: record.type == 'out_invoice' and record.state in ['open'])
                account_move_ids = list(map(lambda x: x.move_id.id, invoices))
                move_lines = move_line_obj.search([('move_id', 'in', account_move_ids),
                                                   ('user_type_id.type', '=', 'receivable'),
                                                   ('reconciled', '=', False)])
                mv_line_dicts = []
                move_line_total_amount = 0.0
                currency_ids = []
                for moveline in move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency(
                            bank_statement, moveline, amount)
                        if currency:
                            currency_ids.append(currency)

                    if amount_currency:
                        amount = amount_currency
                    mv_line_dicts.append({
                        'credit': abs(amount) if amount > 0.0 else 0.0,
                        'name': moveline.invoice_id.number,
                        'move_line': moveline,
                        'debit': abs(amount) if amount < 0.0 else 0.0
                    })
                    move_line_total_amount += amount

                if round(statement_line.amount, 10) == round(move_line_total_amount, 10) and (
                        not statement_line.currency_id or statement_line.currency_id.id == bank_statement.currency_id.id):
                    if currency_ids:
                        currency_ids = list(set(currency_ids))
                        if len(currency_ids) == 1:
                            statement_line.write({'amount_currency': move_line_total_amount,
                                                  'currency_id': currency_ids[0]})
                    statement_line.process_reconciliation(mv_line_dicts)
            elif statement_line.refund_invoice_ids:
                account_move_ids = []
                invoices = statement_line.refund_invoice_ids
                for invoice in invoices:
                    if invoice and invoice.move_id:
                        account_move_ids.append(invoice.move_id.id)
                move_lines = move_line_obj.search([('move_id', 'in', account_move_ids),
                                                   ('user_type_id.type', '=', 'receivable'),
                                                   ('reconciled', '=', False)])
                mv_line_dicts = []
                move_line_total_amount = 0.0
                currency_ids = []
                for moveline in move_lines:
                    amount = moveline.debit - moveline.credit
                    amount_currency = 0.0
                    if moveline.amount_currency:
                        currency, amount_currency = self.convert_move_amount_currency(
                            bank_statement, moveline, amount)
                        if currency:
                            currency_ids.append(currency)
                    if amount_currency:
                        amount = amount_currency
                    mv_line_dicts.append({
                        'credit': abs(amount) if amount > 0.0 else 0.0,
                        'name': moveline.invoice_id.number,
                        'move_line': moveline,
                        'debit': abs(amount) if amount < 0.0 else 0.0
                    })

                    move_line_total_amount += amount

                if round(statement_line.amount, 10) == round(move_line_total_amount, 10) and (
                        not statement_line.currency_id or statement_line.currency_id.id == bank_statement.currency.id):
                    if currency_ids:
                        currency_ids = list(set(currency_ids))
                        if len(currency_ids) == 1:
                            statement_line.write({'amount_currency': move_line_total_amount,
                                                  'currency_id': currency_ids[0]})
                    statement_line.process_reconciliation(mv_line_dicts)
            if not statement_line_obj.search(
                    [('journal_entry_ids', '=', False), ('statement_id', '=', bank_statement.id)]):
                self.write({'state': 'processed'})
            elif statement_line_obj.search(
                    [('journal_entry_ids', '!=', False), ('statement_id', '=', bank_statement.id)]):
                if self.state != 'partially_processed':
                    self.write({'state': 'partially_processed'})
        return True

    def auto_import_settlement_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].browse(seller_id)
            if not seller:
                return True
            if seller.settlement_report_last_sync_on:
                start_date = seller.settlement_report_last_sync_on
                start_date = datetime.strftime(start_date, '%Y-%m-%d %H:%M:%S')
                start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                start_date = earlier.strftime("%Y-%m-%d %H:%M:%S")
            date_end = datetime.now()
            date_end = date_end.strftime("%Y-%m-%d %H:%M:%S")

            vals = {'report_type': '_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_',
                    'name': 'Amazon Settlement Reports',
                    'model_obj': self.env['settlement.report.ept'],
                    'sequence': self.env.ref('amazon_ept.seq_import_settlement_report_job'),
                    'tree_id': self.env.ref('amazon_ept.amazon_settlement_report_tree_view_ept'),
                    'form_id': self.env.ref('amazon_ept.amazon_settlement_report_form_view_ept'),
                    'res_model': 'settlement.report.ept',
                    'start_date': start_date,
                    'end_date': date_end
                    }
            report_wiz_rec = self.env['amazon.process.import.export'].create({
                'seller_id': seller_id,
               'start_date': start_date,
                'end_date': date_end,
                'selling_on':'fba_fbm',
                'both_operations' :'list_settlement_report',
            })
            report_wiz_rec.with_context({'is_auto_process': args.get('is_auto_process', False)}).get_reports(vals)
            seller.write({'settlement_report_last_sync_on': date_end})

        return True

    @api.model
    def auto_process_settlement_report(self, args={}):
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].search([('id', '=', seller_id)])
            settlement_reports = self.search([('seller_id', '=', seller.id),
                                              ('state', 'in', ['_DONE_', 'imported']),
                                              ('report_id', '!=', False)
                                              ], limit=1)
            for report in settlement_reports:
                if report.state == 'imported':
                    report.reconcile_remaining_transactions()
                else:
                    report.get_report()
                    if report.instance_id:
                        report.process_settlement_report_file()
                        self._cr.commit()
                        report.reconcile_remaining_transactions()
                    else:
                        report.write({'state': 'processed'})
        return True

    @api.multi
    def get_report(self):
        self.ensure_one()
        seller = self.seller_id
        amazon_transaction_obj = self.env['amazon.transaction.log']
        amazon_log_book_obj = self.env['amazon.process.log.book']
        job = False
        if not seller:
            raise Warning('Please select seller')
        proxy_data = seller.get_proxy_server()
        if not self.report_id:
            return True

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'amazon_sale_report',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                             seller.country_id.code,
                  'proxies': proxy_data,
                  'report_id': self.report_id,
                  'name': self.name}

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)

        if response.get('reason'):
            if self._context.get('is_auto_process'):
                job_log_vals = {
                    'message': 'Settlement Report Process',
                    'application': 'account',
                    'operation_type': 'import',
                }
                job = amazon_log_book_obj.create(job_log_vals)

                log_line_vals = {
                    'model_id': self.env['amazon.transaction.log'].get_model_id(
                        'settlement.report.ept'),
                    'log_type': 'error',
                    'skip_record': True,
                    'message': response.get('reason'),
                    'job_id': job.id
                }
                amazon_transaction_obj.create(log_line_vals)
            else:
                raise Warning(response.get('reason'))

        else:
            result = response.get('result')
            data = response.get('data')

            if isinstance(result.get('SettlementReport', []), list):
                settlement_report = result.get('SettlementReport', [])[0]
            else:
                settlement_report = result.get('SettlementReport', {})
            orders = []
            if not isinstance(settlement_report.get('Order', {}), list):
                orders.append(settlement_report.get('Order', {}))
            else:
                orders = settlement_report.get('Order', [])

            settlement_data = settlement_report.get('SettlementData', {})
            currency = settlement_data.get('TotalAmount', {}).get('currency', {}).get('value', '')
            start_date = settlement_data.get('StartDate', {}).get('value', '')
            end_date = settlement_data.get('EndDate', {}).get('value', '')
            start_date = dateutil.parser.parse(start_date)
            end_date = dateutil.parser.parse(end_date)
            currency_rec = self.env['res.currency'].search([('name', '=', currency)])
            marketplace = orders and orders[0].get('MarketplaceName', {}).get('value', '') or ''

            """added by Dhruvi if report consist of refund data"""

            if not marketplace:
                refund = []
                if not isinstance(settlement_report.get('Refund', {}), list):
                    refund.append(settlement_report.get('Refund', {}))
                else:
                    refund = settlement_report.get('Refund', {})

                marketplace = refund and refund[0].get('MarketplaceName', {}).get('value') or ''

            instance = self.env['amazon.marketplace.ept'].find_instance(seller, marketplace)

            data = data.encode('utf-8')
            result = base64.b64encode(data)
            file_name = "Settlement_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.xml'
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'datas': result,
                'datas_fname':file_name,
                'res_model': 'mail.compose.message',
                # 'type': 'binary'
            })
            self.message_post(body=_("<b>Settlement Report Downloaded</b>"),
                              attachment_ids=attachment.ids)
            self.write({'attachment_id': attachment.id,
                        'start_date': start_date and start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date and end_date.strftime('%Y-%m-%d'),
                        'currency_id': currency_rec and currency_rec[0].id or False,
                        'instance_id': instance and instance[0].id or False
                        })
        return True

    @api.multi
    def download_report(self):
        self.ensure_one()
        if self.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (self.attachment_id.id),
                'target': 'self',
            }
        return True

    @api.multi
    def make_amazon_advertising_transactions(self, seller, bank_statement,
                                             advertising_transactions):
        for transaction in advertising_transactions:
            trans_type = transaction.get('TransactionType', {}).get('value', '')
            amount = float(transaction.get('TransactionAmount', {}).get('value', 0.0))
            date_posted = transaction.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            invoice_id = transaction.get('InvoiceId', {}).get('value', time.strftime('%Y-%m-%d'))
            self.make_amazon_fee_entry(seller, bank_statement, date_posted, {trans_type: amount},
                                       order_ref=invoice_id)
        return True

    @api.multi
    def make_amazon_other_transactions(self, seller, bank_statement, other_transactions):
        transaction_obj = self.env['amazon.transaction.line.ept']
        account_invoice_obj = self.env['account.invoice']
        reimbursement_invoice = False
        reimbursement_invoices = []
        invoice_amount_line_dict = {}
        tran_type_inv = {}
        for transaction in other_transactions:
            ref_name = transaction.get('AmazonOrderID', {}).get('value')
            if not transaction:
                continue
            sku = False
            other_transactions_items = transaction.get('OtherTransactionItem', {})
            if not isinstance(other_transactions_items, list):
                other_transactions_items = [other_transactions_items]
            for other_transactions_item in other_transactions_items:
                if other_transactions_item:
                    if not sku:
                        sku = other_transactions_item.get('SKU', {}).get('value')
                    else:
                        sku = "%s/%s" % (sku, other_transactions_item.get('SKU', {}).get('value'))
            trans_type = transaction.get('TransactionType', {}).get('value', '')
            trans_id = transaction.get('TransactionID', {}).get('value')
            amount = float(transaction.get('Amount', {}).get('value', 0.0))
            date_posted = transaction.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            amazon_order_ref = transaction.get('AmazonOrderID', {}) and transaction.get(
                'AmazonOrderID', {}).get('value') or False
            trans_line = transaction_obj.search(
                [('transaction_type_id.amazon_code', '=', trans_type),
                 ('seller_id', '=', seller.id),
                 ('transaction_type_id.is_reimbursement', '=', True)])
            name = ''
            name = amazon_order_ref
            if trans_type:
                name = name and "%s/%s" % (name, trans_type) or trans_type
            if trans_id:
                name = name and "%s/%s" % (name, trans_id) or trans_id
            if sku:
                name = name and "%s/sku-%s" % (name, sku) or sku

            if not trans_line:
                self.make_amazon_fee_entry(seller, bank_statement, date_posted,
                                           {trans_type: amount}, order_ref='', rei_name=name)
            else:
                invoice_type = 'out_refund' if amount < 0.00 else 'out_invoice'
                reimbursement_invoice = account_invoice_obj.search(
                    [('id', 'in', reimbursement_invoices), ('date_invoice', '=', date_posted),('type', '=', invoice_type)],
                    limit=1)
                if not reimbursement_invoice:
                    reimbursement_invoice = self.create_amazon_reimbursement_invoice(bank_statement,
                                                                                     seller,
                                                                                     date_posted,
                                                                                     invoice_type)
                    reimbursement_invoice.update(
                        {'reimbursement_id': trans_id, 'name': ref_name or False})
                    reimbursement_invoices.append(reimbursement_invoice.id)
                amt = invoice_amount_line_dict.get(reimbursement_invoice, 0.0)
                invoice_amount_line_dict.update({reimbursement_invoice: amt + amount})
                self.create_amazon_reimbursement_invoice_line(bank_statement, seller,
                                                              reimbursement_invoice, name, amount,
                                                              trans_line)
                tran_type_inv.update({reimbursement_invoice: trans_type})
        reimbursement_line = False
        reimbursement_invoices and self.write(
            {'reimbursement_invoice_ids': [(6, 0, reimbursement_invoices)]})
        for invoice, amount in invoice_amount_line_dict.items():
            name = tran_type_inv.get(invoice)
            if not name:
                name = '%s-%s' % (invoice.id, 'Reimbursement')
            reimbursement_line = self.make_amazon_reimbursement_line_entry(bank_statement,
                                                                           invoice.date_invoice,
                                                                           {name: amount})
            self.reconcile_reimbursement_invoice(invoice, reimbursement_line, bank_statement)
        return True

    @api.multi
    def make_amazon_charge_back(self, seller, bank_statement, charge_back_list, settlement_id):
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for charge_back in charge_back_list:
            charge_back_item = []
            order_ref = charge_back.get('AmazonOrderID', {}).get('value')
            amazon_order = self.env['sale.order'].search([('amazon_reference', '=', order_ref)])
            price = 0.0
            if not isinstance(charge_back.get('Fulfillment', {}).get('AdjustedItem', []), list):
                charge_back_item.append(charge_back.get('Fulfillment', {}).get('AdjustedItem', []))
            else:
                charge_back_item = charge_back.get('Fulfillment', {}).get('AdjustedItem')

            for item in charge_back_item:
                item_price = item.get('ItemPriceAdjustments', {})
                component = item_price.get('Component', {})
                components = []
                if not isinstance(component, list):
                    components.append(component)
                else:
                    components = component
                for component in components:
                    amount_refund = float(component.get('Amount', {}).get('value', 0.0))
                    price += amount_refund
            date_posted = charge_back.get('Fulfillment').get('PostedDate', {}).get('value',
                                                                                   time.strftime(
                                                                                       '%Y-%m-%d'))
            bank_line_vals = {
                'name': 'Charge Back-' + order_ref,
                'ref': settlement_id,
                'partner_id': amazon_order and amazon_order.partner_id and amazon_order.partner_id.id,
                'amount': price,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'amazon_code': 'Chargeback'
            }
            bank_statement_line_obj.create(bank_line_vals)
            fees_type_dict = {}
            for item in charge_back_item:
                item_fees = item.get('ItemFeeAdjustments', {})
                fees = item_fees.get('Fee', [])
                fees_list = []
                if not isinstance(fees, list):
                    fees_list.append(fees)
                else:
                    fees_list = fees

                for fee in fees_list:
                    fee_type = fee.get('Type').get('value')
                    fee_amount = float(fee.get('Amount', {}).get('value', 0.0))
                    if fee_type in fees_type_dict:
                        fees_type_dict[fee_type] = fees_type_dict[fee_type] + fee_amount
                    else:
                        fees_type_dict.update({fee_type: fee_amount})
            self.make_amazon_fee_entry(seller, bank_statement, date_posted, fees_type_dict,
                                       order_ref)

        return True

    @api.multi
    def make_amazon_guarantee_claim(self, seller, bank_statement, guarantee_claim, settlement_id):
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for claim_record in guarantee_claim:
            adjust_item = []
            order_ref = claim_record.get('AmazonOrderID', {}).get('value')
            amazon_order = self.env['sale.order'].search([('amazon_reference', '=', order_ref)])
            price = 0.0
            if not isinstance(claim_record.get('Fulfillment', {}).get('AdjustedItem', []), list):
                adjust_item.append(claim_record.get('Fulfillment', {}).get('AdjustedItem', []))
            else:
                adjust_item = claim_record.get('Fulfillment', {}).get('AdjustedItem')

            for item in adjust_item:
                item_price = item.get('ItemPriceAdjustments', {})
                component = item_price.get('Component', {})
                components = []
                if not isinstance(component, list):
                    components.append(component)
                else:
                    components = component
                for component in components:
                    amount_refund = float(component.get('Amount', {}).get('value', 0.0))
                    price += amount_refund
            date_posted = claim_record.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            bank_line_vals = {
                'name': 'GuaranteeClaim-' + order_ref,
                'ref': settlement_id,
                'partner_id': amazon_order and amazon_order.partner_id and amazon_order.partner_id.id,
                'amount': price,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'amazon_code': 'GuaranteeClaim'
            }
            bank_statement_line_obj.create(bank_line_vals)
            fees_type_dict = {}
            for item in adjust_item:
                item_fees = item.get('ItemFeeAdjustments', {})
                fees = item_fees.get('Fee', [])
                fees_list = []
                if not isinstance(fees, list):
                    fees_list.append(fees)
                else:
                    fees_list = fees

                for fee in fees_list:
                    fee_type = fee.get('Type').get('value')
                    fee_amount = float(fee.get('Amount', {}).get('value', 0.0))
                    if fee_type in fees_type_dict:
                        fees_type_dict[fee_type] = fees_type_dict[fee_type] + fee_amount
                    else:
                        fees_type_dict.update({fee_type: fee_amount})
            self.make_amazon_fee_entry(seller, bank_statement, date_posted, fees_type_dict,
                                       order_ref)
        return True

    @api.multi
    def create_retro_charge(self, seller, bank_statement, retro_charge_list, settlement_id,
                            amazon_code='Retrocharge'):
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for retro_charge in retro_charge_list:
            order_ref = retro_charge.get('AmazonOrderID', {}).get('value')
            amazon_order = self.env['sale.order'].search(
                [('amazon_reference', '=', order_ref), ('amz_instance_id', 'in', seller.instance_ids.ids)], limit=1)
            price = 0.0
            base_tax = []
            if not isinstance(retro_charge.get('BaseTax', {}), list):
                base_tax.append(retro_charge.get('BaseTax', {}))
            else:
                base_tax = retro_charge.get('BaseTax', {})
            shipping_tax = []
            if not isinstance(retro_charge.get('ShippingTax', {}), list):
                shipping_tax.append(retro_charge.get('ShippingTax', {}))
            else:
                shipping_tax = retro_charge.get('ShippingTax', {})

            for tax in base_tax:
                price += float(tax.get('Amount', {}).get('value', 0.0))
            for tax in shipping_tax:
                price += float(tax.get('Amount', {}).get('value', 0.0))
            if price == 0.0:
                continue
            date_posted = retro_charge.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            bank_line_vals = {
                'name': amazon_code + '-' + order_ref,
                'ref': settlement_id,
                'partner_id': amazon_order and amazon_order.partner_id and amazon_order.partner_id.id,
                'amount': price,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'amazon_code': amazon_code,
            }
            bank_statement_line_obj.create(bank_line_vals)
        return True

    """Main method of process settlement report file"""

    @api.multi
    def process_settlement_report_file(self):
        self.ensure_one()
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

        bank_statement_obj = self.env['account.bank.statement']
        imp_file = StringIO(base64.decodestring(self.attachment_id.datas).decode())
        content = imp_file.read()
        # needs to change for DictWrapper
        response = DictWrapper(content, "Message")
        result = response.parsed
        settlement_reports = []
        journal = self.instance_id.settlement_report_journal_id
        if not isinstance(result.get('SettlementReport', []), list):
            settlement_reports.append(result.get('SettlementReport', []))
        else:
            settlement_reports = result.get('SettlementReport', [])

        seller = self.seller_id
        ctx = self._context and self._context.copy() or {}
        ctx.update({'journal_type': 'bank'})
        bank_statement = False

        for report in settlement_reports:
            settlement_data = report.get('SettlementData', {})
            settlement_id = settlement_data.get('AmazonSettlementID', {}).get('value', '')
            total_amount = settlement_data.get('TotalAmount', {}).get('value', '')
            start_date = settlement_data.get('StartDate', {}).get('value', '')
            deposit_date = settlement_data.get('DepositDate', {}).get('value')
            end_date = settlement_data.get('EndDate', {}).get('value', '')
            start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S+00:00").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S+00:00").date()

            bank_statement_exist = bank_statement_obj.search(
                [('settlement_ref', '=', settlement_id)])
            if bank_statement_exist:
                settlement_exist = self.search([('statement_id', '=', bank_statement_exist.id)])
                if settlement_exist:
                    self.write({'already_processed_report_id': settlement_exist.id,
                                'is_already_processed': True, 'state': 'processed'})
                else:
                    self.write({'statement_id': bank_statement_exist.id, 'state': 'processed'})
                continue

            name = '%s %s to %s ' % (self.instance_id.marketplace_id.name, start_date, end_date)
            vals = {
                'settlement_ref': settlement_id,
                'journal_id': journal.id,
                'date': end_date,
                'name': name,
                'balance_end_real': total_amount,
            }
            if self.instance_id.ending_balance_account_id:
                vals.update({'balance_end_real': 0.0})
            bank_statement = bank_statement_obj.create(vals)
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

            orders = []
            refunds = []
            other_transactions = []
            advertising_transactions = []
            guarantee_claim = []
            charge_back = []
            retrocharge = []
            retrochargereversal = []
            if not isinstance(report.get('Order', {}), list):
                orders.append(report.get('Order', {}))
            else:
                orders = report.get('Order', [])

            if not isinstance(report.get('GuaranteeClaim', []), list):
                guarantee_claim.append(report.get('GuaranteeClaim', {}))
            else:
                guarantee_claim = report.get('GuaranteeClaim', [])

            if not isinstance(report.get('Retrocharge'), list):
                retrocharge.append(report.get('Retrocharge', {}))
            else:
                retrocharge = report.get('Retrocharge')

            if not isinstance(report.get('RetrochargeReversal'), list):
                retrochargereversal.append(report.get('RetrochargeReversal', {}))
            else:
                retrochargereversal = report.get('RetrochargeReversal')

            if not isinstance(report.get('Chargeback', []), list):
                charge_back.append(report.get('Chargeback', {}))
            else:
                charge_back = report.get('Chargeback', [])

            if not isinstance(report.get('Refund', {}), list):
                refunds.append(report.get('Refund', {}))
            else:
                refunds = report.get('Refund', [])

            if not isinstance(report.get('OtherTransaction', {}), list):
                other_transactions.append(report.get('OtherTransaction', {}))
            else:
                other_transactions = report.get('OtherTransaction', [])

            if not isinstance(report.get('AdvertisingTransactionDetails', {}), list):
                advertising_transactions.append(report.get('AdvertisingTransactionDetails', {}))
            else:
                advertising_transactions = report.get('AdvertisingTransactionDetails', [])

            """Process Advertising Transactions"""
            advertising_transactions and self.make_amazon_advertising_transactions(seller,
                                                                                   bank_statement,
                                                                                   advertising_transactions)
            """Process of make order transactions"""
            other_transactions and self.make_amazon_other_transactions(seller, bank_statement,
                                                                       other_transactions)

            """Update A-Z Guarantee claim"""
            guarantee_claim and self.make_amazon_guarantee_claim(seller, bank_statement,
                                                                 guarantee_claim, settlement_id)

            """ Update Charge back"""
            charge_back and self.make_amazon_charge_back(seller, bank_statement, charge_back,
                                                         settlement_id)

            """ Update Retrocharge """
            retrocharge and self.create_retro_charge(seller, bank_statement, retrocharge,
                                                     settlement_id)

            """Update Retrocharge Reversal"""
            amazon_code = 'RetrochargeReversal'
            retrochargereversal and self.create_retro_charge(seller, bank_statement,
                                                             retrochargereversal, settlement_id,
                                                             amazon_code)

            """Process of orders"""
            orders and self.process_settlement_orders(seller, bank_statement, settlement_id,
                                                      orders) or {}

            """Process of refunds
                Picking Moves : dict of move which have returned but 2binvoiced
                Picking Products : dict of picking products which have returned but 2binvoiced
                refund invoice dict:dict of refund invoice which not returned & not refunded in ERP system
                refund_stement_line_picking_dict: dict of pickings which have refunds
                refund_stement_line_order_dict :dict of orders which have refunds            
            """
            refund_invoice_dict = self.process_settlement_refunds(seller, bank_statement,
                                                                  settlement_id, refunds)

            """ Create manually refund in ERP whose returned not found in the system"""
            if refund_invoice_dict:
                self.create_refund_invoices(refund_invoice_dict, bank_statement)
        vals = {}
        if bank_statement:
            vals = {'statement_id': bank_statement.id, 'state': 'imported'}
            self.write(vals)
        return True

    @api.model
    def convert_move_amount_currency(self, bank_statement, moveline, amount):
        amount_currency = 0.0
        if moveline.company_id.currency_id.id != bank_statement.currency_id.id:
            # In the specific case where the company currency and the statement currency are the same
            # the debit/credit field already contains the amount in the right currency.
            # We therefore avoid to re-convert the amount in the currency, to prevent Gain/loss exchanges
            amount_currency = moveline.currency_id.compute(moveline.amount_currency,
                                                           bank_statement.currency_id)
        elif (
                moveline.invoice_id and moveline.invoice_id.currency_id.id != bank_statement.currency_id.id):
            amount_currency = moveline.invoice_id.currency_id.compute(amount,
                                                                      bank_statement.currency_id)
        currency = moveline.currency_id.id
        return currency, amount_currency

    @api.model
    def process_settlement_refunds(self, seller, bank_statement, settlement_id, refunds):
        sale_order_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        partner_obj = self.env['res.partner']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        amazon_order_fee_obj = self.env['amazon.sale.order.fee.ept']
        refund_invoice_dict = defaultdict(dict)
        refund_stement_line_order_dict = {}

        for refund in refunds:
            if not refund:
                continue

            order_ref = refund.get('AmazonOrderID', {}).get('value', '')
            fulfillment = refund.get('Fulfillment', {})
            item = fulfillment.get('AdjustedItem', {})
            date_posted = fulfillment.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            items = []
            amzon_orders = sale_order_obj.search(
                [('amazon_reference', '=', order_ref), ('state', '!=', 'cancel')], order="id")
            partner = False
            if amzon_orders:
                partner = partner_obj._find_accounting_partner(amzon_orders[0].partner_id)

            if not isinstance(item, list):
                items.append(item)
            else:
                items = item
            refund_total_amount = 0.0
            orders = sale_order_obj.browse()
            fees_type_dict = {}
            amazon_refund_fees_dict = {}
            for item in items:
                order_item_code = item.get('AmazonOrderItemCode', {}).get('value', '')
                merchant_adjustment_item_id = item.get('MerchantAdjustmentItemID', {}).get('value',
                                                                                           '')
                order_line = sale_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                   ('amazon_order_item_id', '=', order_item_code),
                                                   ('amz_merchant_adjustment_item_id', '=',
                                                    merchant_adjustment_item_id)
                                                   ])
                if not order_line:
                    order_line = sale_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                       ('amazon_order_item_id', '=',
                                                        order_item_code),
                                                       ('amz_merchant_adjustment_item_id', '=',
                                                        False)
                                                       ])
                if not order_line:
                    order_line = sale_line_obj.search([('order_id', 'in', amzon_orders.ids),
                                                       ('amazon_order_item_id', '=',
                                                        order_item_code),
                                                       ])
                if order_line:
                    order_line = order_line[0]
                    amz_order = order_line.order_id

                item_fees = item.get('ItemFeeAdjustments', {})
                fees = item_fees.get('Fee', [])
                fees_list = []
                if not isinstance(fees, list):
                    fees_list.append(fees)
                else:
                    fees_list = fees

                for fee in fees_list:
                    fee_type = fee.get('Type').get('value')
                    fee_amount = float(fee.get('Amount', {}).get('value', 0.0))
                    if fee_type in fees_type_dict:
                        fees_type_dict[fee_type] = fees_type_dict[fee_type] + fee_amount
                    else:
                        fees_type_dict.update({fee_type: fee_amount})
                amazon_refund_fees_dict.update({order_item_code: [fees_type_dict]})
                item_price = item.get('ItemPriceAdjustments', {})
                component = item_price.get('Component', {})
                components = []
                if not isinstance(component, list):
                    components.append(component)
                else:
                    components = component
                product_total_amount = 0.0
                for component in components:
                    ttype = component.get('Type', {}).get('value', '')
                    if ttype and ttype.__contains__('MarketplaceFacilitator'):
                        fees_type_dict.update(
                            {ttype: float(component.get('Amount', {}).get('value', 0.0))})
                    else:
                        amount_refund = float(component.get('Amount', {}).get('value', 0.0))
                        product_total_amount += -amount_refund
                        refund_total_amount += amount_refund
                promotion_adjustment = item.get('PromotionAdjustment', {})
                promotions = []
                if promotion_adjustment and not isinstance(promotion_adjustment, list):
                    promotions.append(promotion_adjustment)
                else:
                    promotions = promotion_adjustment

                for promotion in promotions:
                    product_total_amount += - float(promotion.get('Amount', {}).get('value', 0.0))
                    refund_total_amount += float(promotion.get('Amount', {}).get('value', 0.0))
                if order_line:
                    if amz_order in refund_invoice_dict:
                        product_total_amount += refund_invoice_dict.get(amz_order, {}).get(
                            order_line.product_id.id, 0.0)
                        refund_invoice_dict.get(amz_order).update(
                            {order_line.product_id.id: product_total_amount})
                    else:
                        refund_invoice_dict[amz_order].update(
                            {order_line.product_id.id: product_total_amount})
                    if 'date_posted' not in refund_invoice_dict.get(amz_order, {}):
                        refund_invoice_dict.get(amz_order).update({'date_posted': date_posted})
                    if amz_order not in orders:
                        orders += amz_order
                if order_line:
                    # For Performance Reason, we have update order line by executing query.
                    self._cr.execute(
                        "update sale_order_line set amz_merchant_adjustment_item_id=%s where id=%s" % (
                            merchant_adjustment_item_id, str(order_line.id)))

            if not refund_total_amount:
                continue
            bank_line_vals = {
                'name': 'Refund_' + order_ref,
                'ref': settlement_id,
                'partner_id': partner and partner.id,
                'amount': refund_total_amount,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'is_refund_line': True,
            }

            statement_line = bank_statement_line_obj.create(bank_line_vals)
            if orders:
                if orders in refund_stement_line_order_dict:
                    statement_line += refund_stement_line_order_dict.get(orders)
                refund_stement_line_order_dict.update({orders: statement_line})
                order_ids = []
                for line in statement_line:
                    order_ids += line.amazon_order_ids.ids + orders.ids
                statement_line.write({'amazon_order_ids': [(6, 0, list(set(order_ids)))]})
                for amazon_order_item_code, fees in amazon_refund_fees_dict.items():
                    for fee in fees:
                        amazon_order_lines = sale_line_obj.search(
                            [('amazon_order_item_id', '=', amazon_order_item_code),
                             ('order_id', 'in', orders.ids)])
                        for amazon_order_line in amazon_order_lines:
                            for fee_type, amount in fee.items():
                                vals = {'fee_type': fee_type,
                                        'amount': amount,
                                        'amazon_sale_order_line_id': amazon_order_line.id,
                                        'is_refund': True
                                        }
                                amazon_order_fee_obj.create(vals)
            self.make_amazon_fee_entry(seller, bank_statement, date_posted, fees_type_dict,
                                       order_ref)
        return refund_invoice_dict

    @api.multi
    def filter_orders_based_on_payment(self, amz_orders, order_dict):
        fulfillment = order_dict.get('Fulfillment', {})
        item = fulfillment.get('Item', {})
        items = []
        if not isinstance(item, list):
            items.append(item)
        else:
            items = item
        order_total_amount = 0.0
        amazon_fees_dict = {}
        fees_type_dict = {}
        for item in items:
            item_price = item.get('ItemPrice', {})
            amazon_order_item_code = item.get('AmazonOrderItemCode').get('value')
            item_fees = item.get('ItemFees', {})
            fees = item_fees.get('Fee', [])
            fees_list = []
            if not isinstance(fees, list):
                fees_list.append(fees)
            else:
                fees_list = fees
            for fee in fees_list:
                fee_type = fee.get('Type').get('value')
                fee_amount = float(fee.get('Amount', {}).get('value', 0.0))
                if fee_type in fees_type_dict:
                    fees_type_dict[fee_type] = fees_type_dict[fee_type] + fee_amount
                else:
                    fees_type_dict.update({fee_type: fee_amount})
            amazon_fees_dict.update({amazon_order_item_code: [fees_type_dict]})

            component = item_price.get('Component', {})
            components = []
            if not isinstance(component, list):
                components.append(component)
            else:
                components = component
            for component in components:
                ttype = component.get('Type', {}).get('value', '')
                if ttype and ttype.__contains__('MarketplaceFacilitator'):
                    fees_type_dict.update(
                        {ttype: float(component.get('Amount', {}).get('value', 0.0))})
                else:
                    order_total_amount += float(component.get('Amount', {}).get('value', 0.0))
            promotion_list = item.get('Promotion', {})
            if not isinstance(promotion_list, list):
                promotion_list = [promotion_list]
            promotion_amount = 0
            for promotion in promotion_list:
                promotion_amount = promotion_amount + float(
                    promotion.get('Amount', {}).get('value', 0.0))
            order_total_amount = order_total_amount + promotion_amount
        amazon_order_sub_total = 0.0
        for amazon_order in amz_orders:
            if amazon_order.amount_total == order_total_amount:
                return amazon_order, order_total_amount, fees_type_dict, amazon_fees_dict
            amazon_order_sub_total += amazon_order.amount_total
        if amazon_order_sub_total == order_total_amount:
            return amz_orders, order_total_amount, fees_type_dict, amazon_fees_dict
        return amz_orders, order_total_amount, fees_type_dict, amazon_fees_dict

    @api.model
    def process_settlement_orders(self, seller, bank_statement, settlement_id, orders):
        sale_order_obj = self.env['sale.order']
        partner_obj = self.env['res.partner']
        product_product_obj = self.env['product.product']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        sale_line_obj = self.env['sale.order.line']
        amazon_order_fee_obj = self.env['amazon.sale.order.fee.ept']
        for order in orders:
            if not order:
                continue
            order_ref = order.get('AmazonOrderID', {}).get('value', '')
            fulfillment = order.get('Fulfillment', {})
            shipment_fees = order.get('ShipmentFees', [])
            if not isinstance(shipment_fees, list):
                shipment_fees = [shipment_fees]
            date_posted = fulfillment.get('PostedDate', {}).get('value', time.strftime('%Y-%m-%d'))
            amz_orders = sale_order_obj.search([('amazon_reference', '=', order_ref)],
                                               order="id desc")
            amz_orders, order_total_amount, fees_type_dict, amazon_fees_dict = self.filter_orders_based_on_payment(
                amz_orders, order)
            partner = False
            for shipment_fee in shipment_fees:
                fees = shipment_fee.get('Fee')
                if not isinstance(fees, list):
                    fees = [fees]
                for fee in fees:
                    fee_value = float(fee.get('Amount', {}).get('value', 0.0))
                    self.make_amazon_fee_entry(seller, bank_statement, date_posted,
                                               {fee.get('Type', {}).get('value'): fee_value},
                                               order_ref)
            if amz_orders:
                partner = partner_obj._find_accounting_partner(amz_orders[0].partner_id)
            if order_total_amount > 0.0:
                bank_line_vals = {
                    'name': order_ref,
                    'ref': settlement_id,
                    'partner_id': partner and partner.id,
                    'amount': order_total_amount,
                    'statement_id': bank_statement.id,
                    'date': date_posted,
                    'amazon_order_ids': [(6, 0, amz_orders.ids)]
                }

                bank_statement_line_obj.create(bank_line_vals)
            if amz_orders:
                for amazon_order_item_code, fees in amazon_fees_dict.items():
                    for fee in fees:
                        products = product_product_obj.search(
                            [('type', 'in', ['service', 'consu'])])
                        amazon_order_lines = sale_line_obj.search(
                            [('product_id', 'not in', products.ids),
                             ('amazon_order_item_id', '=', amazon_order_item_code),
                             ('order_id', 'in', amz_orders.ids)])
                        for amazon_order_line in amazon_order_lines:
                            for fee_type, amount in fee.items():
                                vals = {'fee_type': fee_type,
                                        'amount': amount,
                                        'amazon_sale_order_line_id': amazon_order_line.id}
                                amazon_order_fee_obj.create(vals)
                self.check_or_create_invoice_if_not_exist(amz_orders)
            self.make_amazon_fee_entry(seller, bank_statement, date_posted, fees_type_dict,
                                       order_ref)
        return True

    @api.model
    def make_amazon_fee_entry(self, seller, bank_statement, date_posted, fees_type_dict,
                              order_ref='', rei_name=False):
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for fee_type, amount in fees_type_dict.items():
            if amount == 0.0:
                continue
            if rei_name:
                name = rei_name
            else:
                name = order_ref and "%s-%s" % (order_ref, fee_type) or fee_type
            bank_line_vals = {
                'name': name,
                'ref': bank_statement.settlement_ref,
                'amount': amount,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'amazon_code': fee_type
            }
            bank_statement_line_obj.create(bank_line_vals)
        return True

    @api.model
    def check_or_create_invoice_if_not_exist(self, amz_orders):
        stock_immediate_transfer_obj = self.env['stock.immediate.transfer']
        for order in amz_orders:
            """Changes by Dhruvi
                default_fba_partner_id is fetched according to seller wise."""
            if order.amz_instance_id.seller_id.def_fba_partner_id.id == order.partner_id.id:
                continue
            if order.state == 'draft':
                order.action_confirm()

            for picking in order.picking_ids:
                if picking.state in ['confirmed', 'partially_available', 'assigned']:
                    picking.action_confirm()
                    picking.action_assign()
                    stock_immediate_transfer_obj.create({'pick_ids': [(4, picking.id)]}).process()

            if not order.invoice_ids:
                order.action_invoice_create()
            for invoice in order.invoice_ids:
                if invoice.state == 'draft' and invoice.type == 'out_invoice':
                    invoice.action_invoice_open()
        return True

    @api.multi
    def make_amazon_reimbursement_line_entry(self, bank_statement, date_posted,
                                             fees_type_dict, order_ref=''):
        bank_statement_line_obj = self.env['account.bank.statement.line']
        for fee_type, amount in fees_type_dict.items():
            bank_line_vals = {
                'name': order_ref and order_ref + '_' + fee_type or fee_type,
                'ref': bank_statement.settlement_ref,
                'amount': amount,
                'statement_id': bank_statement.id,
                'date': date_posted,
                'amazon_code': fee_type
            }
            statement_line = bank_statement_line_obj.create(bank_line_vals)
        return statement_line

    @api.multi
    def reconcile_reimbursement_invoice(self, reimbursement_invoices, reimbursement_line,
                                        bank_statement):
        move_line_obj = self.env['account.move.line']
        for reimbursement_invoice in reimbursement_invoices:
            if reimbursement_invoice.state == 'draft':
                reimbursement_invoice.compute_taxes()
                reimbursement_invoice.action_invoice_open()
        account_move_ids = list(map(lambda x: x.move_id.id, reimbursement_invoices))
        move_lines = move_line_obj.search([('move_id', 'in', account_move_ids),
                                           ('user_type_id.type', '=', 'receivable'),
                                           ('reconciled', '=', False)])
        mv_line_dicts = []
        move_line_total_amount = 0.0
        currency_ids = []
        for moveline in move_lines:
            amount = moveline.debit - moveline.credit
            amount_currency = 0.0
            if moveline.amount_currency:
                currency, amount_currency = self.convert_move_amount_currency(bank_statement,
                                                                              moveline, amount)
                if currency:
                    currency_ids.append(currency)

            if amount_currency:
                amount = amount_currency
            mv_line_dicts.append({
                'credit': abs(amount) if amount > 0.0 else 0.0,
                'name': moveline.invoice_id.number,
                'move_line': moveline,
                'debit': abs(amount) if amount < 0.0 else 0.0
            })
            move_line_total_amount += amount
        if round(reimbursement_line.amount, 10) == round(move_line_total_amount, 10) and (
                not reimbursement_line.currency_id or reimbursement_line.currency_id.id == bank_statement.currency_id.id):
            if currency_ids:
                currency_ids = list(set(currency_ids))
                if len(currency_ids) == 1:
                    reimbursement_line.write(
                        {'amount_currency': move_line_total_amount, 'currency_id': currency_ids[0]})
            reimbursement_line.process_reconciliation(mv_line_dicts)
        return True

    @api.model
    def check_amazon_mws_refund_exist_or_not(self, order):
        refund = self.env['amazon.order.refund.ept'].search(
            [('order_id', '=', order.id), ('state', '=', 'validate')])
        return refund and {order: refund.invoice_id} or {}

    @api.model
    def create_refund_invoices(self, refund_invoice_dict, bank_statement):
        obj_invoice_line = self.env['account.invoice.line']
        bank_statement_line_obj = self.env['account.bank.statement.line']
        obj_invoice = self.env['account.invoice']
        picking_obj = self.env['stock.picking']
        order_invoices_dict = {}
        for order, product_amount in refund_invoice_dict.items():
            date_posted = product_amount.get('date_posted')
            if 'date_posted' in product_amount:
                del product_amount['date_posted']
            if order.amz_fulfillment_by == 'MFN':
                mws_refund = self.check_amazon_mws_refund_exist_or_not(order)
                refund = mws_refund and mws_refund.get(order)
                mws_refund and order_invoices_dict.update(mws_refund)
                if refund:
                    lines = bank_statement_line_obj.search([('amazon_order_ids', 'in', order.ids), (
                        'statement_id', '=', bank_statement.id), ('is_refund_line', '=', True)])
                    for line in lines:
                        line and line.write({'refund_invoice_ids': [
                            (6, 0, line.refund_invoice_ids.ids + refund.ids)]})
                continue
            product_ids = list(product_amount.keys())
            if order.state in ['draft', 'sent']:
                self.check_or_create_invoice_if_not_exist([order])
            invoices = obj_invoice.search(
                [('id', 'in', order.invoice_ids.ids), ('type', '=', 'out_invoice'),
                 ('invoice_line_ids.product_id', 'in', product_ids)], limit=1)
            if not invoices:
                if order.invoice_policy and order.invoice_policy == 'delivery':
                    pickings = picking_obj.search([('id', 'in', order.picking_ids.ids),
                                                   ('move_lines.product_id', 'in', product_ids),
                                                   ('picking_type_id.code', '=', 'outgoing')],
                                                  limit=1)
                    invoices = obj_invoice.browse()
                    for picking in pickings:
                        if picking.state != 'done':
                            continue
                        invoice_ids = picking.sale_id.action_invoice_create()
                        for invoice in obj_invoice.browse(invoice_ids):
                            invoice.action_invoice_open()
                            invoices += invoice
                else:
                    invoice_ids = order.action_invoice_create()
                    for invoice in obj_invoice.browse(invoice_ids):
                        invoice.action_invoice_open()
                        invoices += invoice
            if not invoices:
                continue
            invoice_browse = obj_invoice.browse()
            for invoice in invoices:
                journal_id = invoice.journal_id.id
                refund_invoice = invoice.refund(date_posted, date_posted, invoice.name, journal_id)

                refund_invoice.write({'date_invoice': date_posted, 'origin': order.name})
                extra_invoice_lines = obj_invoice_line.search(
                    [('invoice_id', '=', refund_invoice.id), ('product_id', 'not in', product_ids)])
                if extra_invoice_lines:
                    extra_invoice_lines.unlink()
                for product_id, amount in product_amount.items():
                    invoice_lines = obj_invoice_line.search(
                        [('invoice_id', '=', refund_invoice.id), ('product_id', '=', product_id)])
                    exact_line = False
                    if len(invoice_lines.ids) > 1:
                        exact_line = obj_invoice_line.search(
                            [('invoice_id', '=', refund_invoice.id),
                             ('product_id', '=', product_id)], limit=1)
                        if exact_line:
                            other_lines = obj_invoice_line.search(
                                [('invoice_id', '=', refund_invoice.id),
                                 ('product_id', '=', product_id), ('id', '!=', exact_line.id)])
                            other_lines.unlink()
                            exact_line.write({'quantity': 1, 'price_unit': amount})
                    else:
                        invoice_lines.write({'quantity': 1, 'price_unit': amount})
                refund_invoice.compute_taxes()
                refund_invoice.action_invoice_open()
                invoice_browse = invoice_browse + refund_invoice
            order_invoices_dict.update({order: invoice_browse})
            lines = bank_statement_line_obj.search(
                [('amazon_order_ids', 'in', order.ids), ('statement_id', '=', bank_statement.id),
                 ('is_refund_line', '=', True)])
            for line in lines:
                line and line.write({'refund_invoice_ids': [
                    (6, 0, line.refund_invoice_ids.ids + invoice_browse.ids)]})
        return order_invoices_dict

    @api.multi
    def view_bank_statement(self):
        self.ensure_one()
        action = self.env.ref('account.action_bank_statement_tree', False)
        form_view = self.env.ref('account.view_bank_statement_form', False)
        result = action and action.read()[0] or {}
        result['views'] = [(form_view and form_view.id or False, 'form')]
        result['res_id'] = self.statement_id and self.statement_id.id or False
        return result

    @api.multi
    def configure_statement_missing_fees(self):
        """
        This method return the cancel order in amazon wizard.
        :return: Cancel Order Wizard
        """
        view = self.env.ref('amazon_ept.view_configure_settlement_report_fees_ept')
        context = dict(self._context)
        context.update({'settlement_id': self.id, 'seller_id': self.seller_id.id})

        return {
            'name': _('Settlement Report Missing Configure Fees'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'settlement.report.configure.fees.ept',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }