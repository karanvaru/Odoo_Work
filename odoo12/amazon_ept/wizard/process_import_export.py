import time
import logging
import base64
import csv
import dateutil.parser
from io import StringIO
from collections import defaultdict
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.addons.iap.models import iap
from ..endpoint import DEFAULT_ENDPOINT

_logger = logging.getLogger(__name__)


class amazon_process_import_export(models.TransientModel):
    _name = 'amazon.process.import.export'
    _description = 'amazon.process.import.export'

    instance_ids = fields.Many2many("amazon.instance.ept", 'amazon_instance_import_export_rel',
                                    'process_id', 'instance_id', "Instances")

    instance_id = fields.Many2one('amazon.instance.ept', string='Instance',
                                  help="This Field relocates amazon instance.")

    browse_node_ids = fields.Many2many("amazon.browse.node.ept",
                                       'amazon_browse_node_import_export_rel',
                                       'process_id', 'browse_node_id', "Browse Nodes")

    is_another_soft_create_fba_inventory = fields.Boolean(
        related="seller_id.is_another_soft_create_fba_inventory",
        string="Does another software create the FBA Inventory reports?",
        help="Does another software create the FBA Inventory reports")

    export_product = fields.Boolean('Export Products')
    export_product_images = fields.Boolean('Update Product Images')
    seller_id = fields.Many2one('amazon.seller.ept', string='Amazon Seller', help="Select Amazon Seller Account")
    is_global_warehouse_in_fba = fields.Boolean(related="instance_id.is_global_warehouse_in_fba",
                                                string='Allow Create Removal Order In FBA?',
                                                help="Allow to create removal order in FBA.")

    report_start_date = fields.Datetime("Start Date", help="Start date of report.")
    report_end_date = fields.Datetime("End Date", help="End date of report.")

    @api.multi
    def _check_duration(self):
        if self.report_start_date and self.report_end_date < self.report_start_date:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date must be precede its end date.',
         ['report_start_date', 'report_end_date'])
    ]

    is_split_report = fields.Boolean('Is Split Report ?', default=False)
    split_report_by_days = fields.Selection([
        ('3', '3'),
        ('7', '7'),
        ('15', '15')
    ], 'Split Report By Days')

    selling_on = fields.Selection([
        ('FBM', 'FBM'),
        ('FBA', 'FBA'),
        ('fba_fbm', 'FBA & FBM')
    ], 'Operation For')

    fbm_operations = fields.Selection([
        ('export_inventory', 'Export Stock from Odoo to Amazon'),
        ('update_order_status', 'Update Order Status'),
        ('import_fbm_order', 'Import FBM Orders'),
    ], 'FBM Operations')

    fba_operations = fields.Selection([
        ('import_pending_orders', 'Import Pending Orders'),
        ('check_cancel_orders_fba', 'Check Cancel Orders'),
        ('shipment_report', 'Shipment Report'),
        ('stock_adjustment_report', 'Stock Adjustment Report'),
        ('removal_order_report', 'Removal Order Report'),
        ('customer_return_report', 'Customer Return Report'),
        ('removal_order_request', 'Removal Order Request'),
        ('import_inbound_shipment', 'Import Inbound Shipment'),
        ('create_inbound_shipment_plan', 'Create Inbound Shipment Plan'),
        ('fba_live_inventory_report', 'FBA Live Inventory')
    ], 'Operations')

    both_operations = fields.Selection([
        ('import_product', 'Import Product'),
        ('sync_active_products', 'Sync Active Products'),
        ('export_product_price', 'Export Price From Odoo to Amazon'),
        ('list_settlement_report', 'List Settlement report'),

    ], 'FBA & FBM Operations')

    start_date = fields.Datetime(string="Start Date")  # for flat report
    end_date = fields.Datetime(string="End Date")  # for flat report

    shipment_id = fields.Char('Shipment Id')
    from_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")

    auto_create_product = fields.Boolean(string='Auto create product?', default=False,
                                         help='Create product in ERP if not found.')

    update_price_in_pricelist = fields.Boolean(string='Update price in pricelist?', default=False,
                                               help='Update or create product line in pricelist if ticked.')
    file_name = fields.Char("File Name")
    choose_file = fields.Binary(string="Choose File", filename="filename")
    delimiter = fields.Selection([('tab', 'Tab'), ('semicolon', 'Semicolon'), ('comma', 'Comma')],
                                 string="Separator", default='comma')
    create_record_from_file = fields.Boolean("Create Report From File", default=False)
    import_file = fields.Binary("Choose File")

    @api.onchange('report_start_date', 'report_end_date')
    def onchange_shipment_report_date(self):
        if self.report_start_date and self.report_end_date:
            count = self.report_end_date.date() - self.report_start_date.date()
            if count.days > 7:
                self.is_split_report = True
            else:
                self.is_split_report = False

    @api.onchange('selling_on')
    def onchange_selling_on(self):
        self.fbm_operations = False
        self.fba_operations = False
        self.both_operations = False

    @api.onchange('seller_id')
    def onchange_seller(self):
        instance_ids = self.env['amazon.instance.ept'].search(
            [('seller_id', '=', self.seller_id and self.seller_id.id or False)])
        self.instance_ids = instance_ids

    @api.onchange('fbm_operations')
    def onchange_operations(self):
        # self.export_inventory = False
        # self.export_product_price = False
        # self.list_settlement_report = False
        # self.fbm_shipped_order_updated_after_date = False
        # self.updated_after_date = False
        self.report_start_date = False
        self.report_end_date = False

    @api.onchange('fba_operations')
    def onchange_fba_operations(self):
        """
        On change of fba_operations field it set start and end date as per configurations from seller
        default start date is -3 days from the date.
        :return:
        """
        if self.fba_operations == "shipment_report":
            self.report_start_date = datetime.now() - timedelta(self.seller_id.fba_shipment_report_days)
            self.report_end_date = datetime.now()

        if self.fba_operations == "customer_return_report":
            self.report_start_date = datetime.now() - timedelta(self.seller_id.customer_return_report_days)
            self.report_end_date = datetime.now()

        if self.fba_operations == "stock_adjustment_report":
            self.report_start_date = datetime.now() - timedelta(self.seller_id.inv_adjustment_report_days)
            self.report_end_date = datetime.now()

        if self.fba_operations == "removal_order_report":
            self.report_start_date = datetime.now() - timedelta(self.seller_id.removal_order_report_days)
            self.report_end_date = datetime.now()

        if self.fba_operations == "fba_live_inventory_report" and self.seller_id.is_another_soft_create_fba_inventory:
            self.report_start_date = datetime.now() - timedelta(self.seller_id.live_inv_adjustment_report_days)
            self.report_end_date = datetime.now()

    @api.multi
    def import_export_processes(self):

        """
        Import / Export Operations are managed from here.
        as per selection on wizard this function will execute
        :return: True
        """
        sale_order_obj = self.env['sale.order']
        # fbm_sale_order_report_obj = self.env['fbm.sale.order.report.ept']
        fba_shipping_report_obj = self.env['shipping.report.request.history']
        customer_return_report_obj = self.env['sale.order.return.report']
        amazon_product_obj = self.env['amazon.product.ept']
        stock_adjustment_report_obj = self.env['amazon.stock.adjustment.report.history']
        removal_order_request_report_record = self.env['amazon.removal.order.report.history']
        live_inventory_request_report_record = self.env['amazon.fba.live.stock.report.ept']
        amazon_removal_order_obj = self.env['amazon.removal.order.ept']
        import_shipment_obj = self.env['amazon.inbound.import.shipment.ept']

        seller_import_order_marketplaces = defaultdict(list)
        seller_export_order_marketplaces = defaultdict(list)
        seller_pending_order_marketplaces = defaultdict(list)
        cancel_order_marketplaces = defaultdict(list)
        export_product_price_instance = defaultdict(list)

        if self.start_date:
            db_import_time = time.strptime(str(self.start_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date)
        else:
            start_date = False

        if self.end_date:
            db_import_time = time.strptime(str(self.end_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            end_date = str(end_date)
        else:
            end_date = False

        if self.fba_operations == "shipment_report":
            if not self.report_start_date or not self.report_end_date:
                raise Warning('Please select Date Range.')
            if self.seller_id.is_another_soft_create_fba_shipment:
                vals = {'report_type': '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_',
                        'name': 'FBA Shipping Report',
                        'model_obj': self.env['shipping.report.request.history'],
                        'sequence': self.env.ref('amazon_ept.seq_import_shipping_report_job'),
                        'tree_id': self.env.ref(
                            'amazon_ept.amazon_shipping_report_request_history_tree_view_ept'),
                        'form_id': self.env.ref(
                            'amazon_ept.amazon_shipping_report_request_history_form_view_ept'),
                        'res_model': 'shipping.report.request.history',
                        'start_date': self.report_start_date,
                        'end_date': self.report_end_date
                        }
                self.get_reports(vals)

            elif self.is_split_report and not self.split_report_by_days:
                raise Warning('Please select the Split Report By Days.')
            elif self.is_split_report and self.split_report_by_days:
                start_date = self.report_start_date
                end_date = False
                shipping_report_record_list = []

                while start_date <= self.report_end_date:
                    if end_date:
                        start_date = end_date

                    if start_date >= self.report_end_date:
                        break

                    end_date = (start_date + timedelta(int(self.split_report_by_days))) - timedelta(1)
                    if end_date > self.report_end_date:
                        end_date = self.report_end_date

                    shipping_report_record = fba_shipping_report_obj.create({
                        'seller_id': self.seller_id.id,
                        'start_date': start_date,
                        'end_date': end_date
                    })
                    shipping_report_record.request_report()
                    shipping_report_record_list.append(shipping_report_record.id)

                return {
                    'name': _('FBA Shipping Report'),
                    'view_mode': 'tree, form',
                    'views': [
                        (self.env.ref('amazon_ept.amazon_shipping_report_request_history_tree_view_ept').id, 'tree'),
                        (False, 'form')],
                    'res_model': 'shipping.report.request.history',
                    'type': 'ir.actions.act_window',
                    'res_id': shipping_report_record_list
                }
            else:
                shipping_report_record = fba_shipping_report_obj.create({
                    'seller_id': self.seller_id.id,
                    'start_date': self.report_start_date,
                    'end_date': self.report_end_date
                })
                shipping_report_record.request_report()
                return {
                    'name': _('FBA Shipping Report'),
                    'view_mode': 'form',
                    'res_model': 'shipping.report.request.history',
                    'type': 'ir.actions.act_window',
                    'res_id': shipping_report_record.id
                }

        if self.fba_operations == 'customer_return_report':
            customer_return_report_record = customer_return_report_obj.create({
                'seller_id': self.seller_id.id,
                'start_date': self.report_start_date,
                'end_date': self.report_end_date
            })
            customer_return_report_record.request_report()
            return {
                'name': _('Customer Return Report'),
                'view_mode': 'form',
                'res_model': 'sale.order.return.report',
                'type': 'ir.actions.act_window',
                'res_id': customer_return_report_record.id
            }

        if self.fba_operations == "stock_adjustment_report":
            if not self.report_start_date or not self.report_end_date:
                raise Warning('Please select Date Range.')

            stock_adjustment_report_record = stock_adjustment_report_obj.create({
                'seller_id': self.seller_id.id,
                'start_date': self.report_start_date,
                'end_date': self.report_end_date
            })
            return {
                'name': _('Stock Adjustment Report Request History'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'amazon.stock.adjustment.report.history',
                'type': 'ir.actions.act_window',
                'res_id': stock_adjustment_report_record.id
            }

        if self.fba_operations == "fba_live_inventory_report":
            inv_report_ids = []
            if self.seller_id.is_another_soft_create_fba_inventory:
                if not self.report_start_date or not self.report_end_date:
                    raise Warning('Please select Date Range.')
                vals = {'start_date': self.report_start_date,
                        'end_date': self.report_end_date,
                        'seller_id': self.seller_id,
                        'instance_ids': self.instance_ids
                        }
                fba_live_stock_report = live_inventory_request_report_record.get_inventory_report(vals)
                return fba_live_stock_report
            elif self.seller_id.is_pan_european:
                fba_live_stock_report = live_inventory_request_report_record.create(
                    {'seller_id': self.seller_id.id, 'report_date': datetime.now()})
                fba_live_stock_report.request_report()
                inv_report_ids.append(fba_live_stock_report.id)
            else:
                if not self.instance_ids:
                    instance_ids = self.seller_id.instance_ids
                else:
                    instance_ids = self.instance_ids
                for instance in instance_ids:
                    fba_live_stock_report = live_inventory_request_report_record.create(
                        {'seller_id': self.seller_id.id, 'report_date': datetime.now(), 'amz_instance_id': instance.id})
                    fba_live_stock_report.request_report()
                    inv_report_ids.append(fba_live_stock_report.id)
            if inv_report_ids:
                action = self.env.ref('amazon_ept.action_live_stock_report_ept', False)
                result = action and action.read()[0] or {}
                if len(inv_report_ids) > 1:
                    result['domain'] = "[('id','in',[" + ','.join(map(str, inv_report_ids)) + "])]"
                else:
                    res = self.env.ref('amazon_ept.amazon_live_stock_report_form_view_ept', False)
                    result['views'] = [(res and res.id or False, 'form')]
                    result['res_id'] = inv_report_ids and inv_report_ids[0] or False
                return result
        if self.fba_operations == "removal_order_report":
            if not self.report_start_date or not self.report_end_date:
                raise Warning('Please select Date Range.')

            removal_order_request_report_record = removal_order_request_report_record.create({
                'seller_id': self.seller_id.id,
                'start_date': self.report_start_date,
                'end_date': self.report_end_date
            })
            return {
                'name': _('Removal Order Report Request History'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'amazon.removal.order.report.history',
                'type': 'ir.actions.act_window',
                'res_id': removal_order_request_report_record.id
            }
        if self.fba_operations == "removal_order_request":
            if not self.is_global_warehouse_in_fba or not self.instance_id:
                raise Warning(
                    'This Seller no any instance configure removal order Please configure removal order configuration.')

            amazon_removal_order_obj = amazon_removal_order_obj.create({
                'removal_disposition': 'Return',
                'warehouse_id': self.instance_id and self.instance_id.removal_warehouse_id.id or False,
                'ship_address_id': self.instance_id.company_id.partner_id.id,
                'company_id': self.seller_id.company_id.id,
                'instance_id': self.instance_id.id,
            })
            return {
                'name': _('Removal Order Request'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'amazon.removal.order.ept',
                'type': 'ir.actions.act_window',
                'res_id': amazon_removal_order_obj.id
            }
        if self.fba_operations == "import_inbound_shipment":
            import_shipment_obj.get_inbound_import_shipment(self.instance_id,
                                                            self.from_warehouse_id,
                                                            self.shipment_id)

        if self.fba_operations == "create_inbound_shipment_plan":
            return self.wizard_create_inbound_shipment_plan(self.seller_id, self.instance_id)

        if self.both_operations == "sync_active_products":
            return self.create_sync_active_products(self.seller_id, self.instance_id,
                                                    self.update_price_in_pricelist, self.auto_create_product)

        if self.both_operations == "import_product":
            return self.import_csv_file()

        if self.instance_ids:
            instance_ids = self.instance_ids
        else:
            instance_ids = self.seller_id.instance_ids

        for instance in instance_ids:
            if self.fbm_operations == 'import_fbm_order':
                seller_import_order_marketplaces[instance.seller_id].append(
                    instance.market_place_id)

            if self.both_operations == 'export_product_price':
                export_product_price_instance[instance.seller_id].append(instance)

            if self.fbm_operations == 'export_inventory':
                instance.export_stock_levels()

            if self.fbm_operations == 'update_order_status':
                seller_export_order_marketplaces[instance.seller_id].append(
                    instance.market_place_id)

            if self.fba_operations == 'import_pending_orders':
                seller_pending_order_marketplaces[instance.seller_id].append(
                    instance.market_place_id)

            if self.fba_operations == 'check_cancel_orders_fba':
                cancel_order_marketplaces[instance.seller_id].append(instance.market_place_id)

        if seller_import_order_marketplaces:
            for seller, marketplaces in seller_import_order_marketplaces.items():
                if seller.create_sale_order_from_flat_or_xml_report == 'api':
                    sale_order_obj.import_sales_order(seller, marketplaces, end_date,start_date)

        if seller_export_order_marketplaces:
            for seller, marketplaces in seller_export_order_marketplaces.items():
                sale_order_obj.amz_update_order_status(seller, marketplaces)

        if seller_pending_order_marketplaces:
            for seller, marketplaces in seller_pending_order_marketplaces.items():
                sale_order_obj.import_fba_pending_sales_order(seller, marketplaces)

        if cancel_order_marketplaces:
            for seller, marketplaces in cancel_order_marketplaces.items():
                sale_order_obj.check_cancel_order_in_amazon(seller, marketplaceids=marketplaces,
                                                            instance_ids=instance_ids.ids or [])

        if export_product_price_instance:
            for seller, instance_ids in export_product_price_instance.items():
                for instance in instance_ids:
                    amazon_products = amazon_product_obj.search(
                        [('instance_id', '=', instance.id), ('exported_to_amazon', '=', True)])
                    if amazon_products:
                        amazon_products.update_price(instance)

        if self.both_operations == 'list_settlement_report':
            vals = {'report_type': '_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_',
                    'name': 'Amazon Settlement Reports',
                    'model_obj': self.env['settlement.report.ept'],
                    'sequence': self.env.ref('amazon_ept.seq_import_settlement_report_job'),
                    'tree_id': self.env.ref('amazon_ept.amazon_settlement_report_tree_view_ept'),
                    'form_id': self.env.ref('amazon_ept.amazon_settlement_report_form_view_ept'),
                    'res_model': 'settlement.report.ept',
                    'start_date': self.report_start_date,
                    'end_date': self.report_end_date
                    }
            return self.get_reports(vals)

        return True

    def download_sample_attachment(self):
        """
        This Method relocates download sample file of amazon.
        :return: This Method return file download file.
        """
        attachment = self.env['ir.attachment'].search([('name', '=', 'import_product_sample.csv')])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
            'nodestroy': False,
        }

    def import_csv_file(self):
        """
        This Method relocates Import product csv in amazon listing and mapping of amazon product listing.
        :return:"""

        if not self.choose_file:
            raise Warning('Please Upload File.')

        self.read_import_csv_file()
        if self.choose_file:
            csv_file = StringIO(base64.b64decode(self.choose_file).decode())
            file_write = open('/tmp/products.csv', 'w+')
            file_write.writelines(csv_file.getvalue())
            file_write.close()

            product_obj = self.env["product.product"]
            amazon_product_ept_obj = self.env['amazon.product.ept']
            instance_dict = {}
            if self.delimiter == "tab":
                reader = csv.DictReader(open('/tmp/products.csv', "rU"), delimiter="\t")
            elif self.delimiter == "semicolon":
                reader = csv.DictReader(open('/tmp/products.csv', "rU"), delimiter=";")
            else:
                reader = csv.DictReader(open('/tmp/products.csv', "rU"), delimiter=",")
            if reader:
                if reader.fieldnames and len(reader.fieldnames) == 5:
                    for line in reader:
                        amazon_product_name = line.get('Title')
                        odoo_default_code = line.get('Internal Reference')
                        seller_sku = line.get('Seller SKU')
                        amazon_marketplace = line.get('Marketplace')
                        fullfillment_by = line.get('Fulfillment')
                        instance = False

                        if odoo_default_code:
                            odoo_product_id = product_obj.search(['|',("default_code", "=", odoo_default_code),("barcode", "=", odoo_default_code)])
                            if not odoo_product_id:
                                odoo_product_dict = {
                                    'name': amazon_product_name,
                                    'default_code': odoo_default_code,
                                    'type': 'product'
                                }
                                odoo_product_id = product_obj.create(odoo_product_dict)

                            if amazon_marketplace:
                                instance = instance_dict.get(amazon_marketplace)
                                if not instance:
                                    instance = self.seller_id.instance_ids.filtered(
                                        lambda l: l.marketplace_id.name == amazon_marketplace)
                                    instance_dict.update({amazon_marketplace: instance})

                            if instance and fullfillment_by and seller_sku:
                                amazon_product_id = amazon_product_ept_obj.search(
                                    [("seller_sku", "=", seller_sku),
                                     ("fulfillment_by", "=", fullfillment_by),
                                     ("instance_id", "=", instance.id)], limit=1)
                                if amazon_product_id:
                                    continue
                                elif not amazon_product_id:
                                    self.create_amazon_product(odoo_product_id,
                                                               amazon_product_name, fullfillment_by, seller_sku,
                                                               instance)
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': "All products import successfully!",
                            'img_url': '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    raise Warning(
                        "Either file is invalid or proper delimiter/separator is not specified "
                        "or not found required fields.")
            else:
                raise Warning(
                    "Either file format is not csv or proper delimiter/separator is not specified")
        else:
            raise Warning("Please Select File and/or choose Amazon Seller to Import Product")

    def create_amazon_product(self, odoo_product_id, amazon_product_name, fullfillment_by,
                              seller_sku, instance):
        """
        This Method relocates if product exist in odoo and product does't exist in amazone create amazon product listing.
        :param odoo_product_id: This arguments relocates browse object of odoo product.
        :param amazon_product_name: This arguments relocates product name of amazon.
        :param fullfillment_by: This arguments relocates fullfillment of amazon.
        :param seller_sku: This arguments relocates seller sku of amazon product.
        :param instance: This arguments relocates instance of amazon.
        :return: This method return boolean(True/False).
        """
        amazon_product_ept_obj = self.env['amazon.product.ept']
        amazon_product_ept_obj.create(
            {'title': amazon_product_name or odoo_product_id.name,
             'fulfillment_by': fullfillment_by,
             'product_id': odoo_product_id.id,
             'seller_sku': seller_sku,
             'instance_id': instance.id,
             'exported_to_amazon': True}
        )
        return True

    def read_import_csv_file(self):
        """
        This Method relocates read csv and check validation if seller sku does't exist in csv rais error.
        :return: This Method return boolean(True/False).
        """
        if self.choose_file:
            data = StringIO(base64.b64decode(self.choose_file).decode())

            if self.delimiter == "tab":
                reader = csv.DictReader(data, delimiter='\t')
            elif self.delimiter == "semicolon":
                reader = csv.DictReader(data, delimiter=';')
            else:
                reader = csv.DictReader(data, delimiter=',')
            seller_error_line = []

            next(reader)
            for line in reader:
                if not line.get('Seller SKU'):
                    seller_error_line.append(reader.line_num)
            message = ""
            if seller_error_line:
                message += ('File is invalid Seller SKU must be required field.')
            if message:
                raise UserError(message)

    def create_sync_active_products(self, seller_id, instance_id,
                                    update_price_in_pricelist, auto_create_product):
        """
            Process will create record of Active Product List of selected seller and instance
            @:param - seller_id - selected seller from wizard
            @:param - instance_id - selected instance from wizard
            @:param - update_price_in_pricelist - Boolean for create pricelist or not
            @:param - auto_create_product - Boolean for create product or not
        """
        if not instance_id:
            raise Warning('Please Select Instance')
        active_product_listing_obj = self.env['active.product.listing.report.ept']
        form_id = self.env.ref('amazon_ept.active_product_list_form_view_ept')
        vals = {'instance_id': instance_id.id,
                'seller_id': seller_id.id,
                'update_price_in_pricelist': update_price_in_pricelist or False,
                'auto_create_product': auto_create_product or False
                }

        active_product_listing = active_product_listing_obj.create(vals)
        try:
            pass
            # active_product_listing.request_report()
        except Exception as exception:
            raise Warning(exception)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Product List',
            'res_model': 'active.product.listing.report.ept',
            'res_id': active_product_listing.id,
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'current'
        }

    def wizard_create_inbound_shipment_plan(self, seller_id, instance):
        """
        This method will create shipment plan record of selected seller and instance
        :return:
        """
        if not instance:
            raise Warning('Please Select Instance')
        inbound_shipment_plan_obj = self.env['inbound.shipment.plan.ept']
        form_id = self.env.ref('amazon_ept.inbound_shipment_plan_form_view')

        warehouse_id = instance.warehouse_id
        vals = {'instance_id': instance.id,
                'warehouse_id': warehouse_id.id,
                'ship_from_address_id': warehouse_id.partner_id and \
                                        warehouse_id.partner_id.id,
                'company_id': instance.company_id and instance.company_id.id,
                'ship_to_country': instance.country_id and instance.country_id.id
                }
        shipment_plan_id = inbound_shipment_plan_obj.create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Inbound Shipment Plan',
            'res_model': 'inbound.shipment.plan.ept',
            'res_id': shipment_plan_id.id,
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'current'
        }

    def prepare_merchant_report_dict(self, seller):
        """
        :return: This method will prepare merchant' informational dictionary which will
                 passed to  amazon api calling method.
        """
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        return {
            'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
            'auth_token': seller.auth_token and str(seller.auth_token) or False,
            'app_name': 'amazon_ept',
            'account_token': account.account_token,
            'emipro_api': 'get_reports',
            'dbuuid': dbuuid,
            'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                       seller.country_id.code,
        }

    def get_reports(self, vals):
        """
        This method will get settlement report data from amazon and create it's record in odoo.
        :return: This method will redirecting us to settlement report tree view.

        "Update by twinkalc-13 jan 2020 : Code to process for settlement report(xml format) and shipment report
         for settlement updated changes related to process from uploaded file and also from the
         give date range of report"

        """

        settlement_obj = self.env['settlement.report.ept']
        bank_statement_obj = self.env['account.bank.statement']
        transaction_log_obj = self.env['amazon.transaction.log']
        log_book_obj = self.env['amazon.process.log.book']
        tree_id = vals.get('tree_id')
        form_id = vals.get('form_id')
        seller = self.seller_id
        odoo_report_ids = []
        if not seller:
            raise Warning('Please select seller')

        start_date, end_date = self.get_fba_reports_date_format()
        kwargs = self.sudo().prepare_merchant_report_dict(seller)
        kwargs.update(
            {'report_type': vals.get('report_type'), 'start_date': start_date,
             'end_date': end_date})

        if self.create_record_from_file and self.both_operations == 'list_settlement_report':
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

                vals.update({'report_request_id': False,
                             'report_id': False,
                             'attachment_id': attachment.id,
                             'currency_id': currency_rec and currency_rec[0].id or False,
                             'instance_id': instance and instance[0].id or False,
                             'start_date': start_date and start_date.strftime('%Y-%m-%d'),
                             'end_date': end_date and end_date.strftime('%Y-%m-%d'),
                             'company_id': seller.company_id and seller.company_id.id or False})

                report = settlement_obj.create(vals)

                odoo_report_ids.append(report.id)

                report.message_post(body=_("<b>Settlement Report Downloaded</b>"),
                                    attachment_ids=attachment.ids)

        else:
            response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs, timeout=1000)
            if response.get('reason'):
                if self._context.get('is_auto_process'):
                    log_vals = {
                        'application': 'other',
                        'operation_type': 'import',
                        'message': 'Amazon Settlement Report',
                    }
                    log_rec = log_book_obj.create(log_vals)
                else:
                    return Warning(response.get('reason'))

                transaction_vals = {'log_type': 'error',
                                    'action_type': 'terminate_process_with_log',
                                    'message': response.get('reason'),
                                    'job_id': log_rec.id, }
                transaction_log_obj.create(transaction_vals)
            else:
                list_of_wrapper = response.get('result')

                odoo_report_ids = self.prepare_fba_report_vals(list_of_wrapper, vals.get('start_date'),
                                                               vals.get('end_date'), vals.get('model_obj'),
                                                               vals.get('sequence'))

        if self._context.get('is_auto_process'):
            return odoo_report_ids

        return {
            'type': 'ir.actions.act_window',
            'name': vals.get('name'),
            'res_model': vals.get('res_model'),
            'domain': [('id', 'in', odoo_report_ids)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'view_id': tree_id.id,
            'target': 'current'
        }

    def prepare_fba_report_vals(self, list_of_wrapper, start_date, end_date, model_obj, sequence):
        """
        Added by Udit
        This method will create settlement report and it's attachments from the amazon api response.
        :param list_of_wrapper: Dictionary of amazon api response.
        :param start_date: Selected start date in wizard in specific format.
        :param end_date: Selected end date in wizard in specific format.
        :return: This method will return list of newly created settlement report id.
        """
        odoo_report_ids = []
        if list_of_wrapper is None:
            list_of_wrapper = []
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
                report_exist = model_obj.search(
                    ['|', ('report_request_id', '=', request_id), ('report_id', '=', report_id),
                     ('report_type', '=', report_type)])
                if report_exist:
                    report_exist = report_exist[0]
                    odoo_report_ids.append(report_exist.id)
                    continue
                vals = self.prepare_fba_report_vals_for_create(report_type, request_id, report_id, start_date, end_date,
                                                               sequence)
                report_rec = model_obj.create(vals)
                report_rec.get_report()
                self._cr.commit()
                odoo_report_ids.append(report_rec.id)
        return odoo_report_ids

    def prepare_fba_report_vals_for_create(self, report_type, request_id, report_id, start_date, end_date, sequence):
        """
        Added by Udit
        :param report_type: Report type.
        :param request_id: Amazon request id.
        :param report_id: Amazon report id.
        :param start_date: Selected start date in wizard in specific format.
        :param end_date: Selected end date in wizard in specific format.
        :return: This method will prepare and return settlement report vals.
        """
        try:
            if sequence:
                report_name = sequence.next_by_id()
            else:
                report_name = '/'
        except:
            report_name = '/'
        return {
            'name': report_name,
            'report_type': report_type,
            'report_request_id': request_id,
            'report_id': report_id,
            'start_date': start_date,
            'end_date': end_date,
            'state': '_DONE_',
            'seller_id': self.seller_id.id,
            'user_id': self._uid,
        }

    def get_fba_reports_date_format(self):
        """
        Added by Udit
        This method will convert selected time duration in specific format to send it to amazon.
        If start date and end date is empty then system will automatically select past 90 days time duration.
        :return: This method will return converted start and end date.
        """
        start_date = self.report_start_date
        end_date = self.report_end_date
        if start_date:
            db_import_time = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S", db_import_time)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(db_import_time, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date) + 'Z'
        else:
            today = datetime.now()
            earlier = today - timedelta(days=90)
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
        return start_date, end_date
