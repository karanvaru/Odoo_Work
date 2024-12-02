from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io

from xlwt import easyxf


class StockPicking(models.Model):
    _inherit = "stock.picking"

    order_id = fields.Many2one('sale.order')
    is_cancelled = fields.Boolean(string="Cancelled", default=False)
    cancel_date = fields.Date(string="Cancel Date")


    def update_order_tracking_file(self,shop_id,awbnumber_dict,shop_log_id):
        for order,data in awbnumber_dict.items():
            order = order
            sale_order = self.env['sale.order'].search([('sub_order_no','=',order),('sales_shop_id','=',shop_id.id)])
            if sale_order:
                if not sale_order.picking_ids:
                    message = 'Sale order is not confirmed Yet %s' \
                              % (order)
                    self.env['shop.fail.log.lines'].create({
                        'operation': 'import_AWB',
                        'message': message,
                        'is_mismatch': True,
                        'shop_log_id': shop_log_id.id
                    })
                    continue
                picking = sale_order.picking_ids.filtered(lambda l:l.state != 'cancel' and not l.carrier_tracking_ref)
                pack_picking = self.env['stock.picking'].search([('id','in',picking.ids),('name','ilike','PACK')])
                if pack_picking:
                    pack_picking.write({'carrier_tracking_ref' : ','.join(data.get('tracking_list'))})
                else :
                    message = "Couldn't able to find Pack Deliver order %s" \
                              % (order)
                    self.env['shop.fail.log.lines'].create({
                        'operation': 'import_AWB',
                        'message': message,
                        'is_mismatch': True,
                        'shop_log_id': shop_log_id.id
                    })

    def create_return_document_of_order(self,shop_id,return_dict,shop_log_id):
        for order,data in return_dict.items():
            order = order
            sale_order = self.env['sale.order'].search([('sub_order_no','=',order),('sales_shop_id','=',shop_id.id)],
                                                       limit=1)
            if sale_order:
                outgoing_picking = sale_order.picking_ids.filtered(lambda l:l.picking_type_id.code == 'outgoing' and
                l.state == 'done')
                if not outgoing_picking:
                    message = 'Delivery Order is not in Done state, So Its not possible to create return for order %s'\
                              % (order)
                    self.env['shop.fail.log.lines'].create({
                        'operation': 'import_return',
                        'message': message,
                        'is_mismatch': True,
                        'shop_log_id': shop_log_id.id
                    })
                incoming_return = sale_order.picking_ids.filtered(lambda l: l.picking_type_id.code == 'incoming' and
                                                                             l.state != 'cancel')
                if outgoing_picking and not incoming_return:
                    return_vals = {'picking_id' : outgoing_picking[0].id}
                    new_record =  self.env['stock.return.picking'].new(return_vals)
                    new_record._onchange_picking_id()
                    new_vals = self.env['stock.return.picking']._convert_to_write(
                            {name: new_record[name] for name in new_record._cache})
                    return_picking = self.env['stock.return.picking'].create(new_vals)
                    return_picking.create_returns()
                    sale_order.write({'sale_state' : 'return_intiated'})
            else:
                message = 'Order is not found with reference %s' \
                          % (order)
                self.env['shop.fail.log.lines'].create({
                    'operation': 'import_return',
                    'message': message,
                    'is_mismatch': True,
                    'shop_log_id': shop_log_id.id
                })


    def write(self, vals):
        #self.ensure_one()
        res = super(StockPicking, self).write(vals)
        for record in self:
            if record.state == 'done':
                picking_id = record.filtered(
                    lambda line: line.picking_type_id.sequence_code == 'PICK' and line.state == 'done')
                if picking_id:
                    record.sale_id.write({'sale_state': 'confirmed'})
                assigned_out_picking_id = record.filtered(
                    lambda line: line.picking_type_id.sequence_code == 'PACK' and line.state == 'done')
                if assigned_out_picking_id:
                    record.sale_id.write({'sale_state': 'assigned'})
                out_picking_id = record.filtered(
                    lambda line: line.picking_type_id.sequence_code == 'OUT' and line.state == 'done')
                if out_picking_id:
                    record.sale_id.write({'sale_state': 'delivered'})
                return_picking = record.filtered(
                        lambda line: line.picking_type_id.code == 'incoming' and line.sale_id and line.state == 'done')
                if return_picking:
                    record.sale_id.write({'sale_state' : 'returned'})
        return res

    def action_cancel_request(self):
        for rec in self:
            if rec.picking_type_code == 'outgoing':
                rec.is_cancelled = True
                rec.cancel_date = fields.date.today()
                rec.message_post(body="order has been cancelled")
                rec.action_cancel()

    def action_mass_pick_list(self):
        res = self.env['stock.picking'].search([('id', 'in', self._context.get('active_ids'))])
        data = {
            'doc_ids': self._context.get('active_ids'),
            'model': 'stock.picking',
            'docs': res,

        }
        flag = False
        msg =''
        for i in res:
            if not i.products_availability == 'Available':
                flag = True
                msg += "\n %s Product is not Available "%(i.name)
            # if not i.state == 'confirmed':
            #     flag = True
            #     msg += "\n %s state is not confirmed" % (i.name)
            if i.state not in ['draft','waiting','confirmed']:
                flag = True
                msg += "\n %s state is not confirmed" % (i.name)
            if i.ready_to_pack:
                msg += "\n %s ready to Pack is True" % (i.name)
                flag = True
        if not flag:
            return self.env.ref('mtrmp_sales_shop.action_mass_picklist').report_action(self)
        else:
            raise ValidationError(_(msg))

    def get_report_values(self, res_picking):
        code_dict = {}

        for re in res_picking:
            for res in re.move_ids_without_package:
                if res.picking_id.location_id.id not in code_dict:
                    code_dict[res.picking_id.location_id.id] = {
                        'name': res.picking_id.location_id.location_id.name + '/' + res.picking_id.location_id.name,

                    }
                if res.qty_on_hand != 0:
                    if res.product_id.id not in code_dict[res.picking_id.location_id.id].keys():
                        code_dict[res.picking_id.location_id.id][res.product_id.id] = {
                            'product_name': res.product_id.name,
                            'qty_required': 0,
                            'qty_done': 0,
                            'qty_on_hand': res.qty_on_hand,
                        }
                    qty_required = code_dict[res.picking_id.location_id.id][res.product_id.id].get('qty_required')
                    qty_done = code_dict[res.picking_id.location_id.id][res.product_id.id].get('qty_done')
                    code_dict[res.picking_id.location_id.id][res.product_id.id].update({
                        'qty_required': qty_required + res.product_uom_qty,
                        'qty_done': qty_done + res.quantity_done
                    })

        return code_dict

    def action_mass_pack_list(self):
        for rec in self:
            # rec.ready_to_pack = True
            res = self.env['stock.picking'].search([('id', 'in', self._context.get('active_ids'))])
            # print("res______", res)
            filename = 'PackList.xls'
            workbook = xlwt.Workbook(encoding="UTF-8")
            sheet1 = workbook.add_sheet('PackList')
            formate_2 = xlwt.easyxf("font: bold 1, color black ;align: horiz center")
            formate_1 = xlwt.easyxf(num_format_str='MM/DD/YYYY')

            row_index = 0
            sheet1.write(row_index, 0, "Channel Name", formate_2)
            sheet1.write(row_index, 1, "Shipping Company", formate_2)
            sheet1.write(row_index, 2, "AWB Number", formate_2)
            sheet1.write(row_index, 3, "Channel Sub Order Id", formate_2)
            sheet1.write(row_index, 4, "Order Date", formate_2)
            sheet1.write(row_index, 5, "Buyer State", formate_2)
            sheet1.write(row_index, 6, "Buyer Pin Code", formate_2)
            sheet1.write(row_index, 7, "Product Sku Code", formate_2)
            sheet1.write(row_index, 8, "Product Name", formate_2)
            sheet1.write(row_index, 9, "Qty", formate_2)
            for re in res:
                for record in re.move_ids_without_package:
                    row_index += 1
                    sheet1.write(row_index, 0, re.sale_id.sales_shop_id.name)
                    sheet1.write(row_index, 1, re.carrier_id.name)
                    sheet1.write(row_index, 2, re.carrier_tracking_ref)
                    sheet1.write(row_index, 3, re.sale_id.sub_order_no)
                    sheet1.write(row_index, 4, re.sale_id.date_order, formate_1)
                    sheet1.write(row_index, 5, re.partner_id.state_id.name)
                    sheet1.write(row_index, 6, re.partner_id.zip)
                    sheet1.write(row_index, 7, record.product_id.default_code)
                    sheet1.write(row_index, 8, record.product_id.name)
                    sheet1.write(row_index, 9, record.quantity_done)

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
class StockMove(models.Model):
    _inherit = "stock.move"

    qty_on_hand = fields.Float(
        string="On Hand",
        compute='_compute_qty_on_hand',
        store=True

    )

    @api.depends('picking_id.location_id', 'product_id')
    def _compute_qty_on_hand(self):
        for rec in self:
            quant_obj = self.env['stock.quant']
            if rec.product_id and rec.picking_id.location_id:
                qty_available = quant_obj._get_available_quantity(rec.product_id, rec.picking_id.location_id)
                rec.qty_on_hand = qty_available
