from odoo import fields,models,api,_
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    scheduled_delivery_date = fields.Datetime('Schedule Date',compute='_compute_delivery_delay_days')
    del_done_date = fields.Datetime('Delivery Done Date')
    delivery_delay_days = fields.Char("Delivery Days",compute='_compute_delivery_delay_days')
    delivery_status = fields.Selection([('waiting', 'Waiting'),('pass', 'Pass'), ('fail', 'Fail')],compute='_compute_delivery_delay_days',string ='Delivery Status', default ='waiting', store=True)
    time_1  = fields.Char('Time 1')
    time_2  = fields.Char('Time 2')
    otd_type = fields.Selection([('SSD', 'SSD'),('NSSD', 'NSSD')], string="OTD Type")
    ssd_reason = fields.Text(string="SSD Failed Reason")
    nssd_reason = fields.Text(string="NSSD Reason")
    so_gem_rp_id = fields.Many2one('res.partner', string="SO Gem RP")
    ssd_failed_reason_id = fields.Many2one('ssd.failed.reason', string="Failure Reason")
    ready_op = fields.Char(string="Ready OP", compute="compute_sale_order_ready_op",store=True)
    phone_number = fields.Char(string="Phone Number", compute="compute_partner")
    invoice_product_category = fields.Selection([('SBC', 'SBC'),
                                                 ('XL Series', 'XL Series'),
                                                 ('Laptop', 'Laptop'),
                                                 ('Tablet', 'Tablet'),
                                                 ('Desktop/AIO', 'Desktop/AIO')], string="Invoiced Product Category")
    product_id = fields.Many2one('product.product', string="Product",domain=[('sale_ok', '=', True)], compute="compute_product")
    effective_date_r = fields.Date(string="Effective Date R", compute="compute_effective_date_r")
    country_state = fields.Char(string="State", compute="compute_partner")
    email = fields.Char(string="Email", compute="compute_partner")
    nad = fields.Date(string="NAD", compute="compute_partner")
    potca_gen_two = fields.Selection([('exactly_contract_specifications', 'Exactly as per Contract Specifications'),
                                      ('literally_higher_specifications', 'Literally Higher Specifications'),
                                      ('higher_specifications', 'Higher Specifications'),
                                      ('other', 'Other')], string="POTCA Gen 2.0", track_visibility='always')
    
    # product_category_invoiced = fields.Selection([('SBC', 'SBC'), ('XL Series', 'XL Series'), ('Desktop/AIO', 'Desktop/AIO'), ('Laptop', 'Laptop'), ('Tablet', 'Tablet'), ('Other', 'Other')], string="Product Category Invoiced")
    manufacturing_details_ids = fields.One2many('mrp.production', 'sale_order_id', string="Manufacturing Details", domain=[("state","!=","cancel")])
    mp_count_id = fields.Integer('MP count', compute="manufacturing_order_count")
    otd_ots_priority = fields.Selection([
        ('vip_platinum', 'VIP Platinum'),
        ('gold', 'Gold'),
        ('general', 'General'),
    ], string="OTD & OTS Priority", track_visibility='onchange', compute="compute_otd_ots_priority")

    purchase_tender_ids = fields.One2many('purchase.agreement', 'sale_order_p_tender_id', string="Purchase Tender",domain=[("state", "!=", "cancel")])
    purchase_order_ids = fields.One2many('purchase.order', 'sale_order_po_id', string="Purchase Order",domain=[("state", "!=", "cancel")])
    vendor_bill_ids = fields.One2many('account.invoice', 'sale_order_po_id', string="Vendor Bills")
    purchase_tender_count = fields.Integer('P Tender count', compute="p_tender_count")
    product_category_head_id = fields.Many2one('res.users', string="Product Category Head", domain=[('is_int_user', '=', True)], track_visibility="always")
    revenue_head_id = fields.Many2one('res.users', string="Revenue Head", domain=[('is_int_user', '=', True)], track_visibility="always")
    vice_president_id = fields.Many2one('res.users', string="Vice President", domain=[('is_int_user', '=', True)], track_visibility="always")
    shipping = fields.Selection([
        ("By Customer (OTD One)", "By Customer (OTD One)"),
        ("By RDP (OTD Two)", "By RDP Surface (OTD Two)"),
        ("By RDP Air (OTD Two)", "By RDP Air (OTD Two)"),
        ("Not Required", "Not Required"),
    ], string='Shipping', track_visibility='onchange')
    receipt_amount = fields.Monetary(string="Receipt Amount", currency_field="currency_id",compute="compute_receipt_amount")
    to_be_collected = fields.Monetary(string="To Be Collected", currency_field="currency_id",compute="compute_to_be_collected")
    defer_amount = fields.Monetary(string="To Be Collected", currency_field="currency_id",compute="compute_to_be_defer")
    open_days = fields.Char(string="Open Days",readonly=True, compute="compute_open_days",track_visibility="always")
    amount_in_words = fields.Char(string="Amount in Words", size=300, compute="compute_amount_in_words")

    total_discount_amount = fields.Monetary(
        string='Total Discount Amount',
        compute='_compute_total_discount_amount',
        store=True,
    )

    @api.depends('order_line.discount_amount')
    def _compute_total_discount_amount(self):
        for order in self:
            order.total_discount_amount = sum(order.order_line.mapped('discount_amount'))

    @api.depends('amount_total')
    def compute_amount_in_words(self):
        for rec in self:
            if rec.amount_total > 1:
                rec.amount_in_words = rec.currency_id.amount_to_text(rec.amount_total).replace(',', ' ').replace('-', ' ')
                print("___________ssssss___________", rec.amount_in_words)

    @api.multi
    def compute_receipt_amount(self):
        for record in self:
            sname = record.name
            total_records = self.env['x_split_receipt_payments'].search([('x_studio_saleorder_no_1', '=', sname), ('x_studio_payment_type', '=', 'inbound')])
            for rec in total_records:
                record.receipt_amount += rec.x_studio_split_payment

    @api.depends('amount_total')
    def compute_to_be_defer(self):
        for rec in self:
            rec.defer_amount = rec.amount_total - rec.receipt_amount

    @api.depends('defer_amount')
    def compute_to_be_collected(self):
        for rec in self:
            rec.to_be_collected = rec.defer_amount


    # @api.depends('order_line.discount', 'order_line.price_subtotal')
    # def _compute_discount_amount(self):
    #     for order in self:
    #         order.discount_amount = sum(
    #             line.price_total * (line.discount / 100)
    #             for line in order.order_line
    #         )

    @api.depends('partner_id')
    def compute_partner(self):
        for record in self:
            record.phone_number = record.partner_id.phone
            record.country_state = record.partner_id.state_id.name
            record.email = record.partner_id.email
            record.nad = record.partner_id.activity_date_deadline
    
    @api.multi
    def compute_effective_date_r(self):
        for record in self:
            record.effective_date_r = record.effective_date
    
    @api.multi
    def compute_product(self):
        for rec in self:
            for record in rec.order_line:
                rec.product_id = record.product_id

    def _update_old_record(self):
        for res in self.env['sale.order'].search([]):
            # All Records Server
            res._compute_delivery_delay_days()
    
    @api.multi
    def compute_sale_order_ready_op(self):
        for rec in self:
            for record in rec.picking_ids:
                rec.ready_op = record.ready_op

    @api.depends('name')
    def compute_open_days(self):
        for record in self:
            sname = record['name']
            invlines = self.env['account.invoice'].search([('origin', '=', sname)])
            if not invlines:
                if record['confirmation_date']:
                    today = datetime.today()
                    record['open_days'] = today - record['confirmation_date']
                    record['open_days'] = record['open_days'].split(',')[0]
            else:
                for rec in invlines:
                    if record['confirmation_date']:
                        if rec['date_invoice']:
                            confirm_date_time = record['confirmation_date']
                            confirm_date = confirm_date_time.date()
                            record['open_days'] = rec['date_invoice'] - confirm_date
                            record['open_days'] = record['open_days'].split(',')[0]

    @api.multi
    @api.depends('picking_ids', 'picking_ids.state', 'picking_ids.scheduled_date')
    def _compute_delivery_delay_days(self):
        for rec in self:
            for stock in rec.picking_ids:
                rec.scheduled_delivery_date = stock.scheduled_date
                rec.del_done_date = stock.date_done
                today = datetime.today()
                today_d = datetime.strftime(today, '%Y-%m-%d %H:%M')
                today_dt = datetime.strptime(today_d, '%Y-%m-%d %H:%M')
                promise = rec.scheduled_delivery_date
                promise_d = datetime.strftime(promise, '%Y-%m-%d %H:%M')
                promise_dt = datetime.strptime(promise_d, '%Y-%m-%d %H:%M')

                if rec.scheduled_delivery_date and stock.state != 'done' or stock.state != 'cancel':
                    rec.time_1 = str((today_dt - promise_dt).days)
                    rec.delivery_delay_days = rec.time_1 + " Days"
                    # rec.r_delivery_delay_days = rec.delivery_delay_days
                if rec.scheduled_delivery_date and stock.state == 'done'or stock.state == 'cancel':
                    if rec.del_done_date and promise_dt:
                        rec.time_2 = str((rec.del_done_date-promise_dt).days)
                        rec.delivery_delay_days = rec.time_2  + " Days"
                    # rec.r_delivery_delay_days = rec.delivery_delay_days

                differ = promise_dt - today_dt
                if stock.state == 'done' and promise_dt >= today_dt:
                    rec.delivery_status = 'pass'
                    # rec.r_delivery_status = str(rec.delivery_status)
                elif stock.state =='done' and promise_dt < today_dt:
                    if int(rec.time_2) > 0: # type: ignore
                        rec.delivery_status = 'pass'
                        # rec.r_delivery_status = str(rec.delivery_status)
                    else:
                        rec.delivery_status = 'fail'
                        # rec.r_delivery_status = str(rec.delivery_status)
                else:
                    rec.delivery_status = 'waiting'
                    # rec.r_delivery_status = str(rec.delivery_status)

    @api.multi
    def manufacturing_order_count(self):
        count_values = self.env['mrp.production'].search_count([('sale_order_id', '=', self.id)])
        self.mp_count_id = count_values

    @api.multi
    def action_view_manufacturing_orders(self):
        return {
            'name': 'Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'context': {
                'default_sale_order_id': self.id
            },
            'domain': [('sale_order_id', '=', self.id)],
        }

    @api.multi
    def action_confirm(self):
        res = super().action_confirm

        for order in self:
            order.show_manufacturing_orders_button = True
        return res

    @api.depends('partner_id')
    def compute_otd_ots_priority(self):
        for rec in self:
            rec.otd_ots_priority = rec.partner_id.otd_ots_priority

    @api.multi
    def p_tender_count(self):
        count_values = self.env['purchase.agreement'].search_count([('sale_order_p_tender_id', '=', self.id)])
        self.purchase_tender_count = count_values

    @api.multi
    def action_view_p_tender_orders(self):
        return {
            'name': 'P Tender Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.agreement',
            'context': {
                'default_sale_order_p_tender_id': self.id
            },
            'domain': [('sale_order_p_tender_id', '=', self.id)]
        }



class SSDFailedReason(models.Model):
    _name = "ssd.failed.reason"
    _description = 'SSD Failed Reason'

    name = fields.Char(string='Name')

 #************Added by Sabitha ******************* 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Monetary(
        string='Discount Amount',
        compute='_compute_discount_amount',
        store=True,
    )

    @api.depends('discount', 'price_unit', 'product_uom_qty')
    def _compute_discount_amount(self):
        for line in self:
            line.discount_amount = (line.price_unit * line.product_uom_qty) * (line.discount / 100)    




   
