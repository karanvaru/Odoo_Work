import csv
import itertools
import operator
from datetime import datetime
from io import StringIO
import base64
from odoo import models, fields, api
from odoo.exceptions import except_orm


class import_product_inbound_shipment(models.TransientModel):
    _name = 'import.product.inbound.shipment'
    _description = 'Import product through csv file for inbound shipment'

    choose_file = fields.Binary('Choose File', filters='*.csv')
    shipment_id = fields.Many2one('inbound.shipment.plan.ept', 'Shipment Reference')
    update_existing = fields.Boolean('Do you want to update already exist record ?')
    replace_product_qty = fields.Boolean('Do you want to replace product quantity?', help="""
        If you select this option then it will replace product quantity by csv quantity field data, 
        it will not perform addition like 2 quantity is there in line and csv contain 3,
        then it will replace 2 by 3, it won't be updated by 5.
        
        If you have not selected this option then it will increase (addition) line quantity with 
        csv quantity field data like 2 quantity in line, and csv have 3 quantity then 
        it will update line with 5 quantity. 
    """)
    delimiter = fields.Selection([('tab', 'Tab'), ('semicolon', 'Semicolon'), ('colon', 'Colon')],
                                 "Seperator", default="colon")

    @api.multi
    def download_sample_product_csv(self):
        """
        Download Sample file for Inbound Shipment Plan Products Import
        Added by Keyur
        :return: Dict
        """
        attachment = self.env['ir.attachment'].search([('name', '=', 'inbound_shipment_plan_sample.csv')])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
            'nodestroy': False,
        }

    @api.multi
    def default_get(self, fields):
        res = super(import_product_inbound_shipment, self).default_get(fields)
        res['shipment_id'] = self._context.get('shipment_id', False)
        return res

    @api.multi
    def wizard_view(self):
        view = self.env.ref('amazon_ept.view_inbound_product_import_wizard')

        return {
            'name': 'Import Product',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.product.inbound.shipment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }

    @api.one
    def get_file_name(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        return '/tmp/inbount_shipment_%s_%s.csv' % (self.env.uid, name)

    @api.one
    def get_reimportable_file_name(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        return '/tmp/reimport_inbount_shipment_%s_%s.csv' % (self.env.uid, name)

    @api.one
    def read_file(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        '''
            Read selected file to import order and return Reader to the caller
        '''
        imp_file = StringIO(base64.decodestring(self.choose_file).decode('utf-8'))
        new_file_name = self.get_file_name(name=name)[0]
        #         open(new_file_name,'wb')
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
    def validate_process(self):
        '''
            Validate process by checking all the conditions and return back with inbound shipment object
        '''
        shipment_obj = self.env['inbound.shipment.plan.ept']
        shipments = []
        for shipment in shipment_obj.browse(self.env.context.get('active_ids')):
            if shipment.state != "draft":
                raise except_orm(('Unable to process..!'),
                                 ('You can process with only draft shipment plan!.'))
            shipments.append(shipment)

        if len(shipment) > 1:
            raise except_orm(('Unable to process..!'),
                             ('You can process only one shipment plan at a time!.'))

        shipment_plan = shipments[0]
        if not shipment_plan:
            raise except_orm(('Unable to process..!'), ('Shipment Plan is not found!!!.'))

        if not self.choose_file:
            raise except_orm(('Unable to process..!'), ('Please select file to process...'))

        return shipment_plan

    @api.one
    def validate_fields(self, fieldname):
        '''
            This import pattern requires few fields default, so check it first whether it's there or not.
        '''
        require_fields = ['default_code', 'quantity', 'quantity_in_case']
        missing = []
        for field in require_fields:
            if field not in fieldname:
                missing.append(field)

        if len(missing) > 0:
            raise except_orm(('Incorrect format found..!'), (
                    'Please provide all the required fields in file, missing fields => %s.' % (
            missing)))

        return True

    def fill_dictionary_from_file(self, reader):
        order_data = []
        for row in reader:
            vals = {
                'default_code': row.get('default_code', False),
                'quantity': row.get('quantity', 0.0),
                'quantity_in_case': row.get('quantity_in_case', 0.0)
            }
            order_data.append(vals)
        return order_data

    def find_invalid_sku_list(self, product_data, shipment_plan):
        product_obj = self.env['product.product']
        invalid_data = []
        for data in product_data:
            line_data = {}
            message = ''
            line_data.update({
                'default_code': data.get('default_code', ''),
                'quantity': data.get('quantity', 0.0),
                'quantity_in_case': data.get('quantity_in_case', 0.0)
            })
            default_code = data.get('default_code', '')
            if not default_code:
                message = 'Product code not found!!!'
                line_data.update({'error': str(message)})
                invalid_data.append(line_data)
                continue

            default_code = default_code.strip()
            quantity = data.get('quantity') and float(data.get('quantity', 0.0)) or 0.0
            product = product_obj.search([('default_code', '=', default_code)])
            if not product:
                message = 'Invalid product code!!!'
                line_data.update({'error': str(message)})
                invalid_data.append(line_data)
                continue

            product_domain = [('product_id', '=', product.id),
                              ('instance_id', '=', shipment_plan.instance_id.id),
                              ('fulfillment_by', '=', 'AFN')]
            amazon_product_id = self.env['amazon.product.ept'].search(product_domain)
            if not amazon_product_id:
                message = 'Product not found for that amazon instance!!!'
                line_data.update({'Error': str(message)})
                invalid_data.append(line_data)
                continue

            if quantity <= 0:
                message = 'Invalid product quantity!!!'
                line_data.update({'error': str(message)})
                invalid_data.append(line_data)
                continue

        return invalid_data

    @api.multi
    def import_shipment_line(self):
        product_obj = self.env['product.product']
        line_obj = self.env['inbound.shipment.plan.line']
        shipment_plan = self.validate_process()[0]

        current_date = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')

        reader = self.read_file(name=current_date)[0]
        fieldname = reader.fieldnames

        if self.validate_fields(fieldname):
            product_data = self.fill_dictionary_from_file(reader)
            invalid_data = self.find_invalid_sku_list(product_data, shipment_plan)
            if len(invalid_data) > 0:
                msg = ""
                for err in invalid_data:
                    msg += str(list(err.values())) + "\n"
                raise except_orm(('Invalid data found..!'),
                                 ('Please correct data first and then import file. \n%s.' % (msg)))

            for data in product_data:
                line_data = {}
                line_data.update({
                    'default_code': data.get('default_code', ''),
                    'quantity': data.get('quantity', 0.0),
                    'quantity_in_case': data.get('quantity_in_case', 0.0)
                })

                default_code = data.get('default_code', '').strip()
                quantity = data.get('quantity') and float(data.get('quantity', 0.0)) or 0.0
                quantity_in_case = data.get('quantity_in_case') and float(
                    data.get('quantity_in_case', 0.0))

                product = product_obj.search([('default_code', '=', default_code)])
                product_domain = [('product_id', '=', product.id),
                                  ('instance_id', '=', shipment_plan.instance_id.id),
                                  ('fulfillment_by', '=', 'AFN')]
                amazon_product_id = self.env['amazon.product.ept'].search(product_domain, limit=1)
                domain = [('amazon_product_id', '=', amazon_product_id.id),
                          ('shipment_plan_id', '=', shipment_plan.id)]
                shipment_plan_line_obj = line_obj.search(domain)

                try:
                    if not shipment_plan_line_obj:
                        dict_data = {
                            'shipment_plan_id': shipment_plan.id,
                            'amazon_product_id': amazon_product_id.id,
                            'quantity': quantity,
                            'quantity_in_case': quantity_in_case
                        }
                        shipment_plan_line_obj.create(dict_data)
                    else:
                        if not self.update_existing:
                            continue

                        if self.replace_product_qty:
                            qty = quantity
                        else:
                            qty = shipment_plan_line_obj.quantity + quantity
                        shipment_plan_line_obj.write({'quantity': qty})
                except Exception as e:
                    raise except_orm(('Unable to process ..!'),
                                     ('Error found while importing products => %s.' % (str(e))))

        return {'type': 'ir.actions.act_window_close'}
