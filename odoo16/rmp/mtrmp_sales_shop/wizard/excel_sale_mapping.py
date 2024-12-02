from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import odoo
from datetime import datetime


class ExcelSaleHeaderMapping(models.TransientModel):
    _name = "excel.header.sale.mapping.wizard"

    lines_ids = fields.One2many('fields.mapping.wizard', 'execl_header_sale_lines_id')
    shop_id = fields.Many2one('sale.shop', string="Shop")

    # TODO : check for resultt
    def upload_sale(self):
        context = self._context
        resultt = self.shop_id
        for rec in context.get('data'):
            partner_id = self.env['res.partner'].search([('name', '=', rec[5])], limit=1)
            state_id = self.env['res.country.state'].search([('name', '=', rec[7])], limit=1)
            if not partner_id:
                partner_id = self.env['res.partner'].create({
                    'name': rec[5],
                    'street': rec[6],
                    'state_id': state_id.id
                })
            date_order = datetime.strptime(rec[4], "%d %b, %Y")
            product = self.env['product.product'].search([('default_code', '=', rec[9])])
            product_devliery = self.env['product.product'].search([('default_code', '=', 'delivery')], limit=1)
            if not product_devliery:
                raise ValidationError("Not Found delivery Product!")
            if not product:
                raise ValidationError("Not Found Product : %s" % (rec[8]))
            # tax_id = self.env['account.tax'].search([('name', '=', rec[17]), ('type_tax_use', '=', 'sale')])
            dis = 0
            if rec[14]:
                dis = round((100 * rec[14]) / rec[12], 2)
            # print("dis", dis)
            number = rec[2].split('_')
            # print("NUMBER", number)
            # print("NUMBER", number[0])
            sub = number[0]
            sale_nu = self.env['sale.order'].search([('sub_order_no', '=', sub)])
            if sale_nu:
                lines_vals = {
                    'order_line': [(0, 0, {'name': product.name,
                                           'product_id': product.id,
                                           'product_uom_qty': rec[11],
                                           'price_unit': rec[12],
                                           'discount': dis
                                           }),
                                   ]

                }
                sale = sale_nu.write(lines_vals)
            else:
                vals = {
                    'partner_id': partner_id.id,
                    'date_order': date_order,
                    'sub_order_no': sub,
                    'order_line': [(0, 0, {'name': product.name,
                                           'product_id': product.id,
                                           'product_uom_qty': rec[11],
                                           'price_unit': rec[12],
                                           # 'tax_id': tax_id.id,
                                           'discount': dis
                                           }), (0, 0, {'name': product_devliery.name,
                                                       'product_id': product_devliery.id,
                                                       'product_uom_qty': 1,
                                                       'price_unit': rec[16],
                                                       })]
                }
                # print("vals", vals)
                sale = self.env['sale.order'].create(vals)
                resultt.write({'order_ids': [(4, sale.id)]})
                # print("SALE", sale)
                sale.action_confirm()

    def d_upload_sale(self):
        config_lines = self.env['fields.mapping.wizard'].search(
            [('execl_header_sale_lines_id', '=', self.id)])
        field_map_dict = {}
        count = 0
        for h in config_lines:
            if h.excel_head == 'Cust address':
                field_map_dict[h.excel_head] = {'Count': count}
            if h.field_id.id != 0:
                field_map_dict[h.excel_head] = {'id': h.field_id}
                field_map_dict[h.excel_head].update({'count': count})
            count += 1
        # print("field_map_dict", field_map_dict)
        relational_fields = ['many2one']
        vals_list = []
        context = self._context
        for row in context.get('data'):
            vals = {}
            for i in field_map_dict:
                for j in field_map_dict[i]:
                    if j == 'id' and j != 'Count':
                        values = field_map_dict[i][j]
                    elif j == 'count' and j != 'Count':
                        if values.ttype not in relational_fields and not values.ttype == 'datetime':
                            if type(row[field_map_dict[i][j]]) == 0:
                                vals.update({values.name: row[field_map_dict[i][j]] + 0.01})
                            else:
                                vals.update({values.name: row[field_map_dict[i][j]]})
                        elif values.ttype == 'datetime':
                            vals.update({values.name: datetime.strptime(row[field_map_dict[i][j]], "%d %b, %Y")})
                        elif values.ttype == 'many2one':
                            ref_id = self.env[values.relation].search([('name', '=', row[field_map_dict[i][j]])],
                                                                      limit=1)
                            if values.name == 'partner_id':
                                if ref_id:
                                    vals.update({'partner_id': ref_id.id})
                                else:
                                    customer = self.env['res.partner'].create({
                                        'name': row[field_map_dict[i][j]],
                                        'street': row[field_map_dict['Cust address']['Count']]
                                    })
                                    vals.update({'partner_id': customer.id})
                            elif ref_id:
                                vals.update({values.name: ref_id.id})
                            else:
                                raise ValidationError(_('%s :  not found!', (values.name)))
            vals_list.append(vals)
        # print("vals_list", vals_list)
        product_list = []
        for i in vals_list:
            product_list.append((0, 0, i))
        resultt.write({'order_ids': product_list})
