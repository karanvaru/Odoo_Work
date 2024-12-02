from odoo import models, fields, api, _
import base64
import requests
import xlrd
from odoo.tools import mute_logger, pycompat
import io
from odoo.exceptions import ValidationError
import threading
import odoo
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ImportAWB(models.Model):
    _name = "import.awb.wizard"
    _description = "Import AWB Wizard"

    _rec_name='shop_id'

    shop_id = fields.Many2one(
        'sale.shop',
        string="Shop",
    )

    file_name = fields.Binary(
        string="File Name"
    )
    failed_count = fields.Integer(
        string="Fail Count"
    )
    success_count = fields.Integer(
        string="Success Count"
    )
    failed_order = fields.Text(
        string="Fail Order"
    )
    user_id = fields.Many2one(
        'res.users',
        string="Upload By User"
    )
    upload_date = fields.Datetime(
        string="Upload Date"
    )
    # samples_file = fields.Binary(
    #     string="Samples Import Format",
    #     readonly=False,
    # )
    # samples_file_name = fields.Char(
    #     string="Samples Import name",
    #     readonly=True,
    # )

    # @api.model
    # def default_get(self, default_fields):
    #     values = super().default_get(default_fields)
    #     active_id = self._context.get('active_id', False)
    #     sample_file = self.env['attachment.sample.file'].search([
    #         ('shop_id', '=', active_id),
    #         ('file_type', '=', 'awb')
    #     ], limit=1)
    #     if sample_file:
    #         values.update({
    #             'samples_file':sample_file.file,
    #             'samples_file_name':sample_file.file_name
    #         })
    #     return values

    def download_sample(self):
        self.ensure_one()
        lines_id = self.env['attachment.sample.file'].search([
            ('shop_id', '=', self.shop_id.id),
            ('file_type', '=', 'awb')
        ], limit=1)
        if lines_id.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=ir.attachment&id=" + str(
                    lines_id.attachment_id.id)+ "&filename_field=name&field=datas&download=true&name=" + lines_id.attachment_id.name
            }
    def import_Awb(self):
        def split_list(alist, wanted_parts=1):
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.file_name)
            )
            _logger.info("Upload File____________")
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        data = []
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        for row in range(number_of_rows):
            data.append(sheet.row_values(row))
        if len(data) and len(data) > 0:
            split_ids = data
            calculation_list = []
            split_ids = [ele for ele in split_ids if ele != []]
            A_calculation = threading.Thread(target=self._run_process, args=(self.id, split_ids, number_of_rows))
            A_calculation.start()
        return {}

    def _run_process(self, active_id, list_of_ids, number_of_rows):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        head_dict = {}
        fail_orders = []
        fail_count = 0
        success_count = 0
        for row in range(number_of_rows):
            rec = list_of_ids[row]
            _logger.info("Read File____________")
            if row == 0:
                for h in rec:
                    head_dict[h] = {'Count': rec.index(h)}
            elif row > 0:
                emp_code = str(rec[head_dict['Sub Order No.']['Count']])
                if '.0' in emp_code:
                    emp_code = emp_code[:-2]
                number = emp_code.split('_')
                sub = number[0]
                sale_nu = self.env['sale.order'].search(
                    [('sub_order_no', '=', sub), ('sales_shop_id', '=', self.shop_id.id)])
                # print("sale_nu_____",sale_nu,sub)
                _logger.info("Search  File____________")
                if sale_nu:
                    out_picking_id = sale_nu.picking_ids.filtered(lambda line: line.picking_type_code == 'outgoing')
                    _logger.info("Search outgoing Picking____________")
                    carrier_id = self.env['delivery.carrier'].search(
                        [('name', '=', rec[head_dict['Delivery Partner']['Count']])], limit=1)
                    if not carrier_id:
                        product_devliery = self.env['product.product'].search([('default_code', '=', 'delivery')],
                                                                              limit=1)
                        if not product_devliery:
                            product_devliery = self.env['product.product'].create({
                                'name': 'Delivery',
                                'default_code': 'delivery'
                            })
                        vals = {
                            'name': rec[head_dict['Delivery Partner']['Count']],
                            'product_id': product_devliery.id,
                            'delivery_type': 'fixed'
                        }
                        carrier_id = self.env['delivery.carrier'].create(vals)
                        _logger.info("Create Delivery Carrier____________")
                    try:
                        out_picking_id.update({
                            'carrier_tracking_ref': rec[head_dict['AWB']['Count']],
                            'carrier_id': carrier_id.id
                        })
                        _logger.info("Set AEB Number____________")
                        success_count += 1
                        new_cr.commit()
                        _logger.info("Import AWB no :%s  And Order Number: %s" % (rec[head_dict['AWB']['Count']], sub))
                    except:
                        fail_orders.append(rec)
                        fail_count += 1
                else:
                    fail_orders.append(rec)
                    fail_count += 1
                    continue
        wizard_id = self.env['import.awb.wizard'].browse(active_id)
        wizard_id.update({
            'success_count': success_count,
            'failed_count': fail_count,
            'failed_order': fail_orders,
            'user_id': self.env.user,
            'upload_date': datetime.today(),

        })
        new_cr.commit()
        template_id = self.env.ref('mtrmp_sales_shop.import_awb_wizard_confirmation_email')
        if template_id:
            template = self.env['mail.template'].browse(template_id).id
            template.send_mail(wizard_id.id, force_send=True)
        new_cr.commit()
        new_cr.close()
        return {}
