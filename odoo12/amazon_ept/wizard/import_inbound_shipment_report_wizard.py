#!/usr/bin/python3

import csv
import base64

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
from datetime import datetime
from odoo.exceptions import except_orm

from odoo import models, fields, api


class AmazonInboundShipmentReportWizard(models.TransientModel):
    _name = "amazon.inbound.shipment.report.wizard"
    _description = 'Import In-bound Shipment Report Through CSV File'

    choose_file = fields.Binary(string="Choose File", filters="*.csv",
                                help="Select amazon In-bound shipment file.")
    file_name = fields.Char("Filename", help="File Name")
    delimiter = fields.Selection([('tab', 'Tab'), ('semicolon', 'Semicolon'), ('colon', 'Colon')],
                                 "Separator", default='colon',
                                 help="Select separator type for the separate file data and "
                                      "import into ERP.")

    @api.multi
    def download_inbound_shipment_sample_csv(self):
        """
        Download Sample Box Content file for Inbound Shipment Plan Products Import
        Added by Keyur
        :return: Dict
        """
        attachment = self.env['ir.attachment'].search([('name', '=', 'amazon_inbound_shipment_box_content.csv')])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
            'nodestroy': False,
        }

    @api.one
    def get_file_name(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        return '/tmp/inbount_shipment_report_%s_%s.csv' % (self.env.uid, name)

    @api.one
    def read_file(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        '''
            Read selected file to import inbound shipment report and return Reader to the caller
        '''
        imp_file = StringIO(base64.decodestring(self.choose_file).decode('utf-8'))
        new_file_name = self.get_file_name(name=name)[0]
        file_write = open(new_file_name, 'w')
        file_write.writelines(imp_file.getvalue())
        file_write.close()
        file_read = open(new_file_name, "rU")
        dialect = csv.Sniffer().sniff(file_read.readline())
        file_read.seek(0)
        if self.delimiter == 'semicolon':
            reader = csv.DictReader(file_read, dialect=dialect, delimiter=';',
                                    quoting=csv.QUOTE_NONE)
        elif self.delimiter == 'colon':
            reader = csv.DictReader(file_read, dialect=dialect, delimiter=',',
                                    quoting=csv.QUOTE_NONE)
        else:
            reader = csv.DictReader(file_read, dialect=dialect, delimiter='\t',
                                    quoting=csv.QUOTE_NONE)
        return reader

    @api.one
    def check_fields_validation(self, fields_name):
        """
            This import pattern requires few fields default, so check it first whether it's there or not.
        """
        require_fields = ['Box No', 'Weight Unit', 'Dimension Name', 'Dimension Type']
        missing = []
        for field in require_fields:
            if field not in fields_name:
                missing.append(field)
        if len(missing) > 0:
            raise except_orm(('Incorrect format found..!'), (
                    'Please provide all the required fields in file, missing fields => %s.' % (
                missing)))
        return True

    def fill_dictionary_from_file(self, reader):
        inboud_shipment_data_list = []
        for row in reader:
            vals = {
                'box_no': row.get('Box No', ''),
                'weight_value': row.get('Weight'),
                'weight_unit': row.get('Weight Unit', ''),
                'dimension_name': row.get('Dimension Name', ''),
                'dimension_type': row.get('Dimension Type', ''),
                'dimension_unit': row.get('Dimension Unit', ''),
                'hight': row.get('Height', ''),
                'width': row.get('Width', 0.0),
                'length': row.get('Length', 0.0),
                'seller_sku': row.get('Seller SKU', ''),
                'quantity': row.get('Quantity', 0.0),
            }
            inboud_shipment_data_list.append(vals)
        return inboud_shipment_data_list

    @api.multi
    def import_inbound_shipment_report(self):
        """
            Import inbound shipment excel report.
            @return: True
        """
        if not self.choose_file:
            raise except_orm(('Unable to process..!'), ('Please Upload File to Process...'))

        amazon_inbound_shipment_obj = self.env["amazon.inbound.shipment.ept"]
        product_ul_ept_obj = self.env["product.ul.ept"]
        amazon_product_ept = self.env["amazon.product.ept"]
        amazon_carton_content_info_obj = self.env["amazon.carton.content.info.ept"]

        active_ids = self._context.get('active_ids', [])
        inbound_shipment_id = amazon_inbound_shipment_obj.search([('id', '=', active_ids)], limit=1)
        if inbound_shipment_id and inbound_shipment_id.partnered_small_parcel_ids and inbound_shipment_id.shipping_type == 'sp':
            return True

        current_date = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')
        reader = self.read_file(name=current_date)[0]
        fields_name = reader.fieldnames

        if self.check_fields_validation(fields_name):
            inboud_shipment_data_list = self.fill_dictionary_from_file(reader) or []

            box_no_list = []
            partnered_small_parcel_list = []
            partnered_small_parcel_dict = {}
            amazon_carton_content_info_dict = {}

            for inboud_shipment_dict in inboud_shipment_data_list:
                box_no = inboud_shipment_dict.get("box_no", "")
                seller_sku = inboud_shipment_dict.get('seller_sku', '')
                quantity = inboud_shipment_dict.get('quantity', '')

                if box_no in box_no_list:
                    if amazon_carton_content_info_dict and amazon_carton_content_info_dict.get(
                            box_no) and seller_sku in amazon_carton_content_info_dict.get(box_no):
                        continue
                    amazon_product = amazon_product_ept.search([("seller_sku", "=", seller_sku)],
                                                               limit=1)
                    if amazon_product:
                        amazon_carton_content_info = False
                        amazon_carton_content_info = amazon_carton_content_info_obj.search(
                            [("amazon_product_id", "=", amazon_product.id),
                             ("seller_sku", "=", seller_sku), ("quantity", "=", quantity)], limit=1)
                        if not amazon_carton_content_info:
                            carton_details_vals = {
                                'amazon_product_id': amazon_product.id,
                                'seller_sku': seller_sku,
                                'quantity': quantity
                            }
                            amazon_carton_content_info = amazon_carton_content_info_obj.create(
                                carton_details_vals)
                        if amazon_carton_content_info_dict and amazon_carton_content_info_dict.get(
                                box_no) and seller_sku not in amazon_carton_content_info_dict.get(
                            box_no):
                            amazon_carton_content_info and amazon_carton_content_info_dict.get(
                                box_no).append(amazon_carton_content_info.id)
                        elif not amazon_carton_content_info_dict or not amazon_carton_content_info_dict.get(
                                box_no):
                            amazon_carton_content_info and amazon_carton_content_info_dict.update(
                                {box_no: [amazon_carton_content_info.id]})
                else:
                    box_no_list.append(box_no)
                    _dimension_domain = [
                        ("type", "=", inboud_shipment_dict.get('dimension_type', '')),
                        ("dimension_unit", "=", inboud_shipment_dict.get('dimension_unit', '')),
                        ("height", "=", inboud_shipment_dict.get('hight', 0.00)),
                        ("width", "=", inboud_shipment_dict.get('width', 0.00)),
                        ("length", "=", inboud_shipment_dict.get('length', 0.00)),
                    ]
                    product_ul = product_ul_ept_obj.search(_dimension_domain, limit=1)
                    if not product_ul:
                        dimension_vals = {
                            'name': inboud_shipment_dict.get('dimension_name', ''),
                            'type': inboud_shipment_dict.get('dimension_type', ''),
                            'dimension_unit': inboud_shipment_dict.get('dimension_unit', ''),
                            'height': inboud_shipment_dict.get('hight', 0.00),
                            'width': inboud_shipment_dict.get('width', 0.00),
                            'length': inboud_shipment_dict.get('length', 0.00),
                        }
                        product_ul_id = product_ul_ept_obj.create(dimension_vals)

                    vals = {
                        'ul_id': (product_ul.id if product_ul else (
                                product_ul_id and product_ul_id.id)) or False,
                        'box_no': inboud_shipment_dict.get("box_no", ""),
                        'weight_value': inboud_shipment_dict.get("weight_value", 0.0),
                        'weight_unit': inboud_shipment_dict.get("weight_unit", "")
                    }

                    amazon_product = amazon_product_ept.search([("seller_sku", "=", seller_sku)],
                                                               limit=1)
                    if amazon_product:
                        amazon_carton_content_info = False
                        amazon_carton_content_info = amazon_carton_content_info_obj.search(
                            [("amazon_product_id", "=", amazon_product.id),
                             ("seller_sku", "=", seller_sku), ("quantity", "=", quantity)], limit=1)
                        if not amazon_carton_content_info:
                            carton_details_vals = {
                                'amazon_product_id': amazon_product.id,
                                'seller_sku': seller_sku,
                                'quantity': quantity
                            }
                            amazon_carton_content_info = amazon_carton_content_info_obj.create(
                                carton_details_vals)
                        amazon_carton_content_info and amazon_carton_content_info_dict.update(
                            {box_no: [amazon_carton_content_info.id]})
                        # amazon_carton_content_info and vals.update({'carton_info_ids':[(6,0,[amazon_carton_content_info.id])]})
                    # partnered_small_parcel_list.append((0,0,vals))
                    partnered_small_parcel_dict.update({str(box_no): vals})

            if partnered_small_parcel_dict and box_no_list:
                for parcel_box_no in box_no_list:
                    if partnered_small_parcel_dict.get(
                            parcel_box_no) and amazon_carton_content_info_dict.get(parcel_box_no):
                        partnered_small_parcel_dict.get(parcel_box_no).update({"carton_info_ids": [
                            (6, 0, amazon_carton_content_info_dict.get(parcel_box_no))]})
                        partnered_small_parcel_list.append(
                            (0, 0, partnered_small_parcel_dict.get(parcel_box_no)))
                    else:
                        partnered_small_parcel_list.append(
                            (0, 0, partnered_small_parcel_dict.get(parcel_box_no)))
            print(partnered_small_parcel_list)
            if inbound_shipment_id.shipping_type == 'sp':
                inbound_shipment_id.partnered_small_parcel_ids = partnered_small_parcel_list
            else:
                inbound_shipment_id.partnered_ltl_ids = partnered_small_parcel_list
        return True
