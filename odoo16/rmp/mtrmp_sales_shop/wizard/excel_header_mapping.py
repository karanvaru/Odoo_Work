from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import threading
import odoo
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ExcelHeaderMapping(models.TransientModel):
    _name = "excel.header.mapping.wizard"
    _description = "Excel Header Mapping Wizard"
    lines_ids = fields.One2many('fields.mapping.wizard', 'execl_header_lines_id')
    shop_id = fields.Many2one('sale.shop', string="Shop")

    def get_fail_log_message(self, code):
        return f"System can't able to find product with {code} SKU"

    def upload_product(self):

        # print(S)
        def split_list(alist, wanted_parts=1):
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

        context = self._context
        data = context.get('data')
        wiz_id = context.get('product_wizard_id')
        self._run_process(wiz_id,data)
        # if len(data) and len(data) > 0:
        #     split_ids = data
        #     calculation_list = []
        #     split_ids = [ele for ele in split_ids if ele != []]
        #
        #     A_calculation = threading.Thread(target=self._run_process,
        #                                      args=(self.id, split_ids))
        #     A_calculation.start()

        return {}

    def product_import_process(self):
        line_ids = self.lines_ids

    def _run_process(self, active_id, product_data):
        run_context = self._context
        # print("run_context",run_context)
        ex_wizard_id = run_context.get('product_wizard_id')
        log_id = int(run_context.get('log_id'))
        # print("ex_wizard_id",ex_wizard_id)
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        config_lines = self.lines_ids
        # config_lines = self.env['fields.mapping.wizard'].sudo().search(
        #     [('execl_header_lines_id', '=', active_id)])
        all_shop_products = []
        for data in product_data:
            shop_product = {'shop_id' :  self.shop_id.id}
            for record in data:
                excel_head = record
                field_name = self.lines_ids.filtered(lambda l: l.excel_head == excel_head).field_id.name
                if field_name:
                    shop_product.update({field_name : data.get(excel_head)})
            all_shop_products.append(shop_product)

        for shop_product in all_shop_products:
            default_code = shop_product.get('default_code')
            master_code = shop_product.get('master_code')
            self._cr.commit()
            if master_code:
                shop_product_id = self.env['sale.shop.product'].search([('shop_id','=',self.shop_id.id),
                                                                         ('default_code','=',default_code)])
                if shop_product_id:
                    shop_product_id.write(shop_product)
                else:
                    product = master_code and self.env['product.product'].search([('default_code', '=', master_code)], limit=1) or \
                              self.env['product.product']
                    if product:
                        shop_product.update({'product_id': product.id,
                                             'product_tmpl_id': product.product_tmpl_id.id})
                        shop_product_id = self.env['sale.shop.product'].create(shop_product)
                        self._cr.commit()
                    if not product:
                        # check configuration for shop
                        if self.shop_id.create_prod:
                            # create product of not found
                            product = self.env['product.product'].create({
                                'name': shop_product.get('name'),
                                'default_code': master_code,
                                'detailed_type': 'product',
                                'categ_id' : self.shop_id.default_category_id.id
                            })
                            shop_product.update({'product_id': product.id,
                                                 'product_tmpl_id': product.product_tmpl_id.id})
                            self.env['sale.shop.product'].create(shop_product)
                        else:
                            # ToDo: Need to create log for this
                            message = self.get_fail_log_message(default_code)
                            check_log_line = self.env['shop.fail.log.lines'].search([('message', '=', message)], limit=1)
                            if check_log_line:
                                check_log_line.write({
                                    # 'operation': 'import_products',
                                    'message': message,
                                    'is_mismatch': True,
                                    'shop_log_id' : log_id
                                })
                                self._cr.commit()
                            else:
                                fail_line = self.env['shop.fail.log.lines'].create({
                                    'operation' : 'import_products',
                                    'message' : message,
                                    'is_mismatch' : True,
                                    'shop_log_id' : log_id
                                })
                                self._cr.commit()
                                continue
        return {}
        # tem = config_lines.filtered(lambda l: l.field_id.name == 'name').excel_head
        # tem = config_lines.filtered(lambda l: l.field_id.name == 'product_tmpl_id').excel_head
        # uom = config_lines.filtered(lambda l: l.field_id.name == 'uom_id').excel_head
        # sale_price = config_lines.filtered(lambda l: l.field_id.name == 'list_price').excel_head
        # hsn_code = config_lines.filtered(lambda l: l.field_id.name == 'l10n_in_hsn_code').excel_head
        # taxes_id = config_lines.filtered(lambda l: l.field_id.name == 'taxes_id').excel_head
        # category = config_lines.filtered(lambda l: l.field_id.name == 'product_public_category_id').excel_head
        # field_map_dict = {}
        # fail_orders = []
        # fail_count = 0
        # success_count = 0
        # count = 0
        # for h in config_lines:
        #     if h.excel_head == uom:
        #         field_map_dict[h.excel_head] = {'count': count}
        #     if h.excel_head == sale_price:
        #         field_map_dict[h.excel_head] = {'count': count}
        #     if h.excel_head == tem:
        #         field_map_dict[h.excel_head] = {'count': count}
        #     if h.excel_head == hsn_code:
        #         field_map_dict[h.excel_head] = {'count': count}
        #     if h.field_id.id != 0:
        #         field_map_dict[h.excel_head] = {'id': h.field_id}
        #         field_map_dict[h.excel_head].update({'count': count})
        #     count += 1
        # var_dict = {}
        # index = 0
        # for i in field_map_dict:
        #     if i == tem:
        #         for j in field_map_dict[i]:
        #             index = field_map_dict[i][j]
        # for row in list_of_ids:
        #     if row[index] not in var_dict:
        #         var_dict[row[index]] = []
        #     tem_dict = {}
        #     for i in field_map_dict:
        #         if i != tem:
        #             for j in field_map_dict[i]:
        #                 if j == 'count':
        #                     tem_dict[i] = row[field_map_dict[i][j]]
        #     var_dict[row[index]].append(tem_dict)
        # relational_fields = ['many2one', 'many2many']
        # valList = []
        # resultt = self.shop_id
        # _logger.info("Template creation Stared____________")
        # for rec in var_dict:
        #     produt_temp = self.env['product.template'].search([('name', '=', rec)])
        #     for res in var_dict[rec]:
        #         vals = {}
        #         pro = 0
        #         for re in list(res.keys()):
        #             if produt_temp:
        #                 pro = produt_temp[0].product_variant_id
        #                 res.update({'product_id': pro.id})
        #             else:
        #                 try:
        #                     uom_id = self.env['uom.uom'].search([('name', '=', res[uom])], limit=1)
        #                     # product_categ_id = self.env['product.category'].search([('name', '=', res[category])],limit=1)
        #                     if self.shop_id.default_category_id:
        #                         product_categ_id = self.shop_id.default_category_id.id
        #                     else:
        #                         product_categ_id = self.env.ref('mtrmp_sales_shop.record_category_unmapped').id
        #
        #                     tag_id = self.env['account.tax.tag'].search(
        #                         [('name', '=', res[taxes_id]), ('tax_id.type_tax_use', '=', 'sale')], limit=1)
        #                     taxe_id = tag_id.tax_id
        #                     produt_temp = self.env['product.template'].create({
        #                         'name': rec,
        #                         'detailed_type': 'product',
        #                         'list_price': res[sale_price],
        #                         'uom_id': uom_id.id,
        #                         'categ_id': product_categ_id,
        #                         'uom_po_id': uom_id.id,
        #                         'l10n_in_hsn_code': res[hsn_code],
        #                         'taxes_id': [(4, taxe_id.id)]
        #                     })
        #                 except:
        #                     template_id = self.env.ref('mtrmp_sales_shop.import_issue_email_temp')
        #                     if template_id:
        #                         template = self.env['mail.template'].browse(template_id).id
        #                         email_values = {
        #                             'message': 'Create Template  Issue'
        #                         }
        #                         template.with_context(email_values).send_mail(ex_wizard_id, force_send=True,
        #                                                                       email_values=None)
        #                     new_cr.commit()
        #                     return
        #                 pro = produt_temp.product_variant_id
        #                 res.update({'product_id': pro.id})
        #         if pro:
        #             vals.update({'product_id': pro.id})
        #         for re in list(res.keys()):
        #             for i in field_map_dict:
        #                 if i == re:
        #                     for j in field_map_dict[i]:
        #                         if j == 'id':
        #                             values = field_map_dict[i][j]
        #                         else:
        #                             if values.ttype not in relational_fields:
        #                                 if values.name == 'default_code':
        #                                     vals.update({'default_code': res[re]})
        #                                 if res[re] == 0:
        #                                     vals.update({values.name: res[re] + 0.01})
        #                                 else:
        #                                     vals.update({values.name: res[re]})
        #                             elif values.ttype == 'many2one' and values.name == 'product_public_category_id':
        #                                 ref_id = self.env[values.relation].search([('name', '=', res[re])])
        #                                 vals.update({'product_category': res[re]})
        #                                 if not ref_id:
        #                                     ref_id = self.env['product.public.category'].create({
        #                                         'name': res[re]
        #                                     })
        #                                 if len(ref_id) > 1:
        #                                     ref = self.env.ref('mtrmp_sales_shop.record_public_category_unmapped')
        #                                     vals.update({values.name: ref.id})
        #                                 else:
        #                                     vals.update({values.name: ref_id.id})
        #                                 resultt.write({
        #                                     'category_ids': [(4, ref_id.id)],
        #                                 })
        #                             elif values.ttype == 'many2one':
        #                                 ref_id = self.env[values.relation].search([('name', '=', res[re])],
        #                                                                           limit=1)
        #                                 if ref_id:
        #                                     vals.update({values.name: ref_id.id})
        #                             elif values.ttype == 'many2many':
        #                                 # print(res[re])
        #                                 tag_id = self.env['account.tax.tag'].search([('name', '=', res[re])], limit=1)
        #                                 ref_m2m_id = tag_id.tax_id
        #                                 if ref_m2m_id:
        #                                     vals.update({values.name: [(4, ref_m2m_id.id)]})
        #         vals.update({'shop_id': resultt.id})
        #         valList.append(vals)
        # _logger.info("Shop product creation Stared____________")
        # for i in valList:
        #     for j in i:
        #         if j == 'default_code':
        #             shop_id = self.env['sale.shop'].browse(i.get('shop_id'))
        #             ress = self.env['sale.shop.product'].search(
        #                 [('default_code', '=', i.get('default_code')), ('shop_id', '=', shop_id.id)], limit=1)
        #             if ress:
        #                 try:
        #                     ress.write(i)
        #                     success_count += 1
        #                     _logger.info("Update Shop Product____________")
        #                 except:
        #                     fail_orders.append(i)
        #                     fail_count += 1
        #                 shop_product_id = ress
        #             else:
        #                 try:
        #                     shop_product_id = self.env['sale.shop.product'].create(i)
        #                     _logger.info("Create Shop Product____________")
        #                     success_count += 1
        #                 except:
        #                     fail_orders.append(i)
        #                     fail_count += 1
        #             new_cr.commit()
        #             _logger.info("product Imported : %s" % (i['default_code']))
        #
        # new_cr.execute(
        #     "update import_product_wizard SET user_id = %s ,upload_date = '%s', success_count = %s , failed_count= %s ,failed_order='%s' where id = %s" % (
        #         self.env.user.id, fields.Datetime.now(), success_count, fail_count, fail_orders, ex_wizard_id))
        # new_cr.commit()
        # template_id = self.env.ref('mtrmp_sales_shop.import_products_confirmations_emails')
        # if template_id:
        #     template = self.env['mail.template'].browse(template_id).id
        #     template.send_mail(ex_wizard_id, force_send=True)
        # new_cr.commit()
        # new_cr.close()
        # return {}



    def _run_run_process(self, active_id, list_of_ids):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        config_lines = self.env['fields.mapping.wizard'].sudo().search(
            [('execl_header_lines_id', '=', active_id)])

        field_map_dict = {}

        count = 0
        for h in config_lines:
            if h.excel_head == 'Size':
                field_map_dict[h.excel_head] = {'count': count}
            if h.excel_head == 'Base Product Name':
                field_map_dict[h.excel_head] = {'count': count}
            if h.field_id.id != 0:
                field_map_dict[h.excel_head] = {'id': h.field_id}
                field_map_dict[h.excel_head].update({'count': count})
            count += 1
        var_dict = {}
        index = 0

        for i in field_map_dict:
            if i == 'Base Product Name':
                for j in field_map_dict[i]:
                    index = field_map_dict[i][j]
        for row in list_of_ids:
            if row[index] not in var_dict:
                var_dict[row[index]] = []
            tem_dict = {}
            for i in field_map_dict:
                if i != 'Base Product Name':
                    for j in field_map_dict[i]:
                        if j == 'count':
                            tem_dict[i] = row[field_map_dict[i][j]]
            var_dict[row[index]].append(tem_dict)

        attribute_ids = self.env['product.attribute'].search([])
        attribute_dict = {}
        for attribute in attribute_ids:
            attribute_dict[attribute.name] = attribute

        relational_fields = ['many2one']
        valList = []
        resultt = self.shop_id
        product_template_ids = self.env['product.template']
        # print("var_dict",var_dict)
        for rec in var_dict:
            # print("rec",rec)
            produt_temp = self.env['product.template'].search([('name', '=', rec)])
            for res in var_dict[rec]:
                vals = {}
                pro = 0
                if produt_temp:
                    for re in list(res.keys()):
                        if re == 'Size':
                            attribute = attribute_dict[re] if re in list(attribute_dict.keys()) else False
                            if not attribute:
                                attribute = self.env['product.attribute'].create({'name': re})
                                attribute_dict[attribute.name] = attribute
                            result_value = self.env['product.attribute.value'].search(
                                [('name', '=', res[re]), ('attribute_id', '=', attribute.id)])
                            if not result_value:
                                result_value = self.env['product.attribute.value'].create(
                                    {'name': res[re], 'attribute_id': attribute.id})
                            exist_attribute_line = produt_temp.attribute_line_ids.filtered(
                                lambda i: i.attribute_id == attribute
                            )
                            if exist_attribute_line:
                                exist_value_line = produt_temp.attribute_line_ids.filtered(
                                    lambda i: i.attribute_id == attribute and result_value in i.value_ids
                                )
                                if not exist_value_line:
                                    exist_attribute_line.write({
                                        'value_ids': [(4, result_value.id)]
                                    })
                            else:
                                produt_temp.write({
                                    'attribute_line_ids': [(0, 0, {
                                        'attribute_id': attribute.id,
                                        'value_ids': [(4, result_value.id)]
                                    })]
                                })
                            pro = self.env['product.product'].search(
                                [(
                                    'product_template_variant_value_ids.product_attribute_value_id', '=',
                                    result_value.id),
                                    ('product_tmpl_id', '=', produt_temp[0].id)], limit=1)
                            res.update({'product_id': pro.id})
                else:
                    for re in list(res.keys()):

                        if re == 'Size':
                            attribute = attribute_dict[re] if re in list(attribute_dict.keys()) else False
                            if not attribute:
                                attribute = self.env['product.attribute'].create({'name': re})
                                attribute_dict[attribute.name] = attribute
                            result_value = self.env['product.attribute.value'].search(
                                [('name', '=', res[re]), ('attribute_id', '=', attribute.id)])
                            if not result_value:
                                result_value = self.env['product.attribute.value'].create(
                                    {'name': res[re], 'attribute_id': attribute.id})
                            produt_temp = self.env['product.template'].create({
                                'name': rec,
                                'default_code': res['SKU'],
                                'detailed_type': 'product',
                                'list_price': res['Sales Price'],
                                'attribute_line_ids': [(0, 0, {
                                    'attribute_id': attribute.id,
                                    'value_ids': [(4, result_value.id)]
                                })]
                            })
                            # print("SSSSSs",produt_temp)
                            pro = self.env['product.product'].search(
                                [('product_tmpl_id', '=', produt_temp.id)], limit=1)
                            # print("product_id________________", pro)
                            # print("product SKU________________", res['SKU'])
                            res.update({'product_id': pro.id})
                            product_template_ids += produt_temp
                # print("product_id",pro)
                vals.update({'product_id': pro.id})
                for re in list(res.keys()):
                    for i in field_map_dict:
                        if i == re:
                            for j in field_map_dict[i]:
                                if j == 'id':
                                    values = field_map_dict[i][j]
                                else:
                                    if values.ttype not in relational_fields:
                                        if values.name == 'default_code':
                                            vals.update({'default_code': res[re]})
                                        if res[re] == 0:
                                            vals.update({values.name: res[re] + 0.01})
                                        else:
                                            vals.update({values.name: res[re]})
                                    # elif values.ttype == 'many2one' and values.name == '':
                                    elif values.ttype == 'many2one':
                                        # print("cat",res[re])
                                        ref_id = self.env[values.relation].search([('name', '=', res[re])],
                                                                                  limit=1)
                                        # print("ref_id",ref_id)
                                        if ref_id:
                                            vals.update({values.name: ref_id.id})
                                        # else:
                                        #     raise ValidationError(_('%s :  not found!', (res[re])))

                vals.update({'shop_id': resultt.id})
                valList.append(vals)
        product_list = []
        for i in valList:
            for j in i:
                if j == 'default_code':
                    # print("shop______", i.get('shop_id'))
                    shop_id = self.env['sale.shop'].browse(i.get('shop_id'))
                    ress = self.env['sale.shop.product'].search(
                        [('default_code', '=', i.get('default_code')), ('shop_id', '=', shop_id.id)], limit=1)
                    # print("ress", ress)
                    if ress:
                        # product_list.append((1, ress.id, i)
                        s = ress.write(i)
                        shop_product_id = ress
                    else:
                        # product_list.append((0, 0, i))
                        shop_product_id = self.env['sale.shop.product'].create(i)
                        # print("shop_product_id_________", shop_product_id)
                    new_cr.commit()
                    _logger.info("product Imported :%s -%s" % (shop_product_id.name, i['default_code']))
        # resultt.write({'product_ids': product_list})
        new_cr.close()
        return {}


class FieldsMapping(models.TransientModel):
    _name = "fields.mapping.wizard"
    _description = "Mapping Wizard"

    execl_header_lines_id = fields.Many2one('excel.header.mapping.wizard')
    execl_header_sale_lines_id = fields.Many2one('excel.header.sale.mapping.wizard')
    excel_head = fields.Char(string="Excel Head")

    field_id = fields.Many2one('ir.model.fields', string="Field")
