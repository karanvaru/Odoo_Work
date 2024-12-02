from odoo import models, fields, api
DEFAULT_DATE_FORMAT = '%m/%d/%Y'

class SaleShop(models.Model):
    _name = 'sale.shop'
    _description = "Shop"

    name = fields.Char(required=True, string="Name", readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", readonly=True,
                                   states={'draft': [('readonly', False)]})
    shop_customer_id = fields.Many2one('res.partner',string='B2C default customer')
    company_id = fields.Many2one('res.company', string="Company",
                                 states={'draft': [('readonly', False)]})
    crm_team_id = fields.Many2one('crm.team', string="Sales Team",
                                  states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string="Sales Manager",
                              states={'draft': [('readonly', False)]})
    is_ecommerce_shop = fields.Boolean(string="Ecommerse Shop", states={'draft': [('readonly', False)]})
    ecommerse_merchant_type = fields.Selection(selection=[('meesho', 'Meesho'),
                                                          ('Amazon','Amazon'),
                                                          ('Flipkart','Flipkart'),
                                                          ('Myntra','Myntra'),
                                                          ('Snapdeal','Snapdeal'),
                                                          ('Ajio','Ajio'),
                                                          ('JioMart','JioMart'),
                                                          ('Tata Cliq','Tata CLiq'),
                                                          ('Shopsy','Shopsy'),('Nykaa Fashion','Nykaa Fashion'),
                                                          ('Bigbasket','Bigbasket'),('shopclues','shopclues'),
                                                          ('Creaftvilla','Creaftvilla'),('Ondc','Ondc'),
                                                          ('Indiamart','Indiamart'),('Tradeindia','Tradeindia'),
                                                          ('Exportersindia','Exportersindia'),
                                                          ('Udaan','Udaan'),
                                                          ('Alibaba','Alibaba'),
                                                          ('Paytm','Paytm'),
                                                          ('jdmart','jdmart.com'),
                                                          ('Citymall', 'Citymall')
                                                          ], string='Ecommerce '
                                                                                                          'Platform',
                                               copy=False,
                                               readonly=True, states={'draft': [('readonly', False)]})
    active = fields.Boolean(string="Active", default=True)
    own_sku_sequence = fields.Boolean(string="Set Different SKU Sequence", readonly=True,
                                      states={'draft': [('readonly', False)]}, copy=False)
    default_sku_sequence_id = fields.Many2one('ir.sequence', string="SKU Sequence", readonly=True,
                                              states={'draft': [('readonly', False)]}, copy=False)
    sku_prefix = fields.Char(string="SKU Prefix", related='default_sku_sequence_id.prefix')
    sku_suffix = fields.Char(string="SKU Suffix", related='default_sku_sequence_id.suffix')
    sku_sequence = fields.Integer(string="SKU Size", related='default_sku_sequence_id.padding')
    default_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse",
                                           states={'draft': [('readonly', False)]}, copy=False)
    default_stock_location_id = fields.Many2one('stock.location', string="Stock Location", readonly=True,
                                                states={'draft': [('readonly', False)]}, copy=False)
    default_discount_product_id = fields.Many2one('product.product', string="Discount Product",
                                                  states={'draft': [('readonly', False)]})
    default_delivery_product_id = fields.Many2one('product.product', string="Delivery Product",
                                                  states={'draft': [('readonly', False)]})
    sale_file_format_id = fields.Many2one('mtrmp.document',string='Sale File Format')
    delivery_file_format_id = fields.Many2one('mtrmp.document', string='Delivery File Format')
    return_file_format_id = fields.Many2one('mtrmp.document', string='Return File Format')
    payment_settlement_format_id = fields.Many2one('mtrmp.document', string='Payment Settlement Format')
    default_category_id = fields.Many2one('product.category', string="Product Category",
                                          states={'draft': [('readonly', False)]}, copy=False
                                          # default=lambda self: self.env.ref('mtrmp_sales_shop.record_category_unmapped')
                                          )
    product_ids = fields.One2many('sale.shop.product', 'shop_id', string="Products", readonly=True,
                                  states={'draft': [('readonly', False)]})
    category_ids = fields.Many2many('product.public.category', string="Categories", readonly=True,
                                    states={'draft': [('readonly', False)]}, copy=False)
    ecommerce_login = fields.Char(string="Email / User ID", states={'draft': [('readonly', False)]})
    ecommerce_password = fields.Char(string="Password", states={'draft': [('readonly', False)]})
    ecommerce_phone = fields.Char(string='Phone / Mobile', states={'draft': [('readonly', False)]})
    order_ids = fields.One2many('sale.order', 'sales_shop_id', states={'draft': [('readonly', False)]})
    product_count = fields.Integer(compute='compute_count')
    sale_count = fields.Integer(compute='compute_count')
    user_ids = fields.Many2many('res.users', states={'draft': [('readonly', False)]})
    sample_attachment_ids = fields.One2many('attachment.sample.file', 'shop_id',
                                            states={'draft': [('readonly', False)]})
    is_button_invisible = fields.Boolean(string="Button Invisible", compute='_compute_is_button_invisible')
    state = fields.Selection(selection=[('draft', 'Draft'), ('active', 'Active'), ('in_active', 'In-Active'), ],
                             default="draft", string="Status", copy=False, tracking=True)

    branch_id = fields.Many2one('res.branch', string='Branch', required=True)

    create_prod = fields.Boolean('Create Product if not found?', default=True)

    payment_settlement_count = fields.Integer(compute="compute_payment_settlement_count")
    amazon_payment_settlement_count = fields.Integer(compute="compute_amazon_payment_settlement_count")
    ajio_payment_settlement_count = fields.Integer(compute="compute_ajio_payment_settlement_count")
    myntra_payment_settlement_count = fields.Integer(compute="compute_myntra_payment_settlement_count")
    citymall_payment_settlement_count = fields.Integer(compute="compute_citymall_payment_settlement_count")
    date_format = fields.Char(string='Date Format', required=True, default=DEFAULT_DATE_FORMAT)


    def payment_settlement(self):
        action = self.env["ir.actions.actions"].sudo()._for_xml_id(
            "mtrmp_sales_shop.actions_channel_payment_settlement")
        form_view = [(self.env.ref('mtrmp_sales_shop.channel_payment_settlement_form').id, 'form')]
        action['views'] = form_view
        action['context'] = {
            'default_shop_id': self.id,
        }
        return action

    def see_payment_settlement(self):
        act = self.env.ref('mtrmp_sales_shop.actions_payment_flipkart_settlement_transaction_lines').sudo().read([])[0]
        orders = self.env['sale.order'].search([('sales_shop_id','=',self.id)])
        print("1111111111111111111   orders",orders)
        transaction = self.env['flipkart.payment.settlement'].search([('order_id','in',orders.ids)])
        act['domain'] = [('id', 'in', transaction.ids)]
        return act

    def see_payment_settlement_amazon(self):
        act = self.env.ref('mtrmp_sales_shop.actions_payment_amazon_settlement_transaction_lines').sudo().read([])[0]
        #orders = self.env['sale.order'].search([('sales_shop_id', '=', self.id)])
        transaction = self.env['amazon.payment.settlement'].search([('sales_shop_id', '=',self.id)])
        act['domain'] = [('id', 'in', transaction.ids)]
        return act

    def see_payment_settlement_ajio(self):
        act = self.env.ref('mtrmp_sales_shop.actions_payment_ajio_settlement_transaction_lines').sudo().read([])[0]
        transaction = self.env['ajio.payment.settlement'].search([('sales_shop_id', '=',self.id)])
        act['domain'] = [('id', 'in', transaction.ids)]
        return act

    def see_payment_settlement_myntra(self):
        act = self.env.ref('mtrmp_sales_shop.actions_payment_myntra_settlement_transaction_lines').sudo().read([])[0]
        transaction = self.env['myntra.payment.settlement'].search([('sales_shop_id', '=',self.id)])
        act['domain'] = [('id', 'in', transaction.ids)]
        return act

    def see_payment_settlement_citymall(self):
        act = self.env.ref('mtrmp_sales_shop.actions_payment_citymall_settlement_transaction_lines').sudo().read([])[0]
        transaction = self.env['citymall.payment.settlement'].search([('sales_shop_id', '=', self.id)])
        act['domain'] = [('id', 'in', transaction.ids)]
        return act




    def compute_payment_settlement_count(self):
        for record in self:
            orders = self.env['sale.order'].search([('sales_shop_id', '=', self.id)])
            transaction = self.env['flipkart.payment.settlement'].search([('order_id', 'in', orders.ids)])
            record.payment_settlement_count = len(transaction)
            if record.ecommerse_merchant_type == "Amazon":
                transaction = self.env['amazon.payment.settlement'].search([('sales_shop_id','=', record.id)])
                record.payment_settlement_count = len(transaction)
            if record.ecommerse_merchant_type == "Ajio":
                transaction = self.env['ajio.payment.settlement'].search([('sales_shop_id', '=', record.id)])
                record.payment_settlement_count = len(transaction)
            if record.ecommerse_merchant_type == "Myntra":
                transaction = self.env['myntra.payment.settlement'].search([('sales_shop_id', '=', record.id)])
                record.payment_settlement_count = len(transaction)
            if record.ecommerse_merchant_type == "Citymall":
                transaction = self.env['citymall.payment.settlement'].search([('sales_shop_id', '=', record.id)])
                record.payment_settlement_count = len(transaction)

    def compute_amazon_payment_settlement_count(self):
        for record in self:
            orders = self.env['sale.order'].search([('sales_shop_id', '=', self.id)])
            transaction = self.env['amazon.payment.settlement'].search([('order_id', 'in', orders.ids)])
            record.amazon_payment_settlement_count = len(transaction)

    def compute_ajio_payment_settlement_count(self):
        for record in self:
            orders = self.env['sale.order'].search([('sales_shop_id', '=', record.id)])
            transaction = self.env['ajio.payment.settlement'].search([('order_id', 'in', orders.ids)])
            record.ajio_payment_settlement_count = len(transaction)

    def compute_myntra_payment_settlement_count(self):
        for record in self:
            orders = self.env['sale.order'].search([('sales_shop_id', '=', record.id)])
            transaction = self.env['myntra.payment.settlement'].search([('order_id', 'in', orders.ids)])
            record.myntra_payment_settlement_count = len(transaction)

    def compute_citymall_payment_settlement_count(self):
        for record in self:
            orders = self.env['sale.order'].search([('sales_shop_id', '=', record.id)])
            transaction = self.env['citymall.payment.settlement'].search([('order_id', 'in', orders.ids)])
            record.myntra_payment_settlement_count = len(transaction)

    @api.onchange('default_warehouse_id')
    def onchange_partner_id(self):
        if self.default_warehouse_id:
            self.branch_id = self.default_warehouse_id.branch_id.id
            self.company_id = self.default_warehouse_id.company_id.id

    @api.depends('product_ids', 'state')
    def _compute_is_button_invisible(self):
        for record in self:
            if record.product_ids and record.state == 'active':
                record.is_button_invisible = True
            else:
                record.is_button_invisible = False

    @api.model
    def default_get(self, fields):
        result = super(SaleShop, self).default_get(fields)
        seq_id = self.env.ref("mtrmp_sales_shop.sequence_sales_shop")
        result.update({'default_sku_sequence_id': seq_id.id,
                       'default_category_id': self.env.ref('mtrmp_sales_shop.record_category_unmapped').id
                       })
        return result

    def compute_count(self):
        for record in self:
            record.product_count = self.env['sale.shop.product'].sudo().search_count(
                [('shop_id', '=', record.id)])
            record.sale_count = self.env['sale.order'].search_count(
                [('sales_shop_id', '=', record.id)])

    def get_shop_product(self):
        for rec in self:
            act = self.env.ref('mtrmp_sales_shop.actions_sale_product_shop_view').sudo().read([])[0]
            act['domain'] = [('shop_id', '=', rec.id)]
        return act

    def get_sale_order(self):
        for rec in self:
            act = self.env.ref('sale.action_orders').sudo().read([])[0]
            act['domain'] = [('sales_shop_id', '=', rec.id)]
        return act

    def action_active(self):
        for record in self:
            record.write({'state': 'active'})

    def action_in_active(self):
        for record in self:
            record.write({'state': 'in_active'})

    def action_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def action_perform_operation(self):
        pass


class IrAttachmentSample(models.Model):
    _name = 'attachment.sample.file'
    _description = "Sample File"

    shop_id = fields.Many2one('sale.shop', string="shop")
    file_type = fields.Selection(
        [('product', 'Import Product'), ('sale_order', 'Import Sale Order'), ('awb', 'Import AWB'),
         ('payment_settlement', 'Import Payment Settlement')],
        string="Import Type File", required=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment File")
    file_name = fields.Char(readonly=False)
    file = fields.Binary(string="File Name", required=True)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        for order in self.sale_order_ids:
            self._create_invoices(order)

        if self.env.context.get('open_invoices'):
            return self.sale_order_ids.action_view_invoice()

        return {'type': 'ir.actions.act_window_close'}