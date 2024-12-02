from odoo import models, fields, api, _
import base64
import requests
import xlrd
from odoo.tools import mute_logger, pycompat
import io
import threading
import odoo


class ImportReturn(models.TransientModel):
    _name = "import.return.wizard"
    _description = "import Return Wizard "

    file_name = fields.Binary(string="File Name")
    samples_file = fields.Binary(string="Samples Import Format",readonly=False)
    samples_file_name = fields.Char(string="Samples Import name", readonly=True)

    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        active_id = self._context.get('active_id', False)
        sample_file = self.env['attachment.sample.file'].search([
            ('shop_id', '=', active_id),
            ('file_type', '=', 'return')
        ], limit=1)
        if sample_file:
            values.update({
                'samples_file':sample_file.file,
                'samples_file_name':sample_file.file_name
            })
        return values

    def import_return(self):
        def split_list(alist, wanted_parts=1):
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

        data = []
        header = []
        count = 0
        csv_data = base64.decodebytes(self.file_name)
        reader = pycompat.csv_reader(io.BytesIO(csv_data), delimiter=',', quotechar='"')
        for i in reader:
            if count == 7:
                header.append(i)
            elif count > 7:
                data.append(i)
            count += 1
        # print("header", header)
        # print("data", data)
        if len(data) and len(data) > 0:
            split_ids = data
            calculation_list = []
            split_ids = [ele for ele in split_ids if ele != []]

            A_calculation = threading.Thread(target=self._run_process, args=(self.id, split_ids, header))
            A_calculation.start()
        return {}

    def _run_process(self, active_id, list_of_ids, header):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        head_dict = {}
        count = 0
        vals = {}
        order_line_obj = self.env['stock.return.picking']
        for he in header:
            for h in he:
                head_dict[h] = count
                count += 1
        for re in list_of_ids:
            sale_nu = self.env['sale.order'].search([('sub_order_no', '=', re[head_dict['Order Number']])])
            # print("sale_nu", sale_nu)
            if sale_nu:
                pc = self.env['stock.picking'].search(
                    [('picking_type_code', '=', 'outgoing'), ('sale_id', '=', sale_nu.id), ('state', '=', 'done')],limit=1)
                # print("pc",pc)
                att_pro = self.env['product.template.attribute.value'].search(
                    [('attribute_id.name', '=', 'Size'),
                     ('product_attribute_value_id.name', '=', re[head_dict['Size']])])
                product = self.env['product.product'].search(
                    [('default_code', '=', re[head_dict['SKU']]),
                     ('product_template_variant_value_ids', 'in', att_pro.ids)])
                vals = {
                    'picking_id': pc.id,
                    'product_return_moves': [(0, 0, {
                        'product_id': product.id,
                        'quantity': re[head_dict['Qty']],
                    })]
                }
                # print("vals", vals)
                order_line_new = order_line_obj.new(vals)
                order_line_new._onchange_picking_id()
                order_line_values = order_line_new._convert_to_write(order_line_new._cache)
                return_id = order_line_obj.create(order_line_values)
                return_id.create_returns()

        new_cr.commit()
        new_cr.close()
        return {}
