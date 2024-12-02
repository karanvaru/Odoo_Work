from odoo import models, fields, api, _
import base64
import requests
import xlrd
import io
from odoo.exceptions import ValidationError
from datetime import datetime
import threading
import odoo
import logging

_logger = logging.getLogger(__name__)


class ImportSale(models.Model):
    _name = "import.sale.wizard"
    _description = "Imort Sale Wizard"
    _rec_name='shop_id'

    file_name = fields.Binary(
        string="File Name"
    )
    shop_id = fields.Many2one(
        'sale.shop',
        string="Shop",

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
    #         ('file_type', '=', 'sale')
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
            ('file_type', '=', 'sale_order')
        ], limit=1)
        if lines_id.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=ir.attachment&id=" + str(
                    lines_id.attachment_id.id)+ "&filename_field=name&field=datas&download=true&name=" + lines_id.attachment_id.name
            }
#     @api.model
#     def default_get(self, fields):
#         rec = super(ImportSale, self).default_get(fields)
#         active_id = self._context.get('active_id', False)
#         shop_id = self.env['sale.shop'].browse(active_id)
#         sale_file = shop_id.sample_attachment_ids.filtered(lambda l: l.file_type == 'sale_order').file
#         rec.update({
#             'shop_id': shop_id,
#             'samples_file':sale_file
#         })
#         return rec

    def import_sale(self):
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
        if not self.shop_id.branch_id.state_id:
            raise ValidationError("Please Configure state on Branch")
        data = []
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        for i in range(number_of_rows):
            data.append(sheet.row_values(i))
        if len(data) and len(data) > 0:
            split_ids = data
            calculation_list = []
            split_ids = [ele for ele in split_ids if ele != []]

            A_calculation = threading.Thread(target=self._run_process, args=(self.id, split_ids, number_of_rows))
            A_calculation.start()
        return {}

    def _run_process(self, active_id, split_ids, number_of_rows):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        fail_orders = []
        fail_count = 0
        success_count = 0
        for row in range(number_of_rows):
            if row > 2:
                rec = split_ids[row]
                _logger.info("Read File____________")
                state_id = self.env['res.country.state'].search([('name', 'ilike', rec[7])], limit=1)
                if self.shop_id.shop_as_customer:
                    partner_id = self.shop_id.shop_customer_id
                if not self.shop_id.shop_customer_id:
                    partner_id = self.env['res.partner'].create({
                        'name': rec[5],
                        'street': rec[6],
                        'state_id': state_id.id,
                        'branch_id': self.shop_id.branch_id.id,
                    })
                date_order = datetime.strptime(rec[4], "%d %b, %Y")
                shop_product = self.env['sale.shop.product'].search(
                    [('default_code', '=', rec[9]), ('shop_id', '=', self.shop_id.id)])
                product = shop_product.product_id
                _logger.info("Search Base Product____________")
                product_devliery = self.env['product.product'].search([('default_code', '=', 'delivery')], limit=1)
                if not product_devliery:
                    product_devliery = self.env['product.product'].create({
                        'name': 'Delivery',
                        'default_code': 'delivery',
                        'detailed_type': 'service'
                    })
                if not product:
                    fail_orders.append(rec)
                    fail_count += 1
                    continue
                tax_code = str(rec[17])
                if '.0' in tax_code:
                    tax_code = tax_code[:-2]
                tag_id = self.env['account.tax.tag'].search(
                    [('name', '=', tax_code), ('tax_id.type_tax_use', '=', 'sale')], limit=1)
                if rec[7].lower() != rec[26].lower():
                    if tag_id.tax_id.alternate_tax_id:
                        tax_id = tag_id.tax_id.alternate_tax_id
                        _logger.info("Set IGST____________")
                    else:
                        igst_grp_id = self.env['account.tax.group'].sudo().search([('name', '=', 'IGST')]).id
                        tax_tag_id = self.env['account.tax.tag'].search(
                            [('name', '=', tax_code), ('tax_id.type_tax_use', '=', 'sale'),
                             ('tax_id.tax_group_id', '=', igst_grp_id)], limit=1)
                        tax_id = tax_tag_id.tax_id
                        _logger.info("Set IGST____________")
                else:
                    tax_id = tag_id.tax_id
                    _logger.info("Set GST____________")

                # igst_grp_id = self.env['account.tax.group'].sudo().search([('name', '=', 'IGST')]).id
                # if rec[7].lower() != rec[26].lower():
                #     tag_id = self.env['account.tax.tag'].search(
                #         [('name', '=', tax_code), ('tax_id.type_tax_use', '=', 'sale'),
                #          ('tax_id.tax_group_id', '=', igst_grp_id)], limit=1)
                #     tax_id = tag_id.tax_id
                #     _logger.info("Set IGST____________")
                # else:
                #     tag_id = self.env['account.tax.tag'].search(
                #         [('name', '=', tax_code), ('tax_id.type_tax_use', '=', 'sale'),
                #          ('tax_id.tax_group_id', '!=', igst_grp_id)], limit=1)
                #     tax_id = tag_id.tax_id
                #     _logger.info("Set GST____________")

                dis = 0
                if rec[14]:
                    dis = round((100 * rec[14]) / rec[12], 2)
                emp_code = str(rec[2])
                if '.0' in emp_code:
                    emp_code = emp_code[:-2]
                number = emp_code.split('_')
                sub = number[0]

                sale_nu = self.env['sale.order'].search([('sub_order_no', '=', sub)])
                _logger.info("Search with order.no of Sale order ____________")
                if sale_nu:
                    if rec[1] == 'Cancelled':
                        sale_nu.cancelled_action()
                        sale_nu.picking_ids.filtered(
                            lambda line: line.picking_type_code == 'outgoing').action_cancel_request()
                        out_picking_id = sale_nu.picking_ids.filtered(lambda line: line.picking_type_code == 'outgoing')
                        if out_picking_id:
                            out_picking_id.message_post(body="order has been cancelled")
                    lines_vals = {
                        'order_line': [(0, 0, {'name': product.name,
                                               'product_id': product.id,
                                               'product_uom_qty': rec[11],
                                               'price_unit': rec[12],
                                               'discount': dis,
                                               'tax_id': tax_id and [(4, tax_id.id)] or []
                                               }),
                                       ]
                    }
                    try:
                        if rec[0] != 'Credit Invoice':
                            sale_nu.write(lines_vals)
                            success_count += 1
                            _logger.info("Update Sale Order____________")
                        else:
                            for out_picking_id in sorted(sale_nu.picking_ids, key=lambda sub_line: sub_line['id']):
                                wizard_id = self.env['stock.immediate.transfer'].with_context({'button_validate_picking_ids':out_picking_id.ids}).create({
                                    'pick_ids': [(6, 0, out_picking_id.ids)],
                                    'immediate_transfer_line_ids':[(0, 0, {'picking_id':out_picking_id.id,'to_immediate':True})]

                                })
                                wizard_id.process()
                            retu_vals = {
                                'order_id': sale_nu.id,
                                'type': 'return'
                            }
                            ticket_id = self.env['shop.order.ticket'].create(retu_vals)
                            sale_nu.update({
                                'is_return': True,
                                'request_id': ticket_id.id,
                            })


                    except:
                        fail_orders.append(rec)
                        fail_count += 1
                    sale = sale_nu
                else:
                    vals = {
                        'partner_id': partner_id.id,
                        'date_order': date_order,
                        'sub_order_no': sub,
                        'sales_shop_id': self.shop_id.id,
                        'branch_id':self.shop_id.branch_id.id,
                        'warehouse_id':self.shop_id.default_warehouse_id.id,
                        'order_state_id': partner_id.state_id.id,
                        'order_address': rec[6],
                        'order_line': [(0, 0, {'name': product.name,
                                               'product_id': product.id,
                                               'product_uom_qty': rec[11],
                                               'price_unit': rec[12],
                                               'tax_id': tax_id and [(4, tax_id.id)] or [],
                                               'discount': dis
                                               }), (0, 0, {'name': product_devliery.name,
                                                           'product_id': product_devliery.id,
                                                           'product_uom_qty': 1,
                                                           'price_unit': rec[16],
                                                           'tax_id': tax_id and [(4, tax_id.id)] or []
                                                           })]
                    }
                    sale = False
                    try:
                        sale = self.env['sale.order'].sudo().create(vals)
                        _logger.info("create Sale Order____________")
                        sale.sudo().action_confirm()
                        success_count += 1
                        _logger.info("Sale Order Imported :%s  And Order Number: %s" % (sale.name, sub))
                    except:
                        fail_orders.append(rec)
                        fail_count += 1
                        _logger.info("Sale Order Fail to Import :%s" % (rec))
                    if rec[1] == 'Cancelled':
                        if sale:
                            sale.cancelled_action()
                    elif rec[0] == 'Credit Invoice':
                        _logger.info("Return Flag True____________")
                        if sale:
                            for out_picking_id in sorted(sale.picking_ids, key=lambda sub_line: sub_line['id']):
                                wizard_id = self.env['stock.immediate.transfer'].with_context(
                                    {'button_validate_picking_ids': out_picking_id.ids}).create({
                                    'pick_ids': [(6, 0, out_picking_id.ids)],
                                    'immediate_transfer_line_ids': [
                                        (0, 0, {'picking_id': out_picking_id.id, 'to_immediate': True})]

                                })
                                wizard_id.process()
                            retu_vals = {
                                'order_id': sale.id,
                                'type': 'return'
                            }
                            ticket_id = self.env['shop.order.ticket'].create(retu_vals)
                            sale.update({
                                'is_return': True,
                                'request_id': ticket_id.id,
                            })

        wizard_id = self.env['import.sale.wizard'].browse(active_id)
        wizard_id.update({
            'success_count': success_count,
            'failed_count': fail_count,
            'failed_order': fail_orders,
            'user_id': self.env.user,
            'upload_date': datetime.today(),

        })
        new_cr.commit()
        template_id = self.env.ref('mtrmp_sales_shop.import_sale_order_confirmation_email')
        if template_id:
            template = self.env['mail.template'].browse(template_id).id
            template.send_mail(wizard_id.id, force_send=True)
        new_cr.commit()
        new_cr.close()
        return {}
