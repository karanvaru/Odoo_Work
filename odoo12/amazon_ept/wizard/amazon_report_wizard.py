import xml.etree.ElementTree as ET
import dateutil.parser
import base64
from datetime import datetime, timedelta
from odoo import models, fields, api, _
import time
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_report_wizard(models.TransientModel):
    _name = "amazon.report.wizard"
    _description = 'amazon.report.wizard'

    seller_id = fields.Many2one("amazon.seller.ept", "Seller")
    #_GET_V2_SETTLEMENT_REPORT_DATA_XML_
    #_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_
    report_type = fields.Char(size=256, string='Report Type',
                              default='_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    create_record_from_file = fields.Boolean("Create Report From File", default=False)
    import_file = fields.Binary("Choose File")
    file_name = fields.Char("File Name")

    @api.model
    def default_get(self, fields):
        res = super(amazon_report_wizard, self).default_get(fields)
        if 'default_instance_id' in self._context:
            instance_id = self._context.get('default_instance_id')
            if instance_id:
                instance = self.env['amazon.instance.ept'].browse(instance_id)
                res.update({'seller_id': instance.seller_id.id})
        return res

    @api.onchange('seller_id')
    def on_change_seller_id(self):
        value = {}
        if self.seller_id:
            value.update({'start_date': self.seller_id.settlement_report_last_sync_on,
                          'end_date': datetime.now()})
        return {'value': value}

    @api.multi
    def _check_duration(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date must be precede its end date.',
         ['start_date', 'end_date'])
    ]

    @api.multi
    def get_reports(self):
        self.ensure_one()
        seller = self.seller_id
        odoo_report_ids = []
        settlement_obj = self.env['settlement.report.ept']
        bank_statement_obj = self.env['account.bank.statement']
        if not seller:
            raise Warning('Please select seller')

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        log_book_obj = self.env['amazon.process.log.book']
        transaction_log_obj = self.env['amazon.transaction.log']
        model_id = transaction_log_obj.get_model_id('settlement.report.ept')
        log_rec = False

        if self.create_record_from_file != True:
            start_date = self.start_date
            end_date = self.end_date
            if start_date:
                db_import_time = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
                db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
                start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                    time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
                start_date = str(start_date) + 'Z'
            else:
                today = datetime.now()
                earlier = today - timedelta(days=30)
                earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
                start_date = earlier_str + 'Z'
            if end_date:
                db_import_time = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
                db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
                end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                    time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
                end_date = str(end_date) + 'Z'
            else:
                today = datetime.now()
                earlier_str = today.strftime("%Y-%m-%dT%H:%M:%S")
                end_date = earlier_str + 'Z'

            kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                      'auth_token': seller.auth_token and str(seller.auth_token) or False,
                      'app_name': 'amazon_ept',
                      'account_token': account.account_token,
                      'emipro_api': 'get_reports',
                      'dbuuid': dbuuid,
                      'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                 seller.country_id.code,
                      'report_type': self.report_type,
                      'start_date': start_date,
                      'end_date': end_date, }

            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                if self._context.get('is_auto_process'):
                    log_vals = {
                        'message': 'Settlement Report Process',
                        'application': 'account',
                        'operation_type': 'import',
                    }
                    log_rec = log_book_obj.create(log_vals)

                    transaction_vals = {'model_id': model_id,
                                        'log_type': 'error',
                                        'action_type': 'terminate_process_with_log',
                                        'message': response.get('reason'),
                                        'job_id': log_rec.id, }
                    transaction_log_obj.create(transaction_vals)
                else:
                    return Warning(response.get('reason'))

            else:
                list_of_wrapper = response.get('result')

            settlement_obj = self.env['settlement.report.ept']
            odoo_report_ids = []
            for result in list_of_wrapper:
                reports = []
                if not isinstance(result.get('ReportInfo', []), list):
                    reports.append(result.get('ReportInfo', []))
                else:
                    reports = result.get('ReportInfo', [])
                for report in reports:
                    request_id = report.get('ReportRequestId', {}).get('value', '')
                    report_id = report.get('ReportId', {}).get('value', '')
                    report_type = report.get('ReportType', {}).get('value', '')
                    report_exist = settlement_obj.search(
                        ['|', ('report_request_id', '=', request_id), ('report_id', '=', report_id),
                         ('report_type', '=', report_type)])
                    if report_exist:
                        report_exist = report_exist[0]
                        odoo_report_ids.append(report_exist.id)
                        continue
                    try:
                        sequence = self.env.ref('amazon_ept.seq_import_settlement_report_job')
                        if sequence:
                            report_name = sequence.next_by_id()
                        else:
                            report_name = '/'
                    except:
                        report_name = '/'

                    vals = {
                        'name': report_name,
                        'report_type': report_type,
                        'report_request_id': request_id,
                        'report_id': report_id,
                        'start_date': start_date,
                        'end_date': end_date,
                        'state': '_DONE_',
                        'seller_id': seller.id,
                        'user_id': self._uid,
                    }
                    report_rec = settlement_obj.create(vals)
                    report_rec.get_report()
                    self._cr.commit()
                    odoo_report_ids.append(report_rec.id)

        else:
            if self.import_file:
                if self.file_name and self.file_name[-3:] != 'xml':
                    raise Warning("Please Provide Only xml file !!!")
                file_data = base64.b64decode(self.import_file.decode("utf-8"))
                root = ET.fromstring(file_data)
                message = root.findall("Message")
                order = message[0][1].findall("Order")
                refund = message[0][1].findall("Refund")
                settlement_data = message[0][1][0]

                settlement_id = settlement_data.find("AmazonSettlementID").text

                bank_statement_exist = bank_statement_obj.search(
                    [('settlement_ref', '=', settlement_id)])
                if bank_statement_exist:
                    settlement_exist = settlement_obj.search(
                        [('statement_id', '=', bank_statement_exist.id)])
                    if settlement_exist:
                        raise Warning("File Already Processed!!!")

                currency = settlement_data.find("TotalAmount").attrib.get('currency', '')
                start_date = settlement_data.find("StartDate").text
                end_date = settlement_data.find("EndDate").text

                start_date = dateutil.parser.parse(start_date)
                end_date = dateutil.parser.parse(end_date)

                currency_rec = self.env['res.currency'].search([('name', '=', currency)])

                marketplace = order and order[0].find("MarketplaceName").text

                if not marketplace:
                    marketplace = refund and refund[0].find("MarketplaceName").text

                instance = self.env['amazon.marketplace.ept'].find_instance(seller, marketplace)

                datas = self.import_file

                file_name = "Settlement_report_" + time.strftime("%Y_%m_%d_%H%M%S") + '.xml'

                attachment = self.env['ir.attachment'].create({
                    'name': file_name,
                    'datas': datas,
                    'datas_fname': file_name,
                    'res_model': 'settlement.report.ept',
                })

                try:
                    sequence = self.env.ref('amazon_ept.seq_import_settlement_report_job')
                    if sequence:
                        report_name = sequence.next_by_id()
                    else:
                        report_name = '/'
                except:
                    report_name = '/'

                vals = {'name': report_name,
                        'report_type': '_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_',
                        'report_request_id': False,
                        'report_id': False,
                        'state': '_DONE_',
                        'seller_id': seller.id,
                        'user_id': self._uid,
                        'attachment_id': attachment.id,
                        'start_date': start_date and start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date and end_date.strftime('%Y-%m-%d'),
                        'currency_id': currency_rec and currency_rec[0].id or False,
                        'instance_id': instance and instance[0].id or False,
                        'seller_id': seller and seller.id or False,
                        'company_id': seller.company_id and seller.company_id.id or False
                        }

                report = settlement_obj.create(vals)

                odoo_report_ids.append(report.id)

                report.message_post(body=_("<b>Settlement Report Downloaded</b>"),
                                    attachment_ids=attachment.ids)

        return odoo_report_ids

    @api.multi
    def get_report_list(self):
        odoo_report_ids = self.get_reports()
        if odoo_report_ids:
            action = self.env.ref('amazon_ept.action_amazon_settlement_report_ept', False)
            result = action and action.read()[0] or {}

            if len(odoo_report_ids) > 1:
                result['domain'] = "[('id','in',[" + ','.join(map(str, odoo_report_ids)) + "])]"
            else:
                res = self.env.ref('amazon_ept.amazon_settlement_report_form_view_ept', False)
                result['views'] = [(res and res.id or False, 'form')]
                result['res_id'] = odoo_report_ids and odoo_report_ids[0] or False
            return result

        return True
