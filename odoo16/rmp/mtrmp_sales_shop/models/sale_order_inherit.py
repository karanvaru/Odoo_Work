from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_shop_id = fields.Many2one('sale.shop', string="Shop")
    payment_transaction_settlement_id = fields.One2many('payment.settlement.transaction', 'order_id',
        string="Payment Settlement Transaction")
    sale_state = fields.Selection([
        ('draft', 'New'), ('sent', 'New Sent'), ('sale', 'Order'), ('done', 'Locked'),
        ('cancel', 'Cancelled'), ('confirmed', 'Packing'), ('assigned', 'Ready to Shipped'),
        ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('returned', 'Returned'),
        ('return_intiated', 'Return Intiated'),('return_accepted', 'Return Accepted'),
        ('rejected', 'Rejected')], string='Status', readonly=True, copy=False, index=True,
        tracking=3, default='draft')
    flipkart_payment_settlement_ids = fields.One2many('flipkart.payment.settlement', 'order_id',
                                                        string="Flipkart Settlement Transaction")
    amazon_payment_settlement_ids = fields.One2many('amazon.payment.settlement', 'order_id',
                                                        string="Amazon Settlement Transaction")

    ajio_payment_settlement_ids = fields.One2many('ajio.payment.settlement', 'order_id',
                                                    string="Ajio Settlement Transaction")

    myntra_payment_settlement_ids = fields.One2many('myntra.payment.settlement', 'order_id',
                                                    string="Myntra Settlement Transaction")

    city_payment_settlement_ids = fields.One2many('citymall.payment.settlement', 'order_id',
                                                    string="Myntra Settlement Transaction")

    # TODO : Ask for compute field
    out_picking = fields.Many2one('stock.picking', string="Out Picking",
        compute="_compute_out_picking",
        store=True)
    out_picking_state = fields.Selection(string="OUT Picking State", related="out_picking.state", store=True)
    in_picking = fields.Many2one('stock.picking', string="IN Picking",
        compute="_compute_out_picking",
        store=True)
    in_picking_state = fields.Selection(string="In Picking State", related="in_picking.state", store=True)

    sub_order_no = fields.Char(string="Ecommerce Order No")
    invoice_type = fields.Selection([('invoice', 'Invoice'), ('create_invoice', 'Create Invoice')])
    is_cancelled = fields.Boolean(string="Cancelled", default=False)
    is_return = fields.Boolean(string="Returned", default=False)
    cancel_date = fields.Date(string="Cancel Date")
    cancel_type = fields.Selection([('cancel', 'Cancelled')])

    # ORDER Ticket
    request_id = fields.Many2one('shop.order.ticket', string='Ticket #', copy=False)
    request_qa_result = fields.Many2one('shop.order.ticket.quality', string='Quality Result',
                                        related='request_id.qa_result', copy=False)
    request_state = fields.Selection([], related='request_id.state', copy=False)
    request_ticket_count = fields.Integer(compute='compute_count')

    type = fields.Selection(
        [('return', 'Return'), ('reject', 'Rejected'), ('other', 'Other')],
        string="Type", copy=False )

    def cancel_orders(self):
        for order in self:
            self.env['sale.order.cancel'].create({'order_id': order.id}).action_cancel()
            self._cr.commit()

    def process_payment_trasaction_file(self,shop_id, payment_main_dict, shop_log_id):
        for record in payment_main_dict:
            order = payment_main_dict.get('sale_order')
            if not order:
                continue
            sale_order = self.env['sale.order'].search([('client_order_ref', '=', order), ('sales_shop_id', '=', shop_id.id)],
                    limit=1)
            if not sale_order:
                continue
            payment_transaction_id = self.env['payment.settlement.transaction'].search([('order_id','=',sale_order.id)])
            if not payment_transaction_id:
                payment_transaction_id = self.env['payment.settlement.transaction'].create(
                        {'shop_id' : shop_id.id,
                        'order_id' :  sale_order.id,
                        'transaction_id' : record.get('transaction_id')})
            shop_product = self.env['sale.shop.product'].search(
                    [('default_code', '=', record.get('sku')), ('shop_id', '=',
                                                                      shop_id.id)])
            product = shop_product.product_id
            order_field_list = ['sale_amount', 'sku', 'quantity', 'delivered_quantity', 'unit_price',
                                'transaction_id', 'other_charges1', 'other_charges2', 'other_charges3',
                                'other_charges4', 'other_charges5', 'other_charges6',
                                'other_charges7', 'other_charges8', 'other_charges9', 'other_charges10',
                                'payment_date', 'sale_return_amount', 'shipping_amount', 'igst_rate', 'igst',
                                'cgst_rate', 'cgst', 'sgst_rate', 'sgst', 'tds_rate',
                                'other_charges', 'return_qty']
            for value in order_field_list:
                payment_dict_value =  record.get(value)
                if payment_dict_value:
                    excel_head = self.env['payment.settlement.head.type'].search([('name','=',record.get('excel_head'))])
                    if not excel_head:
                       excel_head= self.env['payment.settlement.head.type'].create({'name' :record.get(
                               'excel_head')})
                    self.env['payment.settlement.transaction.lines'].create(
                            {'payment_transaction_id' : payment_transaction_id.id,
                             'order_id': sale_order.id,
                             'type_id' : excel_head.id,
                             'product_id' : product.id,
                             'value' : payment_dict_value.get('value'),
                             'order_reference' : order
                             })


    def process_order_main_dict(self,shop,order_main_dict,shop_log_id):
        for order,order_dict in order_main_dict.items():
            if order_dict.get('skip_order'):
                continue
            partner = self.env['res.partner']
            billing_partner = self.env['res.partner']
            shipping_partner = self.env['res.partner']
            sale_order = self.env['sale.order'].search([('client_order_ref','=',order),('sales_shop_id','=',shop.id)],
                                                       limit=1)
            if sale_order:
                continue
            if order_dict.get('customer'):
                customer = order_dict.get('customer')
                if customer.get('name'):
                    partner = self.env['res.partner'].search([('name','=',customer.get('name'))],limit=1)
                    if not partner:
                        partner = self.env['res.partner'].search([('name','=',customer.get('name'))],limit=1)
                    if not partner:
                        partner = self.env['res.partner'].create({'name' : customer.get('name')})
            if not partner:
                partner = shop.shop_customer_id
            if order_dict.get('billing'):
                billing_vals = order_dict.get('billing')
                if billing_vals.get('name'):
                    billing_partner = self.env['res.partner'].search([('name', '=', billing_vals.get('email'))], limit=1)
                    if not billing_partner:
                        billing_partner = self.env['res.partner'].search([('name','=', billing_vals.get('name'))],limit=1)
                    if not billing_partner:
                        billing_partner = self.env['res.partner'].create(billing_vals)
            if order_dict.get('shipping'):
                shipping_vals = order_dict.get('shipping')
                if shipping_vals.get('name'):
                    shipping_partner = self.env['res.partner'].search([('name', '=', shipping_vals.get('name'))], limit=1)
                    if not shipping_partner:
                        shipping_partner = self.env['res.partner'].search([('name','=', shipping_vals.get('name'))],limit=1)
                    if not shipping_partner:
                        shipping_partner = self.env['res.partner'].create(shipping_vals)
            date_order = datetime.now()
            try:
                date_order = datetime.strptime(order_dict.get('order_date'), shop.date_format)
            except:
                date_order = datetime.now()
                pass

            order_vals =  {
                    "company_id": shop.company_id.id,
                    "branch_id" : shop.branch_id.id,
                    "partner_id": partner.id,
                    "partner_invoice_id": billing_partner.id or partner.id,
                    "partner_shipping_id": shipping_partner.id or partner.id,
                    "warehouse_id": shop.default_warehouse_id.id,
                    "date_order": date_order,
                    #"date_order": datetime.now(),
                    "state": "draft",
                    "pricelist_id": shop.pricelist_id.id,
                    "team_id": shop.crm_team_id.id,
                    "client_order_ref" : order,
                    "sub_order_no" : order,
                    "sales_shop_id" : shop.id
                }
            order = self.create(order_vals)

            for product_list in order_dict.get('product_info'):
                shop_product = self.env['sale.shop.product'].search([('default_code','=',product_list.get('sku')),('shop_id','=',
                                                                                                     shop.id)])
                product = shop_product.product_id
                uom_id = product and product.uom_id and product.uom_id.id or False
                if product:
                    line_vals = {
                        "product_id": product and product.ids[0] or False,
                        "order_id": order.id,
                        "company_id": order.company_id.id,
                        "product_uom": uom_id,
                        "price_unit": product_list.get('price'),
                        "product_uom_qty": product_list.get('qty')
                    }
                    self.env['sale.order.line'].create(line_vals)
            self._cr.commit()
            order.action_confirm()
        return True

    def compute_count(self):
        for record in self:
            record.request_ticket_count = self.env['shop.order.ticket'].search_count(
                [('order_id', '=', record.id)])

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({'sale_state' : 'sale'})
        for so in self.order_line:
            sale = self.env['sale.shop.product'].search([('product_id', '=', so.product_id.id)], limit=1)
            if sale:
                vals = {
                    'last_sale_order_line_id': so.id,
                    'last_sale_order_id': so.order_id.id
                }
                sale.update(vals)
        return res

    # def _write(self, vals):
    #     res = super(SaleOrder, self)._write(vals)
    #     picking_id = self.picking_ids.filtered(
    #         lambda line: line.picking_type_id.sequence_code == 'PICK' and line.state == 'done')
    #     if picking_id:
    #         self.write({'state': 'confirmed'})
    #     assigned_out_picking_id = self.picking_ids.filtered(
    #         lambda line: line.picking_type_id.sequence_code == 'OUT' and line.state == 'assigned')
    #     if assigned_out_picking_id:
    #         self.write({'state': 'assigned'})
    #     out_picking_id = self.picking_ids.filtered(
    #         lambda line: line.picking_type_id.sequence_code == 'OUT' and line.state == 'done')
    #     if out_picking_id:
    #         self.write({'state': 'in_transit'})
    #     # if vals.get('out_picking_state'):
    #     #     self.write({'state': vals.get('out_picking_state')})
    #     # if vals.get('out_picking_state') == 'done':
    #     #     self.write({'state': 'in_transit'})
    #     # if vals.get('out_picking_state') == 'draft':
    #     #     self.write({'state': 'sale'})
    #     return res

    def retrun_order(self):
        self.write({'sale_state': 'returned'})

    def delivery_order(self):
        self.write({'sale_state': 'delivered'})

    def reject_order(self):
        self.write({'sale_state': 'rejected'})

    def _prepare_confirmation_values(self):
        if not self.date_order:
            return super(SaleOrder, self)._prepare_confirmation_values()
        else:
            return {
                'state': 'sale',
                'date_order': self.date_order
            }

    @api.depends('picking_ids')
    def _compute_out_picking(self):
        for rec in self:
            out_picking_id = rec.picking_ids.filtered(lambda line: line.picking_type_code == 'outgoing' and
                                                                   line.state != 'cancel')
            if out_picking_id:
                rec.out_picking = out_picking_id and out_picking_id[0].id
            in_picking_id = rec.picking_ids.filtered(lambda line: line.picking_type_code == 'incoming' and line.state
                                                                  != 'cancel')
            if in_picking_id:
                rec.in_picking = out_picking_id and in_picking_id[0].id

    def cancelled_action(self):
        for rec in self:
            rec.is_cancelled = True
            rec.cancel_date = fields.date.today()
            rec.cancel_type = 'cancel'
            rec.action_cancel()
            rec.message_post(body="order has been cancelled")
            rec.picking_ids.filtered(lambda line: line.picking_type_code == 'outgoing').action_cancel_request()
            out_picking_id = rec.picking_ids.filtered(lambda line: line.picking_type_code == 'outgoing')
            if out_picking_id:
                out_picking_id.message_post(body="order has been cancelled")

    def return_ticket(self):
        for rec in self:
            act = self.env.ref('mtrmp_sales_shop.actions_shop_order_ticket_view').read([])[0]
            act['domain'] = [('order_id', '=', rec.id)]
        return act

    def raise_ticket(self):
        if not self.type:
            raise UserError(_('Please Select Type!'))
        if self.request_id:
            raise UserError(_('All Ready Return Ticket Generated!'))
        in_picking = self.picking_ids.filtered(lambda l : l.picking_type_id.code == 'incoming' and l.state != 'cancel')
        ticket_vals = {
            'order_id': self.id,
            'type': self.type,
            'state': 'confirm',
            'in_picking': in_picking and in_picking[0].id or False
        }
        ge_ticket_id = self.env['shop.order.ticket'].create(ticket_vals)
        self.request_id = ge_ticket_id.id
        # if self.type == 'return':
        #     return {
        #         'name': 'Return Product',
        #         'type': 'ir.actions.act_window',
        #         'view_mode': 'form',
        #         'res_model': 'return.product.wizard',
        #         'target': 'new',
        #     }
        # elif self.type == 'reject':
        #     lines = []
        #     vals = {}
        #     order_line_obj = self.env['stock.return.picking']
        #     for res in self.order_line.filtered(lambda l: l.qty_delivered):
        #         lines.append((0, 0, {
        #             'product_id': res.product_id.id,
        #             'quantity': res.qty_delivered
        #         }))
        #     vals.update({
        #         'product_return_moves': lines,
        #         'picking_id': self.picking_ids[0].id
        #     })
        #     order_line_new = order_line_obj.new(vals)
        #     order_line_new._onchange_picking_id()
        #     order_line_values = order_line_new._convert_to_write(order_line_new._cache)
        #     return_id = order_line_obj.create(order_line_values)
        #     return_res_id =return_id.create_returns()
