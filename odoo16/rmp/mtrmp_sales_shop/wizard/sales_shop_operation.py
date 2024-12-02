from odoo import models, fields, api, _
import base64
import xlrd
from io import StringIO, BytesIO
import requests
import io
import csv
import logging
import json
import threading
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools.misc import xlwt

_logger = logging.getLogger(__name__)

class AttachmentUpdateWizard(models.TransientModel):
    _name = "sales.shop.operation"
    _description = "Sales Shop Operation for Import/Export process"

    operation = fields.Selection([
        ('import_products', 'Import Products'),
        ('import_sales_order', 'Import Sales Order'), ('import_AWB', 'Import AWB'), ('import_return', 'Import Return'),
        ('import_payment_settlement', 'Import Payment settlement')],
            string='Operation',
            default='import_products')

    file_name = fields.Binary(string="File Name")
    filename = fields.Char(string="File name", readonly=False)
    failed_count = fields.Integer(string="Fail Count")
    success_count = fields.Integer(string="Success Count")
    failed_order = fields.Text(string="Fail Order")
    user_id = fields.Many2one('res.users', string="Upload By User")
    upload_date = fields.Datetime(string="Upload Date")
    shop_id = fields.Many2one('sale.shop', string="Shop")
    product_public_category_id = fields.Many2one('product.public.category', string="Channel Category")
    need_stock_qty = fields.Boolean(string="with Stock Qty", default=True)
    qty_type = fields.Selection([('on_hand', 'On Hand'), ('forcasted', 'Forcasted')], string='Qty Type')
    warehouse_type = fields.Selection([('all_warehouse', 'All Warehouse'), ('shop_warehouse', 'Shop Warehouse')],
                                      string='Warehouse')

    header_position = fields.Integer('Header Position', default=1)

    def download_sample(self):
        self.ensure_one()
        lines_id = False
        if self.operation == 'import_products':
            lines_id = self.env['attachment.sample.file'].search([
                ('shop_id', '=', self.shop_id.id),
                ('file_type', '=', 'product')
            ], limit=1)
        elif self.operation == 'import_sales_order':
            lines_id = self.env['attachment.sample.file'].search([
                ('shop_id', '=', self.shop_id.id),
                ('file_type', '=', 'sale_order')
            ], limit=1)
        elif self.operation == 'import_AWB':
            lines_id = self.env['attachment.sample.file'].search([
                ('shop_id', '=', self.shop_id.id),
                ('file_type', '=', 'awb')
            ], limit=1)
        if lines_id and lines_id.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=ir.attachment&id=" + str(
                        lines_id.attachment_id.id) + "&filename_field=name&field=datas&download=true&name=" + lines_id.attachment_id.name
            }

    def process_operation(self):
        res = None
        if self.operation == 'import_products':
            res = self.import_product()
        elif self.operation == 'export_products':
            res = self.export_product()
        elif self.operation == 'import_sales_order':
            res = self.import_sale_orders()
        elif self.operation == 'import_AWB':
            res = self.import_awb_numbers()
        elif self.operation == 'import_return':
            res = self.import_return_file()
        elif self.operation == 'import_payment_settlement':
            res = self.import_payment_settlement()
        return res

    def import_product(self):
        active_id = self._context.get('active_id', False)
        if self.filename:
            if not self.filename.endswith('.csv'):
                raise ValidationError(_('File must be in .csv format!'))
        shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_products',
                                                        'shop_id': self.shop_id.id})
        self.create_shop_file_attachment(self.file_name, res_model='shop.fail.log', log_book=shop_log_id,
                                         file_name='Product Import.csv')
        csv_data = False
        try:
            csv_data = base64.decodebytes(self.file_name)
            _logger.info("Upload File____________")
        except:
            pass
        if not csv_data:
            _logger.info("Not Upload File____________")
            template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
            if template_id:
                template = self.env['mail.template'].browse(template_id).id
                email_values = {
                    'message': 'Csv Reading Issue'
                }
                template.with_context(email_values).send_mail(self.id, force_send=True, email_values=email_values)

        reader = False
        try:
            import_file = BytesIO(base64.decodebytes(self.file_name))
            file_read = StringIO(import_file.read().decode())
            reader = csv.DictReader(file_read, delimiter=",")
            _logger.info("Read File____________")
        except:
            pass
        if not reader:
            _logger.info("Not Read File____________")
            template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
            if template_id:
                template = self.env['mail.template'].browse(template_id).id
                email_values = {
                    'message': 'Csv Reading Issue'
                }
                template.with_context(email_values).send_mail(self.id, force_send=True, email_values=email_values)
        # headers = []
        # try:
        #     for r in reader:
        #         headers = r
        #         break
        # except:
        #     template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
        #     if template_id:
        #         template = self.env['mail.template'].browse(template_id).id
        #         email_values = {
        #             'message': 'headers Reading Issue'
        #         }
        #         template.with_context(email_values).send_mail(self.id, force_send=True, email_values=None)
        #     return
        lines = []
        data = []
        for i in reader:
            data.append(i)
        headers = list(data[0].keys())
        for i in headers:
            res = self.env['ir.model.fields'].search(
                    [('model_id.model', '=', 'sale.shop.product'), ('field_description', '=', i)])
            vals = {'excel_head': i}
            if res:
                vals.update({'field_id': res.id})
            lines.append((0, 0, vals))
        wizard_id = self.env['excel.header.mapping.wizard'].create(
                {'lines_ids': lines, 'shop_id': self.shop_id.id})
        # print("self_id",self.id)
        return {
            'name': 'Upload Product',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'excel.header.mapping.wizard',
            'res_id': wizard_id.id,
            'target': 'new',
            'context': {'data': data, 'product_wizard_id': self.id,'log_id' :shop_log_id.id}
        }

    def export_product(self):
        filename = 'Export Product.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet1 = workbook.add_sheet('Exprot PRoduct Report')
        domain = [
            ('shop_id', '=', self.shop_id.id),
            ('product_public_category_id', '=', self.product_public_category_id.id)
        ]

        record_ids = self.env['sale.shop.product'].search(domain)
        formate_2 = xlwt.easyxf("font: bold 1, color black ;align: horiz center")

        row_index = 0
        sheet1.write(row_index, 0, "Base Product", formate_2)
        sheet1.write(row_index, 1, "Name", formate_2)
        sheet1.write(row_index, 2, "SKU", formate_2)
        sheet1.write(row_index, 3, "Sales Price", formate_2)
        sheet1.write(row_index, 4, "MRP", formate_2)
        sheet1.write(row_index, 5, "Unit of Measure", formate_2)
        sheet1.write(row_index, 6, "Inventory", formate_2)
        sheet1.write(row_index, 7, "HSN ID", formate_2)
        sheet1.write(row_index, 8, "Size", formate_2)
        sheet1.write(row_index, 9, "GST %", formate_2)
        sheet1.write(row_index, 10, "Color", formate_2)
        sheet1.write(row_index, 11, "Product weight (gms)", formate_2)
        sheet1.write(row_index, 12, "Country of Origin", formate_2)

        # print("records_ids", record_ids)
        for rec in record_ids:
            row_index += 1
            sheet1.write(row_index, 0, rec.product_id.name)
            sheet1.write(row_index, 1, rec.name)
            sheet1.write(row_index, 2, rec.default_code)
            sheet1.write(row_index, 3, rec.list_price)
            sheet1.write(row_index, 4, rec.product_id.standard_price)
            sheet1.write(row_index, 5, rec.uom_id.name)
            qty = 0
            if self.need_stock_qty:
                if self.qty_type == "on_hand":
                    if self.warehouse_type == "shop_warehouse":
                        qty = rec.product_id.with_context(warehouse=rec.shop_id.default_warehouse_id.id).qty_available
                    else:
                        qty = rec.product_id.qty_available
                if self.qty_type == "forcasted":
                    if self.warehouse_type == "shop_warehouse":
                        qty = rec.product_id.with_context(
                                warehouse=rec.shop_id.default_warehouse_id.id).virtual_available
                    else:
                        qty = rec.product_id.virtual_available
            sheet1.write(row_index, 6, qty)
            sheet1.write(row_index, 7, rec.product_id.l10n_in_hsn_code)
            sheet1.write(row_index, 8, rec.size)

            taxes_id = rec.product_id.taxes_id.mapped('name')
            tax = ','.join(taxes_id)
            sheet1.write(row_index, 9, tax)

            color_id = self.env['product.attribute'].search([('name', '=', 'Color')], limit=1)
            color_val = rec.product_id.product_template_variant_value_ids.filtered(
                    lambda line: line.attribute_id == color_id).product_attribute_value_id.name
            sheet1.write(row_index, 10, color_val or '')
            sheet1.write(row_index, 11, rec.product_id.weight)
            sheet1.write(row_index, 12, rec.country_id.name)

        fp = io.BytesIO()
        workbook.save(fp)
        report_id = self.env['excel.report'].create(
                {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {'view_mode': 'form',
                'res_id': report_id.id,
                'res_model': 'excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
                }

    def create_shop_file_attachment(self, filename, res_model=False, log_book=None,file_name=None):
        """
            Usage: Used for read the file and create attachment of that file or if any exception
            occurs then create a log.
            :param buffer: Buffer Object of CSV Data.
            :param file_name: name of the temp file
            :param resource_object: Resource Object, such as, sale.order(), product.product() etc.
            :param res_model: Resource Model, such as, sale.order, product.product
            :param log_book: common.log.book.ept()
            :return: ir.attachment()
            @type file_name: object
        """
        attachment = self.env['ir.attachment']
        try:
            if filename:
                values = {
                    'name': file_name,
                    'datas': self.file_name,
                    'type': 'binary',
                    'res_model': res_model,
                    'res_id': log_book.id if log_book else False
                }
                attachment = attachment.create(values)
                if attachment and log_book and hasattr(log_book, 'message_post'):
                    log_book.message_post(body=_(f"<b>File: {file_name}</b>"), attachment_ids=attachment.ids)
        except Exception as error:
            message = f"While creating the file attachment error occur, Error: [{error}]"
            _logger.info(message)
        return attachment

    def import_sale_orders(self):
        shop_id = self.shop_id
        file_format_id = self.shop_id.sale_file_format_id
        if not self.filename:
            raise ValidationError(_('Please select file to Process'))

        shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_sales_order',
                                                        'shop_id': self.shop_id.id})
        self.create_shop_file_attachment(self.file_name, res_model='shop.fail.log', log_book=shop_log_id,
                                         file_name='Sale Order Import.xlsx')
        if self.filename.endswith('.csv'):
            headers, file_data = self.read_csv_file()
        else:
            headers, file_data = self.read_xlsx_file(shop_log_id)
        order_main_dict = self.prepare_order_data(headers, file_data, file_format_id, shop_log_id)
        self.env['sale.order'].process_order_main_dict(shop_id, order_main_dict, shop_log_id)

    def prepare_order_data(self, headers, file_data, file_format, shop_log_id):
        """
        {'billing' : {'name': 'ABC','state' : 'Gujarat','Country' : 'IN', 'Zipcode' :380006 ,'Address1':'Rannsdi'}
        """
        order_main_dict = {}
        skip_order_list = []
        original_field_dict = {}
        if file_format.document_type:
            order_field_list = ['order reference', 'order_date', 'customer name', 'customer email', 'customer phone',
                                'shipping name', 'shipping email', 'shipping phone', 'shipping address',
                                'shipping state',
                                'shipping country', 'shipping zip', 'shipping city', 'billing name', 'billing email',
                                'billing phone', 'billing address', 'billing state', 'billing country', 'billing zip',
                                'billing city', 'product name', 'product_sku', 'price', 'quantity', 'tax rate',
                                'tax amount',
                                'discount ', 'shipping charge']
            for field in order_field_list:
                excel_field = file_format.column_ids.filtered(lambda l: l.sale_order_confirmation_fields == field).name
                if excel_field:
                    original_field_dict.update({field: excel_field})
        else:
            column_obj = self.env['document.column.wizard']
            domain = column_obj.get_domain()
            token = column_obj.get_token()
            route = column_obj.get_column_parser_route()
            data = {
                "token": token,
                "score_thersold": 50,
                "document_id": file_format.document_id,
                "tags": headers
            }
            endpoint = f'{domain}/{route}'
            query = f'{endpoint}'
            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", query, headers=headers, data=payload)

            response = response.json()
            if not response.get('data'):
                raise ValidationError("Can't able to get data from the API")
        for data in file_data:
            skip_order = False
            product_dict = {'sku': data.get(original_field_dict.get('product_sku')),
                            'qty': data.get(original_field_dict.get('quantity')),
                            'price': data.get(original_field_dict.get('price')),
                            'discount': data.get(original_field_dict.get('discount')),
                            'shipping': data.get(original_field_dict.get('shipping charge'))}

            shop_product = self.env['sale.shop.product'].search(
                    [('default_code', '=', data.get(original_field_dict.get('product_sku'))),
                     ('shop_id', '=', self.shop_id.id)])
            if data.get(original_field_dict.get('order reference')) in skip_order_list:
                continue
            if not shop_product:
                if self.shop_id.create_prod:
                    product = self.env['product.product'].search([('default_code','=',data.get(
                            original_field_dict.get('product_sku')))],limit=1)
                    if not product:
                        product = self.env['product.product'].create({
                            'name': data.get(original_field_dict.get('product_sku')),
                            'default_code': data.get(original_field_dict.get('product_sku')),
                            'detailed_type': 'product',
                            'categ_id': self.shop_id.default_category_id.id
                        })
                    shop_product = self.env['sale.shop.product'].create({'product_id': product.id,
                                         'product_tmpl_id': product.product_tmpl_id.id,
                                      'default_code' : data.get(original_field_dict.get('product_sku')),
                                      'master_code' : data.get(original_field_dict.get('product_sku')),})
                else :
                    message = 'Product is not synced with SKU %s, Due to that skip order import %s' % (data.get(
                            original_field_dict.get('product_sku')), data.get(original_field_dict.get('order reference')))
                    self.env['shop.fail.log.lines'].create({
                        'operation': 'import_sales_order',
                        'message': message,
                        'is_mismatch': True,
                        'shop_log_id': shop_log_id.id
                    })
                    skip_order_list.append(data.get(original_field_dict.get('order reference')))
                    skip_order = True
            if order_main_dict.get(data.get(original_field_dict.get('order reference'))):
                order_dict = order_main_dict.get(data.get(original_field_dict.get('order reference')))
                if not order_dict.get('skip_order'):
                    order_dict.update({'skip_order': skip_order})
                if order_dict.get('product_info'):
                    order_dict.get('product_info').append(product_dict)
                continue
            order_dict = {'order_ref': data.get(original_field_dict.get('order reference')),
                          'product_info': [product_dict],
                          'order_date': data.get(original_field_dict.get('order_date')),
                          'customer': {'name': data.get(original_field_dict.get('customer_name')),
                                       'email': data.get(original_field_dict.get('customer email'))
                                       },
                          'skip_order': skip_order}
            if original_field_dict.get('billing name') and data.get(original_field_dict.get('billing name')):
                billing_country = data.get(original_field_dict.get('shipping country')) or False
                billing_state = data.get(original_field_dict.get('shipping state')) or False
                order_dict.update({'billing': {
                    'name': data.get(original_field_dict.get('billing name')),
                    'email': data.get(original_field_dict.get('billing email')),
                    'phone': data.get(original_field_dict.get('billing phone')) or False,
                    'street': data.get(original_field_dict.get('billing address')) or False,
                    'city': data.get(original_field_dict.get('billing city')) or False,
                    'state_id': self.get_state(billing_country, billing_state).id or False,
                    'country_id': self.get_country(billing_country).id or False,
                    'zip': data.get(original_field_dict.get('billing zip')) or False,
                }})
            if original_field_dict.get('shipping name') and data.get(original_field_dict.get('shipping name')):
                shipping_country = data.get(original_field_dict.get('shipping country')) or False
                shipping_state = data.get(original_field_dict.get('shipping state')) or False
                order_dict.update({'shipping': {
                    'name': data.get(original_field_dict.get('shipping name')),
                    'email': data.get(original_field_dict.get('shipping email')),
                    'phone': data.get(original_field_dict.get('shipping phone')) or False,
                    'street': data.get(original_field_dict.get('shipping address')) or False,
                    'city': data.get(original_field_dict.get('shipping city')) or False,
                    'state_id': self.get_state(shipping_country, shipping_state).id or False,
                    'country_id': self.get_country(shipping_country).id or False,
                    'zip': data.get(original_field_dict.get('shipping zip')) or False,
                }})
            order_main_dict.update({data.get(original_field_dict.get('order reference')): order_dict})
        return order_main_dict

    def get_state(self, country_code, state_name_or_code):
        """ This method is used to search state-based country, state code or zip code.
        """
        res_country_obj = self.env['res.country.state']
        country = self.get_country(country_code)
        state = res_country_obj.search(['|', ('name', '=ilike', state_name_or_code),
                                        ('code', '=ilike', state_name_or_code),
                                        ('country_id', '=', country.id)], limit=1)
        return state

    def get_country(self, country_name_or_code):
        """
            Usage : Search Country by name or code if not found then use =ilike operator for ignore case sensitive
            search and set limit 1 because it may possible to find multiple emails due to =ilike operator
            :param country_name_or_code: Country Name or Country Code, Type: Char
            :return: res.country()
        """
        country = self.env['res.country'].search(['|', ('code', '=ilike', country_name_or_code),
                                                  ('name', '=ilike', country_name_or_code)], limit=1)
        return country

    def read_csv_file(self):
        file = self.file_name
        csv_data = base64.decodebytes(self.file_name)
        reader = False
        data = []
        try:
            import_file = BytesIO(base64.decodebytes(self.file_name))
            file_read = StringIO(import_file.read().decode())
            reader = csv.DictReader(file_read, delimiter=",")
            _logger.info("Read File____________")
        except:
            pass
        for i in reader:
            data.append(i)
        headers = list(data[0].keys())
        return headers, data

    def read_xlsx_file(self, shop_log_id):
        """
        This method is used to read the xlsx file data.
        """
        validation_header = []
        product_data = []
        sheets = xlrd.open_workbook(file_contents=base64.b64decode(self.file_name.decode('UTF-8')))
        header = dict()
        is_header = False
        header_position = self.header_position - 1
        for sheet in sheets.sheets():
            headers = [d.value for d in sheet.row(header_position)]
            validation_header = headers
            [header.update({d: headers.index(d)}) for d in headers]
            new_range = sheet.nrows - header_position
            for row_no in range(self.header_position, new_range):
                row = dict()
                [row.update({k: sheet.row(row_no)[v].value}) for k, v in header.items() for c in
                 sheet.row(row_no)]
                product_data.append(row)
        return validation_header, product_data

    def import_awb_numbers(self):
        shop_id = self.shop_id
        file_format_id = self.shop_id.delivery_file_format_id
        if not self.filename:
            raise ValidationError(_('Please select file to Process'))

        shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_AWB',
                                                        'shop_id': self.shop_id.id})
        self.create_shop_file_attachment(self.file_name, res_model='shop.fail.log', log_book=shop_log_id,
                                         file_name='AWB number import.xlsx')
        if self.filename.endswith('.csv'):
            headers, file_data = self.read_csv_file()
        else:
            headers, file_data = self.read_xlsx_file(shop_log_id)
        order_main_dict = self.prepare_order_awb_data(headers, file_data, file_format_id, shop_log_id)
        self.env['stock.picking'].update_order_tracking_file(shop_id, order_main_dict, shop_log_id)

    def prepare_order_awb_data(self, headers, file_data, file_format, shop_log_id):
        tracking_main_dict = {}
        skip_order_list = []
        original_field_dict = {}
        if file_format.document_type:
            order_field_list = ['order reference', 'delivery date', 'AWB number', 'sku', 'quantity']
            for field in order_field_list:
                excel_field = file_format.column_ids.filtered(
                        lambda l: l.delivery_order_confirmation_fields == field).name
                if excel_field:
                    original_field_dict.update({field: excel_field})
        else:
            column_obj = self.env['document.column.wizard']
            domain = column_obj.get_domain()
            token = column_obj.get_token()
            route = column_obj.get_column_parser_route()
            data = {
                "token": token,
                "score_threshold": 50,
                "document_id": file_format.document_id,
                "tags": headers
            }
            endpoint = f'{domain}/{route}'
            query = f'{endpoint}'
            response = requests.post(query, data=data)
            response = response.json()
            if not response.get('data'):
                raise ValidationError("Can't able to get data from the API")
        for data in file_data:
            skip_order = False
            product_dict = {'sku': data.get(original_field_dict.get('sku')),
                            'qty': data.get(original_field_dict.get('quantity')),
                            'tracking': data.get(original_field_dict.get('AWB number'))}
            if tracking_main_dict.get(data.get(original_field_dict.get('order reference'))):
                order_dict = tracking_main_dict.get(data.get(original_field_dict.get('order reference')))
                if order_dict.get('product_info'):
                    order_dict.get('product_info').append(product_dict)
                if order_dict.get('tracking_list'):
                    order_dict.get('tracking_list').append(data.get(original_field_dict.get('AWB number')))
                continue
            order_dict = {'order_ref': data.get(original_field_dict.get('order reference')),
                          'product_info': [product_dict],
                          'delivery_date': data.get(original_field_dict.get('delivery date')),
                          'tracking_list': [data.get(original_field_dict.get('AWB number'))]
                          }
            tracking_main_dict.update({data.get(original_field_dict.get('order reference')): order_dict})
        return tracking_main_dict

    def import_return_file(self):
        shop_id = self.shop_id
        file_format_id = self.shop_id.return_file_format_id
        if not self.filename:
            raise ValidationError(_('Please select file to Process'))

        shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_retrun',
                                                        'shop_id': self.shop_id.id})
        self.create_shop_file_attachment(self.file_name, res_model='shop.fail.log', log_book=shop_log_id,
                                         file_name='Return import.xlsx')
        if self.filename.endswith('.csv'):
            headers, file_data = self.read_csv_file()
        else:
            headers, file_data = self.read_xlsx_file(shop_log_id)
        order_main_dict = self.prepare_return_awb_data(headers, file_data, file_format_id, shop_log_id)
        self.env['stock.picking'].create_return_document_of_order(shop_id, order_main_dict, shop_log_id)

    def prepare_return_awb_data(self, headers, file_data, file_format, shop_log_id):
        tracking_main_dict = {}
        skip_order_list = []
        original_field_dict = {}
        if file_format.document_type:
            order_field_list = ['order reference', 'delivery date', 'AWB number', 'sku', 'quantity']
            for field in order_field_list:
                excel_field = file_format.column_ids.filtered(
                        lambda l: l.return_confirmation_fields == field).name
                if excel_field:
                    original_field_dict.update({field: excel_field})
        else:
            column_obj = self.env['document.column.wizard']
            domain = column_obj.get_domain()
            token = column_obj.get_token()
            route = column_obj.get_column_parser_route()
            data = {
                "token": token,
                "score_threshold": 50,
                "document_id": file_format.document_id,
                "tags": headers
            }
            endpoint = f'{domain}/{route}'
            query = f'{endpoint}'
            response = requests.post(query, data=data)
            response = response.json()
            if not response.get('data'):
                raise ValidationError("Can't able to get data from the API")
        for data in file_data:
            skip_order = False
            product_dict = {'sku': data.get(original_field_dict.get('sku')),
                            'qty': data.get(original_field_dict.get('quantity')),
                            'tracking': data.get(original_field_dict.get('AWB number'))}
            if tracking_main_dict.get(data.get(original_field_dict.get('order reference'))):
                order_dict = tracking_main_dict.get(data.get(original_field_dict.get('order reference')))
                if order_dict.get('product_info'):
                    order_dict.get('product_info').append(product_dict)
                if order_dict.get('tracking_list'):
                    order_dict.get('tracking_list').append(data.get(original_field_dict.get('AWB number')))
                continue
            order_dict = {'order_ref': data.get(original_field_dict.get('order reference')),
                          'product_info': [product_dict],
                          'delivery_date': data.get(original_field_dict.get('delivery date')),
                          'tracking_list': [data.get(original_field_dict.get('AWB number'))]
                          }
            tracking_main_dict.update({data.get(original_field_dict.get('order reference')): order_dict})
        return tracking_main_dict

    def import_payment_settlement(self):
        shop_id = self.shop_id
        file_format_id = self.shop_id.payment_settlement_format_id
        if not self.filename:
            raise ValidationError(_('Please select file to Process'))

        shop_log_id = self.env['shop.fail.log'].create({'operation': 'import_payment_settlement',
                                                        'shop_id': shop_id.id})
        self.create_shop_file_attachment(self.file_name, res_model='shop.fail.log', log_book=shop_log_id,
                                         file_name='AWB number import.xlsx')
        if self.filename.endswith('.csv'):
            headers, file_data = self.read_csv_file()
        else:
            headers, file_data = self.read_xlsx_file(shop_log_id)
        # To-do for Dhaval to update below method to create records
        if shop_id.ecommerse_merchant_type == 'Flipkart':
            return self.process_flipkart_payment_settlement_file(shop_id,file_data,headers,shop_log_id)
        if shop_id.ecommerse_merchant_type == 'Amazon':
            return self.process_amazon_payment_settlement_file(shop_id,file_data,headers,shop_log_id)
        if shop_id.ecommerse_merchant_type == 'Ajio':
            return self.process_ajio_payment_settlement_file(shop_id,file_data,headers,shop_log_id)
        if shop_id.ecommerse_merchant_type == 'Myntra':
            return self.process_myntra_payment_settlement_file(shop_id,file_data,headers,shop_log_id)
        if shop_id.ecommerse_merchant_type == 'Citymall':
            return self.process_citymall_payment_settlement_file(shop_id,file_data,headers,shop_log_id)

        # payment_main_dict = self.prepare_shop_payment_settlement_data(headers, file_data, file_format_id, shop_log_id)
        # # ToDo : Implementation for payment details
        # self.env['sale.order'].sudo().process_payment_trasaction_file(shop_id, payment_main_dict, shop_log_id)


    def process_flipkart_payment_settlement_file(self,shop_id,file_data,headers,shop_log_id):
        for data in file_data:
            order = data.get('Order ID')
            if order:
                sale_order = self.env['sale.order'].search(
                        [('client_order_ref', '=', order), ('sales_shop_id', '=', shop_id.id)],
                        limit=1)
                if not sale_order:
                    message = 'Order is not found with Order ID %s' % (data.get('Order ID'))
                    self.env['shop.fail.log.lines'].create({
                        'operation': 'import_payment_settlement',
                        'message': message,
                        'is_mismatch': True,
                        'shop_log_id': shop_log_id.id
                    })
                if sale_order:
                    payment_dict = {'additional_information' : data.get('Additional Information'),
                        'amount_free_shipping' : data.get('Free Shipping Offer (Rs.)'),
                        'amount_non_free_shipping' : data.get('Non-Free Shipping Offer (Rs.)'),
                        'bank_settlement_value' : data.get('Bank Settlement Value (Rs.)'),
                        'chargeable_weight_source' : data.get('Chargeable Weight Source'),
                        'chargeable_weight_type' : data.get('Chargeable Weight Type'),
                        'chargeable_wt_slab' : data.get('Chargeable Wt. Slab (In Kgs)'),
                        'collection_fees' : data.get('Collection Fee (Rs.)'),
                        'commission' : data.get('Commission (Rs.)'),
                        'commission_rate' : data.get('Commission Rate (%)'),
                        'customer_addon_amount_recovery' : data.get('Customer Add-ons Amount Recovery (Rs.)'),
                        'customer_addons_amount' : data.get('Customer Add-ons Amount (Rs.)'),
                        'dead_weight' : data.get('Dead Weight (kgs)'),
                        'discount_in_mp_fees' : data.get('Discount in MP fees (Rs.)'),
                        'dispatch_date' : data.get('Dispatch Date'),
                        'fixed_fees' : data.get('Fixed Fee  (Rs.)'),
                        'franchisee_fees' : data.get('Franchise Fee (Rs.)'),
                        'fulfilment_type' : data.get('Fulfilment Type'),
                        'gst_on_discount' : data.get('GST on Discount (Rs.)'),
                        'gst_on_mp_fees' : data.get('GST on MP Fees (Rs.)'),
                        'income_tax_credit' : data.get('Income Tax Credits (Rs.) [TDS]'),
                        'input_gst_tcs_credit' : data.get('Input GST + TCS Credits (Rs.) [GST+TCS]'),
                        'installation_fees' : data.get('Installation Fee (Rs.)'),
                        'invoice_date' : data.get('Invoice Date'),
                        'invoice_id' : data.get('Invoice ID'),
                        'item_gst_rate' : data.get('Item GST Rate (%)'),
                        'item_return_status' : data.get('Item Return Status'),
                        'marketplace_fees' : data.get('Marketplace Fee (Rs.)'),
                        'my_total_non_shipping_offer_share' : data.get('Non-Free Shipping Offer (Rs.)'),
                        'my_total_non_shipping_share' : data.get('Non-Free Shipping Offer (Rs.)'),
                        'my_total_shipping_share' : data.get('Free Shipping Offer (Rs.)'),
                        'my_totoal_share' : data.get('My share (Rs.)'),
                        'neft_id' : data.get('NEFT ID'),
                        'neft_type' : data.get('Neft Type'),
                        'no_cost_emi_Reimbursement' : data.get('No Cost Emi Fee Reimbursement(Rs.)'),
                        'offer_adjustment' : data.get('Offer Adjustments (Rs.)'),
                        'offer_amount_settled_as_discount_in_mp_fee' : data.get('Offer amount settled as Discount in MP Fee (Rs.)'),
                        'order_date' : data.get('Order Date'),
                        'order_item_id' : data.get('Order item ID'),
                        'payment_date' : data.get('Payment Date'),
                        'pick_pack_fees' : data.get('Pick And Pack Fee (Rs.)'),
                        'product_cancellation_fee' : data.get('Product Cancellation Fee (Rs.)'),
                        'product_sub_category' : data.get('Product Sub Category'),
                        'protection_fund' : data.get('Protection Fund (Rs.)'),
                        'quantity' : data.get('Quantity'),
                        'refund_amount' : data.get('Refund (Rs.)'),
                        'return_type' : data.get('Return Type'),
                        'reverse_shipping_fees' : data.get('Reverse Shipping Fee (Rs.)'),
                        'seller_sku' : data.get('Seller SKU'),
                        'shipping_fees' : data.get('Shipping Fee (Rs.)'),
                        'shipping_zone' : data.get('Shipping Zone'),
                        'shopsy_marketing_fees' : data.get('Shopsy Marketing Fee (Rs.)'),
                        'shopsy_order' : data.get('Shopsy Order'),
                        'tcs' : data.get('TCS (Rs.)'),
                        'tds' : data.get('TDS (Rs.)'),
                        'tech_visit_fees' : data.get('Tech Visit Fee (Rs.)'),
                        'tier' : data.get('Tier'),
                        'total_discount_in_mp_fees' : data.get('Total Discount in MP Fee (Rs.)'),
                        'total_offer_amount' : data.get('Total Offer Amount (Rs.)'),
                        'total_sale_amount' : data.get('Sale Amount (Rs.)'),
                        'total_taxes' : data.get('Taxes (Rs.)'),
                        'total_volume' : data.get('Length*Breadth*Height'),
                        'uninstall_packing_fees' : data.get('Uninstallation & Packaging Fee (Rs.)'),
                        'volumetric_weight' : data.get('Volumetric Weight (kgs)'),
                        }
                    order_item_id = data.get('Order item ID')
                    existing_order_line = sale_order.flipkart_payment_settlement_ids.filtered(lambda l : l.order_item_id ==
                                                                                            order_item_id)
                    shop_product = self.env['sale.shop.product'].search(
                            [('default_code', '=', data.get('Seller SKU')),
                             ('shop_id', '=', self.shop_id.id)])
                    if not existing_order_line:
                        payment_dict.update({'order_id' : sale_order.id,
                                        'product_id' : shop_product and shop_product.product_id.id})
                        self.env['flipkart.payment.settlement'].create(payment_dict)
                    else :
                        existing_order_line.write(payment_dict)
                    self._cr.commit()

    def process_amazon_payment_settlement_file(self, shop_id, file_data,headers,shop_log_id):
        for data in file_data:
            order = data.get('order id')
            sale_order = None
            _logger.info(data)
            if order:
                sale_order = self.env['sale.order'].search([('client_order_ref', '=', order), ('sales_shop_id', '=', shop_id.id)], limit=1)
            if sale_order and sale_order.amazon_payment_settlement_ids:
                continue
            payment_dict = {'sales_shop_id': shop_id.id,
                            'date': data.get('date/time'),
                            'settlement_id': data.get('settlement id'),
                            'type': data.get('type'),
                            'sku': data.get('Sku'),
                            'description': data.get('description'),
                            'quantity': data.get('quantity'),
                            'marketplace': data.get('marketplace'),
                            'account_type': data.get('account type'),
                            'fulfillment': data.get('fulfillment'),
                            'order_city': data.get('order city'),
                            'order_state': data.get('order state'),
                            'order_postal': data.get('order postal'),
                            'product_sales': data.get('product sales'),
                            'shipping_credits': data.get('shipping credits'),
                            'promotional_rebates': data.get('promotional rebates'),
                            'total_sales_tax_liable': data.get('Total sales tax liable(GST before adjusting TCS)'),
                            'tcs_cgst': data.get('TCS-CGST'),
                            'tcs_sgst': data.get('TCS-SGST'),
                            'tcs_igst': data.get('TCS-IGST'),
                            'tds': data.get('TDS (Section 194-O)'),
                            'selling_fees': data.get('selling fees'),
                            'fba_fees': data.get('fba fees'),
                            'other_transaction_fees': data.get('other transaction fees'),
                            'other': data.get('other'),
                            'total': data.get('total'),
                            }
            shop_product = self.env['sale.shop.product'].search(
                [('default_code', '=', data.get('Sku')),
                 ('shop_id', '=', self.shop_id.id)], limit=1)
            _logger.info(shop_product)
            _logger.info(payment_dict)
            payment_dict.update({'order_id': sale_order and sale_order.id,
                                 'product_id': shop_product and shop_product.product_id.id or
                                               False})
            self.env['amazon.payment.settlement'].create(payment_dict)

    def process_ajio_payment_settlement_file(self, shop_id, file_data,headers,shop_log_id):
        for data in file_data:
            order = data.get('Order No')
            sale_order = None
            _logger.info(data)
            if order:
                sale_order = self.env['sale.order'].search([('client_order_ref', '=', order), ('sales_shop_id', '=', shop_id.id)], limit=1)
            if sale_order and sale_order.ajio_payment_settlement_ids:
                continue
            payment_dict = {'sales_shop_id': shop_id.id,
                            'journey_type': data.get('Journey Type'),
                            'clearing_doc_no': data.get('Clearing doc no'),
                            'clearing_date': data.get('Clearing date'),
                            'expected_Settlement_date': data.get('Expected settlement date'),
                            'internal_document_no': data.get('Internal Document no'),
                            'forward_po_number': data.get('Forward PO Number'),
                            'forward_po_date': data.get('Forward PO date'),
                            'invoice_number': data.get('Invoice Number'),
                            'invoice_date': data.get('Invoice Date'),
                            'order_no': data.get('Order No'),
                            'order_date': data.get('Order Date'),
                            'awb_no': data.get('AWB No'),
                            'shipment_no': data.get('Shipment No'),
                            'value': data.get('Value'),
                            'status': data.get('Status'),
                            'credit_note_no': data.get('Credit Note No'),
                            'delivery_challan_number': data.get('Delivery Challan Number'),
                            'delivery_challan_date': data.get('Delivery Challan date'),
                            'pob_id': data.get('POB ID'),
                            'fulfilment_type': data.get('Fulfillment type'),
                            'order_id': sale_order and sale_order.id
                            }
            self.env['ajio.payment.settlement'].create(payment_dict)

    def process_myntra_payment_settlement_file(self, shop_id, file_data,headers,shop_log_id):
        for data in file_data:
            order = data.get('sale_order_code')
            sale_order = None
            _logger.info(data)
            if order:
                sale_order = self.env['sale.order'].search([('client_order_ref', '=', order), ('sales_shop_id', '=', shop_id.id)], limit=1)
            if sale_order and sale_order.myntra_payment_settlement_ids:
                continue
            payment_dict = {
                'sales_shop_id': shop_id.id,
                'order_id': sale_order and sale_order.id,
                'sale_order_code': data.get('sale_order_code'),
                'order_number': data.get('order_number'),
                'order_date': data.get('order_date'),
                'packing_date': data.get('packing_date'),
                'invoice_number': data.get('invoice_number'),
                'product_sku_code': data.get('product_sku_code'),
                'order_item_status': data.get('order_item_status'),
                'promised_delivery_date': data.get('promised_delivery_date'),
                'actual_delivery_date': data.get('actual_delivery_date'),
                'return_date': data.get('return_date'),
                'restocked_date': data.get('restocked_date'),
                'return_type': data.get('return_type'),
                'promised_settlement_date': data.get('promised_settlement_date'),
                'currency': data.get('currency'),
                'customer_paid_amount': data.get('customer_paid_amount'),
                'postpaid_amount': data.get('postpaid_amount'),
                'prepaid_amount': data.get('prepaid_amount'),
                'mrp': data.get('mrp'),
                'discount_amount': data.get('discount_amount'),
                'shipping_case': data.get('shipping_case'),
                'tax_rate': data.get('tax_rate'),
                'igst_amount': data.get('igst_amount'),
                'cgst_amount': data.get('cgst_amount'),
                'sgst_amount': data.get('sgst_amount'),
                'tcs_igst_amt': data.get('tcs_igst_amt'),
                'tcs_sgst_amt': data.get('tcs_sgst_amt'),
                'tcs_cgst_amt': data.get('tcs_cgst_amt'),
                'minimum_commission': data.get('minimum_commission'),
                'commission_pct': data.get('commission_pct'),
                'commission_total_amount': data.get('commission_total_amount'),
                'total_commission_plus_tcs_deduction_fw': data.get('total_commission_plus_tcs_deduction_fw'),
                'logistics_deduction_fw': data.get('logistics_deduction_fw'),
                'customer_paid_amt_fw': data.get('customer_paid_amt_fw'),
                'total_settlement_fw': data.get('total_settlement_fw'),
                'amount_pending_settlement_fw': data.get('amount_pending_settlement_fw'),
                'prepaid_commission_deduction_fw': data.get('prepaid_commission_deduction_fw'),
                'prepaid_logistics_deduction_fw': data.get('prepaid_logistics_deduction_fw'),
                'prepaid_payment_fw': data.get('prepaid_payment_fw'),
                'postpaid_commission_deduction_fw': data.get('postpaid_commission_deduction_fw'),
                'postpaid_logistics_deduction_fw': data.get('postpaid_logistics_deduction_fw'),
                'postpaid_payment_fw': data.get('postpaid_payment_fw'),
                'settlement_date_prepaid_comm_deduction_fw': data.get('settlement_date_prepaid_comm_deduction_fw'),
                'settlement_date_prepaid_logistics_deduction_fw': data.get('settlement_date_prepaid_logistics_deduction_fw'),
                'settlement_date_prepaid_payment_fw': data.get('settlement_date_prepaid_payment_fw'),
                'settlement_date_postpaid_comm_deduction_fw': data.get('settlement_date_postpaid_comm_deduction_fw'),
                'settlement_date_postpaid_logistics_deduction_fw': data.get('settlement_date_postpaid_logistics_deduction_fw'),
                'settlement_date_postpaid_payment_fw': data.get('settlement_date_postpaid_payment_fw'),
                'bank_utr_no_prepaid_comm_deduction_fw': data.get('bank_utr_no_prepaid_comm_deduction_fw'),
                'bank_utr_no_prepaid_logistics_deduction_fw': data.get('bank_utr_no_prepaid_logistics_deduction_fw'),
                'bank_utr_no_prepaid_payment_fw': data.get('bank_utr_no_prepaid_payment_fw'),
                'bank_utr_no_postpaid_comm_deduction_fw': data.get('bank_utr_no_postpaid_comm_deduction_fw'),
                'bank_utr_no_postpaid_logistics_deduction_fw': data.get('bank_utr_no_postpaid_logistics_deduction_fw'),
                'bank_utr_no_postpaid_payment_fw': data.get('bank_utr_no_postpaid_payment_fw'),
                'total_commission_plus_tcs_deduction_rv': data.get('total_commission_plus_tcs_deduction_rv'),
                'logistics_deduction_rv': data.get('logistics_deduction_rv'),
                'customer_paid_amt_rv': data.get('customer_paid_amt_rv'),
                'total_settlement_rv': data.get('total_settlement_rv'),
                'amount_pending_settlement_rv': data.get('amount_pending_settlement_rv'),
                'prepaid_commission_deduction_rv': data.get('prepaid_commission_deduction_rv'),
                'prepaid_logistics_deduction_rv': data.get('prepaid_logistics_deduction_rv'),
                'prepaid_payment_rv': data.get('prepaid_payment_rv'),
                'postpaid_commission_deduction_rv': data.get('postpaid_commission_deduction_rv'),
                'postpaid_logistics_deduction_rv': data.get('postpaid_logistics_deduction_rv'),
                'postpaid_payment_rv': data.get('postpaid_payment_rv'),
                'settlement_date_prepaid_comm_deduction_rv': data.get('settlement_date_prepaid_comm_deduction_rv'),
                'settlement_date_prepaid_logistics_deduction_rv': data.get('settlement_date_prepaid_logistics_deduction_rv'),
                'settlement_date_prepaid_payment_rv': data.get('settlement_date_prepaid_payment_rv'),
                'settlement_date_postpaid_comm_deduction_rv': data.get('settlement_date_postpaid_comm_deduction_rv'),
                'settlement_date_postpaid_logistics_deduction_rv': data.get('settlement_date_postpaid_logistics_deduction_rv'),
                'settlement_date_postpaid_payment_rv': data.get('settlement_date_postpaid_payment_rv'),
                'bank_utr_no_prepaid_comm_deduction_rv': data.get('bank_utr_no_prepaid_comm_deduction_rv'),
                'bank_utr_no_prepaid_logistics_deduction_rv': data.get('bank_utr_no_prepaid_logistics_deduction_rv'),
                'bank_utr_no_prepaid_payment_rv': data.get('bank_utr_no_prepaid_payment_rv'),
                'bank_utr_no_postpaid_comm_deduction_rv': data.get('bank_utr_no_postpaid_comm_deduction_rv'),
                'bank_utr_no_postpaid_logistics_deduction_rv': data.get('bank_utr_no_postpaid_logistics_deduction_rv'),
                'bank_utr_no_postpaid_payment_rv': data.get('bank_utr_no_postpaid_payment_rv'),
                'courier_name': data.get('courier_name'),
                'e_commerce_portal_name': data.get('e_commerce_portal_name'),
                'hsn': data.get('hsn'),
                'product_tax_category': data.get('product_tax_category'),
                'payment_method': data.get('payment_method'),
                'brand': data.get('brand'),
                'gender': data.get('gender'),
                'article_type': data.get('article_type'),
                'supply_type': data.get('supply_type'),
                'is_try_and_buy': data.get('is_try_and_buy'),
                'tracking_no': data.get('tracking_no'),
                'customer_name': data.get('customer_name'),
                'customer_pincode': data.get('customer_pincode'),
                'customer_state': data.get('customer_state'),
                'igst_rate': data.get('igst_rate'),
                'cgst_rate': data.get('cgst_rate'),
                'sgst_rate': data.get('sgst_rate'),
                'taxable_amount': data.get('taxable_amount'),
                'tcs_igst_rate': data.get('tcs_igst_rate'),
                'tcs_sgst_rate': data.get('tcs_sgst_rate'),
                'tcs_cgst_rate': data.get('tcs_cgst_rate'),
                'shipping_amount': data.get('shipping_amount'),
                'gift_amount': data.get('gift_amount'),
                'cart_discount': data.get('cart_discount'),
                'coupon_discount': data.get('coupon_discount'),
                'seller_gstn': data.get('seller_gstn'),
                'seller_name': data.get('seller_name'),
                'seller_state_code': data.get('seller_state_code'),
                'additional_amount': data.get('additional_amount'),
                'postpaid_amount_other': data.get('postpaid_amount_other'),
                'prepaid_amount_other': data.get('prepaid_amount_other'),
                'myntra_gstn': data.get('myntra_gstn'),
                'party_id_to': data.get('party_id_to'),
                'item_code': data.get('Item_Code'),
                'item_created_on': data.get('Item_Created_On'),
                'item_updated_on': data.get('Item_Updated_On'),
                'item_status': data.get('Item_Status'),
                'grn_number': data.get('GRN_Number'),
                'grn_created': data.get('GRN_Created'),
                'vendor_code': data.get('Vendor_Code'),
                'facility': data.get('Facility'),
                'item_type_name': data.get('Item_Type_Name'),
                '_mrp': data.get('_MRP'),
                'item_type_skucode': data.get('Item_Type_skuCode'),
                'vendor_skucode': data.get('Vendor_skuCode'),
                'unit_price_without_tax': data.get('Unit_price_without_tax'),
                'unit_price_with_tax': data.get('Unit_price_with_tax'),
                'rejection_reason': data.get('Rejection_Reason'),
                'gate_pass_No': data.get('Gate_Pass_No'),
                'gate_pass_type': data.get('Gate_Pass_Type'),
                'gate_pass_status': data.get('Gate_Pass_Status'),
                'gate_pass_created': data.get('Gate_Pass_Created'),
                'hsn_code': data.get('HSN_Code'),
                '_invoice_number': data.get('_Invoice_Number'),
                '_invoice_date': data.get('_Invoice_Date'),
                'po_type': data.get('PO_Type'),
                'po_code': data.get('PO_Code'),
                'po_created': data.get('PO_Created'),
                'sale_order_status': data.get('Sale_Order_status'),
                'myntra_status_ogp': data.get('Myntra_Status_OGP'),
                'vendor_style_code': data.get('Vendor_Style_Code'),
                'asn_code': data.get('ASN_code'),
                'asn_created': data.get('ASN_created'),
                'asn_packed': data.get('ASN_packed'),
                'asn_picked': data.get('ASN_picked'),
                'foci_supply_type': data.get('FOCI_supply_type'),
            }
            self.env['myntra.payment.settlement'].create(payment_dict)


    def process_citymall_payment_settlement_file(self, shop_id, file_data,headers,shop_log_id):
        for data in file_data:
            order = data.get('order_id')
            _logger.info(data)
            sale_order = self.env['sale.order'].search([('client_order_ref', '=', order), ('sales_shop_id', '=', self.shop_id.id)], limit=1)
            if sale_order.city_payment_settlement_ids:
                continue
            product_id = self.env['sale.shop.product'].search([('default_code', '=', data.get('sku_id')), ('shop_id', '=', self.shop_id.id)], limit=1)
            payment_dict = {
                'order_id': sale_order.id,
                'product_id': product_id.id,
                'sales_shop_id': self.shop_id.id,
                'order_code': data.get('order_id'),
                'order_date': data.get('order_date'),
                'payment_date': data.get('payment_date'),
                'dispatch_date': data.get('dispatch_date'),
                'return_date_of_delivery_to_seller': data.get('return_date_of_delivery_to_seller'),
                'month_of_return_date_of_delivery_to_seller': data.get('month_of_return_date_of_delivery_to_seller'),
                'product_name': data.get('product_name'),
                'sku_id': data.get('sku_id'),
                'live_order_status': data.get('live_order_status'),
                'product_gst': data.get('product_gst'),
                'listing_price': data.get('listing_price'),
                'quantity': data.get('quantity'),
                'transaction_id': data.get('transaction_id'),
                'final_settlement_amount': data.get('final_settlement_amount'),
                'sale_return_amount': data.get('sale_return_amount'),
                'shipping_revenue': data.get('shipping_revenue'),
                'forward_shipping_fee_without_gst': data.get('forward_shipping_fee_without_gst'),
                'shipping_return_amount': data.get('shipping_return_amount'),
                'return_shipping_fee_without_gst': data.get('return_shipping_fee_without_gst'),
                'total_sale_amount': data.get('total_sale_amount'),
                'platform_fee': data.get('platform_fee'),
                'penalty': data.get('penalty'),
                'shipping_charge': data.get('shipping_charge'),
                'return_shipping_charge': data.get('return_shipping_charge'),
                'tcs': data.get('tcs'),
                'tds': data.get('tds'),
            }
            self.env['citymall.payment.settlement'].create(payment_dict)


    def prepare_shop_payment_settlement_data(self, headers, file_data, file_format, shop_log_id):
        tracking_main_dict = []
        skip_order_list = []
        original_field_dict = {}
        if file_format.document_type:
            order_field_list = ['sale_order', 'sale_amount', 'sku', 'quantity','delivered_quantity' ,'unit_price',
                                'transaction_id','other_charges1', 'other_charges2', 'other_charges3',
                                'other_charges4', 'other_charges5', 'other_charges6',
                                'other_charges7','other_charges8', 'other_charges9', 'other_charges10',
                                'payment_date', 'sale_return_amount', 'shipping_amount', 'igst_rate', 'igst',
                                'cgst_rate', 'cgst', 'sgst_rate', 'sgst', 'tds_rate',
                                'other_charges', 'return_qty']
            for field in order_field_list:
                excel_field = file_format.column_ids.filtered(
                        lambda l: l.payment_settlement_fields == field).name
                if excel_field:
                    original_field_dict.update({field: excel_field})
        for data in file_data:
            # product_dict = {'sku': data.get(original_field_dict.get('sku')),
            #                 'qty': data.get(original_field_dict.get('quantity'))}
            # if tracking_main_dict.get(data.get(original_field_dict.get('sale_order'))):
            #     payment_dict = tracking_main_dict.get(data.get(original_field_dict.get('sale_order')))
            #     if payment_dict:
            #         payment_dict.append(product_dict)
            #     continue
            payment_dict = {'sale_order': data.get(original_field_dict.get('sale_order')),
                            'sale_amount' : {'value': data.get(original_field_dict.get('sale_amount')),'excel_head' : original_field_dict.get('sale_amount')},
                            'sku': data.get(original_field_dict.get('sku')),
                            'qty': {'value': data.get(original_field_dict.get('quantity')),'excel_head' : original_field_dict.get('quantity')},
                            'unit_price': {'value': data.get(original_field_dict.get('unit_price')),'excel_head' :original_field_dict.get('unit_price') },
                            'transaction_id': {'value': data.get(original_field_dict.get('transaction_id')),'excel_head' :original_field_dict.get('transaction_id') },
                            'payment_date': {'value': data.get(original_field_dict.get('payment_date')),'excel_head' : original_field_dict.get('payment_date')},
                            'sale_return_amount': {'value': data.get(original_field_dict.get('sale_return_amount')),'excel_head' : original_field_dict.get('sale_return_amount')},
                            'shipping_amount': {'value': data.get(original_field_dict.get('shipping_amount')),'excel_head' : original_field_dict.get('shipping_amount')},
                            'igst_rate': {'value': data.get(original_field_dict.get('igst_rate')),'excel_head' : original_field_dict.get('igst_rate')},
                            'igst': {'value': data.get(original_field_dict.get('igst')),'excel_head' : original_field_dict.get('igst')},
                            'cgst_rate': {'value': data.get(original_field_dict.get('cgst_rate')),'excel_head' : original_field_dict.get('cgst_rate')},
                            'cgst': {'value': data.get(original_field_dict.get('cgst')),'excel_head' :original_field_dict.get('cgst') },
                            'sgst_rate': {'value': data.get(original_field_dict.get('sgst_rate')),'excel_head' : original_field_dict.get('sgst_rate')},
                            'sgst': {'value': data.get(original_field_dict.get('sgst')),'excel_head' : original_field_dict.get('sgst')},
                            'tds_rate':{'value': data.get(original_field_dict.get('tds_rate')),'excel_head' : original_field_dict.get('tds_rate')},
                            'other_charges': {'value': data.get(original_field_dict.get('other_charges')),'excel_head' : original_field_dict.get('other_charges')},
                            'return_qty': {'value': data.get(original_field_dict.get('return_qty')),'excel_head' : original_field_dict.get('return_qty')},
                            'other_charges1': {'value': data.get(original_field_dict.get('other_charges1')),'excel_head' :original_field_dict.get('other_charges1') },
                            'other_charges2': {'value': data.get(original_field_dict.get('other_charges2')),'excel_head' : original_field_dict.get('other_charges2')},
                            'other_charges3': {'value': data.get(original_field_dict.get('other_charges3')),'excel_head' : original_field_dict.get('other_charges3')},
                            'other_charges4': {'value': data.get(original_field_dict.get('other_charges4')),
                                               'excel_head' : original_field_dict.get('other_charges4')},
                            'other_charges5': {'value': data.get(original_field_dict.get('other_charges5')),
                                               'excel_head' : original_field_dict.get('other_charges5')},
                            'other_charges6': {'value': data.get(original_field_dict.get('other_charges6')),
                                               'excel_head' : original_field_dict.get('other_charges6')},
                            'other_charges7': {'value': data.get(original_field_dict.get('other_charges7')),
                                               'excel_head' : original_field_dict.get('other_charges7')},
                            'other_charges8': {'value': data.get(original_field_dict.get('other_charges8')),
                                               'excel_head' : original_field_dict.get('other_charges8')},
                            'other_charges9': {'value': data.get(original_field_dict.get('other_charges9')),
                                               'excel_head' : original_field_dict.get('other_charges9')},
                            'other_charges10': {'value': data.get(original_field_dict.get('other_charges10')),
                                                'excel_head' : original_field_dict.get('other_charges10')},
                            }
            tracking_main_dict.append(payment_dict)
        return tracking_main_dict

class ExcelReport(models.TransientModel):
    _name = 'excel.report'
    _description = "Excel Report"

    file_name = fields.Char('Excel File', size=64, readonly=True)
    excel_file = fields.Binary('Download Report', readonly=True)
