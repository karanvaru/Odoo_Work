from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT


class amazon_instace_ept(models.Model):
    _name = "amazon.instance.ept"
    _inherit = ['mail.thread']

    def _get_default_company_id(self):
        return self.env.user.company_id.id

    """Added by Dhruvi [28-08-2018]
    To set default value to stock field"""

    def _get_default_stock_field(self):
        return self.env.ref('stock.field_product_product__qty_available')

    seller_id = fields.Many2one('amazon.seller.ept', string='Seller', required=True)
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')],
                                      related="seller_id.amazon_selling",
                                      string='Fulfillment By ?', readonly=True)

    marketplace_id = fields.Many2one('amazon.marketplace.ept', string='Marketplace', required=True,
                                     domain="[('seller_id','=',seller_id),"
                                            "('is_participated','=',True)]")
    active = fields.Boolean(string='Active', default=True)

    name = fields.Char(size=120, string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=_get_default_company_id)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    partner_id = fields.Many2one('res.partner', string='Default Customer')
    lang_id = fields.Many2one('res.lang', string='Language')
    account_id = fields.Many2one('account.account', string='Account')

    """Commented by Dhruvi As these is added to amazon seller"""
    # order_auto_import = fields.Boolean(string='Auto Order Import?')
    # order_prefix = fields.Char(size=10, string='Order Prefix')
    # auto_workflow_id = fields.Many2one('sale.workflow.process.ept', string='Auto Workflow (FBM)')

    stock_auto_export = fields.Boolean(string="Stock Auto Export?")
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    price_tax_included = fields.Boolean(string='Is Price Tax Included?')
    tax_id = fields.Many2one('account.tax', string='Default Sales Tax')
    stock_field = fields.Many2one('ir.model.fields', string='Stock Field',
                                  default=_get_default_stock_field)

    """Changes by Dhruvi auto_workflow_id is fetched according to seller wise"""
    picking_policy = fields.Selection([('direct', 'Deliver each product when available'),
                                       ('one', 'Deliver all products at once')],
                                      string='Shipping Policy',
                                      related="seller_id.auto_workflow_id.picking_policy",
                                      readonly=True)
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'), ('delivery', 'Delivered quantities'), ],
        string='Invoicing Policy', related="seller_id.auto_workflow_id.invoice_policy",
        readonly=True)

    country_id = fields.Many2one("res.country", "Country", related="marketplace_id.country_id")

    access_key = fields.Char("Access Key", related="seller_id.access_key")
    secret_key = fields.Char("Secret Key", related="seller_id.secret_key")
    merchant_id = fields.Char("Merchant Id", related="seller_id.merchant_id")
    market_place_id = fields.Char("Marketplace ID", related="marketplace_id.market_place_id")

    # added by dhaval
    auth_token = fields.Char('Auth Token', related="seller_id.auth_token")

    # commented by dhaval 26-2-2019
    # no more field required
    # send_order_acknowledgment = fields.Boolean("Order Acknowledgment required ?")
    # allow_order_adjustment = fields.Boolean("Allow Order Adjustment ?")

    catalog_last_sync_on = fields.Datetime("Last Catalog Sync Time")
    inventory_last_sync_on = fields.Datetime("Last FBM Inventory Sync Time")
    image_last_sync_on = fields.Datetime("Last Images Sync Time")

    """Commented by Dhruvi as these fields are moved to amazon seller ept"""
    # shipment_charge_product_id = fields.Many2one("product.product", "Shipment Fee",
    #                                              domain=[('type', '=', 'service')])
    # gift_wrapper_product_id = fields.Many2one("product.product", "Gift Wrapper Fee",
    #                                           domain=[('type', '=', 'service')])
    # promotion_discount_product_id = fields.Many2one("product.product", "Promotion Discount",
    #                                                 domain=[('type', '=', 'service')])
    # ship_discount_product_id = fields.Many2one("product.product", "Shipment Discount",
    #                                            domain=[('type', '=', 'service')])
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    # condition = fields.Selection([('New', 'New'),
    #                               ('UsedLikeNew', 'UsedLikeNew'),
    #                               ('UsedVeryGood', 'UsedVeryGood'),
    #                               ('UsedGood', 'UsedGood'),
    #                               ('UsedAcceptable', 'UsedAcceptable'),
    #                               ('CollectibleLikeNew', 'CollectibleLikeNew'),
    #                               ('CollectibleVeryGood', 'CollectibleVeryGood'),
    #                               ('CollectibleGood', 'CollectibleGood'),
    #                               ('CollectibleAcceptable', 'CollectibleAcceptable'),
    #                               ('Refurbished', 'Refurbished'),
    #                               ('Club', 'Club')], string="Condition",default='New',copy=False)

    cod_charge_product_id = fields.Many2one("product.product", "COD Fee",
                                            domain=[('type', '=', 'service')])
    team_id = fields.Many2one('crm.team', 'Sales Team')

    pro_advt_access_key = fields.Char("Pro Access Key")
    pro_advt_scrt_access_key = fields.Char("Secret Access Key")
    pro_advt_associate_tag = fields.Char("Associate Tag")

    default_amazon_tax_code_id = fields.Many2one('amazon.tax.code.ept', "Default Tax Code")
    fulfillment_by = fields.Selection([('MFN', 'Manufacturer Fulfillment Network')],
                                      string="Fulfillment By", default='MFN')

    manage_multi_tracking_number_in_delivery_order = fields.Boolean(
        "Manage Multi Tracking Number In Delivery Order", default=False)

    """Commented by Dhruvi as these fields are added in amazon seller"""
    #     auto_create_return_picking = fields.Boolean("Auto Create Return Picking ?",default=False)
    #     auto_create_refund = fields.Boolean("Auto Create Refund ?",default=False)

    update_stock_on_fly = fields.Boolean("Auto Update Stock On the Fly ?", default=False,
                                         help='If it is ticked, real time stock update in Amazon.')
    customer_is_company = fields.Boolean("Customer is Company ?", default=False)
    settlement_report_journal_id = fields.Many2one('account.journal',
                                                   string='Settlement Report Journal')

    """Commented by Dhruvi
        As is_default_odoo_sequence_in_sale_order is moved to amazon seller"""
    # is_default_odoo_sequence_in_sales_order=fields.Boolean("Is default Odoo Sequence in Sales Orders ?")
    ending_balance_account_id = fields.Many2one('account.account', string="Ending Balance Account")
    ending_balance_description = fields.Char("Ending Balance Description")
    invoice_tmpl_id = fields.Many2one("mail.template",
                                      string="Invoice Template")  # for auto_send_invoice
    refund_tmpl_id = fields.Many2one("mail.template",
                                     string="Refund Template")  # for auto_send_refund

    # added by Dhruvi
    producturl_prefix = fields.Char(string="Product URL")
    # Account Field
    amazon_property_account_payable_id = fields.Many2one('account.account', string="Account Payable",
                                                         help='This account will be used instead of the default one as the payable account for the current partner')
    amazon_property_account_receivable_id = fields.Many2one('account.account', string="Account Receivable",
                                                            help='This account will be used instead of the default one as the receivable account for the current partner')

    # Amazon FBA fields

    fba_warehouse_id = fields.Many2one('stock.warehouse', string='FBA Warehouse')
    """Commented by Twinkal [30-07-2019] as stock inventory is transfered as per seller"""
    #     validate_stock_inventory_for_report = fields.Boolean(
    #         "Auto Validate Amazon FBA Live Stock Report")
    fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="Fulfillment By", default='MFN')
    #     stock_auto_import_by_report = fields.Boolean(string='Auto Import FBA Live Stock Report?')

    split_order = fields.Boolean('Split FBA Order by Warehouse', default=True)

    # split_order = fields.Boolean('Split FBA Order by Warehouse', default=True)

    order_return_config_ids = fields.One2many('order.return.config', 'instance_id',
                                              string='Order Return Conditions')

    # Inbound Shipment
    allow_process_unshipped_products = fields.Boolean(
        "Allow Process Unshipped Products in Inbound Shipment ?", default=True)
    update_partially_inbound_shipment = fields.Boolean('Allow Update Partially Inbound Shipment ?',
                                                       default=False)
    is_allow_prep_instruction = fields.Boolean(
        string="Allow Prep Instruction in Inbound Shipment ?", default=False,
        help="Amazon FBA: If ticked then allow to pass the prep-instructions details "
             "during create Inbount Shipment Plan in Amazon.")

    check_status_days = fields.Integer("Check Status Days", default=30,
                                       help="System will check status after closed shipment")
    """Commented by Twinkal [30-07-2019] as these field is added to amazon seller."""
    #     auto_process_fba_live_stock_report = fields.Boolean(
    #         string='Auto Process FBA Live Stock Report?')
    amazon_sale_order_ids = fields.One2many('sale.order', 'amz_instance_id',
                                            domain=[('amz_fulfillment_by', '=', 'MFN'),
                                                    ('amz_is_outbound_order', '=', False)],
                                            string='(FBM)Orders')
    quotation_ids = fields.One2many('sale.order', 'amz_instance_id',
                                    domain=[('state', 'in', ['draft', 'sent']),
                                            ('amz_fulfillment_by', '=', 'MFN'),
                                            ('amz_is_outbound_order', '=', False)],
                                    string="(FBM)Quotations")
    order_ids = fields.One2many('sale.order', 'amz_instance_id',
                                domain=[('state', 'not in', ['draft', 'sent', 'cancel']),
                                        ('amz_fulfillment_by', '=', 'MFN'),
                                        ('amz_is_outbound_order', '=', False)],
                                string="(FBM)Sales Order")

    # Unsellable Location
    unsellable_location_id = fields.Many2one('stock.location', string="Unsellable Location",
                                             help="Amazon unsellabel location")

    amazon_fba_sale_order_ids = fields.One2many('sale.order', 'amz_instance_id',
                                                domain=[('amz_fulfillment_by', '=', 'AFN'),
                                                        ('amz_is_outbound_order', '=', False)],
                                                string='(FBA)Sale Orders')
    fba_sale_order_count = fields.Integer(compute='_fba_count_all', string="(FBA)Orders")
    fba_quotation_ids = fields.One2many('sale.order', 'amz_instance_id',
                                        domain=[('state', 'in', ['draft', 'sent']),
                                                ('amz_fulfillment_by', '=', 'AFN'),
                                                ('amz_is_outbound_order', '=', False)],
                                        string="(FBA)Sale Quotations")
    fba_quotation_count = fields.Integer(compute='_fba_count_all', string="(FBA)Quotations")
    fba_order_ids = fields.One2many('sale.order', 'amz_instance_id',
                                    domain=[('state', 'not in', ['draft', 'sent', 'cancel']),
                                            ('amz_fulfillment_by', '=', 'AFN'),
                                            ('amz_is_outbound_order', '=', False)],
                                    string="(FBA)Sales Order")
    fba_order_count = fields.Integer(compute='_fba_count_all', string="(FBA)Sales Orders")

    count_draft_inbound_shipment_plan = fields.Integer(string="Count Draft Inbound Shipment Plan",
                                                       compute="_fba_count_all")
    count_approved_inbound_shipment_plan = fields.Integer(
        string="Count Approved Inbound Shipment Plan", compute="_fba_count_all")

    count_working_inbound_shipment = fields.Integer(string="Count Working Inbound Shipment",
                                                    compute="_fba_count_all")
    count_shipped_inbound_shipment = fields.Integer(string="Count Shipped Inbound Shipment",
                                                    compute="_fba_count_all")
    count_cancelled_inbound_shipment = fields.Integer(string="Count Cancelled Inbound Shipment",
                                                      compute="_fba_count_all")
    count_closed_inbound_shipment = fields.Integer(string="Count Closed Inbound Shipment",
                                                   compute="_fba_count_all")

    fba_return_delivery_order_ids = fields.One2many('stock.picking', 'amazon_instance_id', domain=[
        ('is_amazon_fba_return_delivery_order', '=', 'True')], string="FBA Return Picking")
    fba_return_delivery_order_count = fields.Integer(compute='_fba_count_all',
                                                     string="FBA Return Pickings")

    removal_order_report_last_sync_on = fields.Datetime("Last Removal Order Report Request Time")
    removal_order_config_ids = fields.One2many("removal.order.config.ept", 'instance_id',
                                               string="Removal Order Configuration")

    is_global_warehouse_in_fba = fields.Boolean('Allow Create Removal Order In FBA?',
                                                help="Allow to create removal order in FBA.")

    removal_warehouse_id = fields.Many2one('stock.warehouse', string="Removal Warehouse", help="Removal Warehouse")
    is_configured_rm_ord_routes = fields.Boolean(string="Configured Removal Order Routes", default=False,
                                                 help="Configured Removal Order Routes")

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active

    @api.constrains('is_global_warehouse_in_fba')
    def check_removal_config(self):
        if len(self.env['amazon.instance.ept'].search(
                [('is_global_warehouse_in_fba', '=', True), ('seller_id', '=', self.seller_id.id)]).ids) > 1:
            raise Warning("Default Removal configuration allow only marketplace per seller")

    def create_sellable_route(self, warehouse_id, fba_warehouse_id):
        """
            Create sellable routes and pull/procurement rules for amazon removal order.
        """
        stock_location_route_obj = self.env['stock.location.route']
        stock_location_obj = self.env['stock.location']

        fba_sellable_location_id = fba_warehouse_id and fba_warehouse_id.lot_stock_id or False
        sellable_location_id = warehouse_id and warehouse_id.lot_stock_id or False
        if sellable_location_id and fba_sellable_location_id:
            location_id = stock_location_obj.search(
                ['|', ('company_id', '=', False), ('company_id', '=', fba_warehouse_id.company_id.id),
                 ('usage', '=', 'transit')], limit=1)
            stock_picking_type_id = fba_warehouse_id.out_type_id
            pull1_vals = {
                'name': '%s Sellable to Transit' % (fba_warehouse_id.code),
                'action': 'pull',
                'location_src_id': fba_sellable_location_id.id,
                'procure_method': 'make_to_stock',
                'location_id': location_id and location_id.id or False,
                'picking_type_id': stock_picking_type_id and stock_picking_type_id.id or False,
                'warehouse_id': warehouse_id.id
            }

            pull2_stock_picking_type_id = warehouse_id.in_type_id
            pull2_vals = {
                'name': 'Transit to %s Transit' % (warehouse_id.code),
                'action': 'pull',
                'location_src_id': location_id and location_id.id or False,
                'procure_method': 'make_to_order',
                'location_id': sellable_location_id and sellable_location_id.id or False,
                'picking_type_id': pull2_stock_picking_type_id and pull2_stock_picking_type_id.id or False,
                'warehouse_id': warehouse_id.id
            }
            vals = {
                'name': '%s Sellable to %s Sellable' % (fba_warehouse_id.name, warehouse_id.name),
                'rule_ids': [(0, 0, pull1_vals), (0, 0, pull2_vals)],
                'supplied_wh_id': warehouse_id.id,
                'supplier_wh_id': fba_warehouse_id.id
            }
            sellable_route_id = stock_location_route_obj.create(vals)
            return sellable_route_id or False
        return False

    def create_unsellable_route(self, warehouse_id, fba_warehouse_id):
        """
            Create unsellable routes and pull/procurement rules for amazon removal order.
        """
        stock_location_route_obj = self.env['stock.location.route']
        stock_location_obj = self.env['stock.location']
        stock_picking_type_obj = self.env['stock.picking.type']

        fba_unsellable_location_id = fba_warehouse_id and fba_warehouse_id.unsellable_location_id or False
        unsellable_location_id = warehouse_id and warehouse_id.unsellable_location_id or False
        if not unsellable_location_id:
            unsellable_location_id = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1)

        if fba_unsellable_location_id and unsellable_location_id:
            location_id = stock_location_obj.search(
                ['|', ('company_id', '=', False), ('company_id', '=', fba_warehouse_id.company_id.id),
                 ('usage', '=', 'transit')], limit=1)
            stock_picking_type_id = fba_warehouse_id.out_type_id
            pull1_vals = {
                'name': '%s Unsellable to Transit' % (fba_warehouse_id.code),
                'action': 'pull',
                'location_src_id': fba_unsellable_location_id.id,
                'procure_method': 'make_to_stock',
                'location_id': location_id and location_id.id or False,
                'picking_type_id': stock_picking_type_id and stock_picking_type_id.id or False,
                'warehouse_id': warehouse_id.id
            }
            pull2_stock_picking_type_id = stock_picking_type_obj.search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', warehouse_id.id)], limit=1)
            pull2_vals = {
                'name': '%s to %s Transit' % (fba_warehouse_id.code, warehouse_id.code),
                'action': 'pull',
                'location_src_id': location_id and location_id.id or False,
                'procure_method': 'make_to_order',
                'location_id': unsellable_location_id and unsellable_location_id.id or False,
                'picking_type_id': pull2_stock_picking_type_id and pull2_stock_picking_type_id.id or False,
                'warehouse_id': warehouse_id.id,
            }
            vals = {
                'name': '%s Unsellable to %s Unsellable' % (fba_warehouse_id.code, warehouse_id.code),
                'is_removal_order': True,
                'supplied_wh_id': warehouse_id.id,
                'supplier_wh_id': fba_warehouse_id.id,
                'rule_ids': [(0, 0, pull1_vals), (0, 0, pull2_vals)]
            }
            unsellable_route_id = stock_location_route_obj.create(vals)
            return unsellable_route_id or False
        return False

    @api.multi
    def update_unsellable_route(self, fba_warehouse_id, removal_order_config_ids):
        """
            Update unsellable routes and pull/procurement rules for amazon removal order.
            @return: True
        """
        stock_location_obj = self.env['stock.location']

        unsellable_route_id = False
        for removal_order_config_id in removal_order_config_ids:
            if removal_order_config_id.removal_disposition == "Return":
                unsellable_route_id = removal_order_config_id.unsellable_route_id or False

        fba_unsellable_location_id = fba_warehouse_id and fba_warehouse_id.unsellable_location_id or False
        for pull_id in (unsellable_route_id.rule_ids if unsellable_route_id else []):
            if pull_id.procure_method == "make_to_stock":
                location_id = stock_location_obj.search(
                    ['|', ('company_id', '=', False), ('company_id', '=', fba_warehouse_id.company_id.id),
                     ('usage', '=', 'transit')], limit=1)
                stock_picking_type_id = fba_warehouse_id.out_type_id
                cha_pull1_vals = {
                    'name': '%s Unsellable to Transit' % (fba_warehouse_id.code),
                    'location_src_id': fba_unsellable_location_id.id,
                    'location_id': location_id and location_id.id or False,
                    'picking_type_id': stock_picking_type_id and stock_picking_type_id.id or False
                }
                pull_id.write(cha_pull1_vals)
        return True

    @api.one
    def configure_amazon_removal_order_routes(self):
        """
            Create routes and pull/procurement rules for amazon removal order.
            @return: True
        """
        self.ensure_one()
        if self.is_global_warehouse_in_fba and self.removal_order_config_ids:
            fba_warehouse_id = self.fba_warehouse_id or False
            removal_order_config_ids = self.removal_order_config_ids
            self.update_unsellable_route(fba_warehouse_id, removal_order_config_ids)

        if self.is_global_warehouse_in_fba and not self.removal_order_config_ids:
            stock_picking_type_obj = self.env['stock.picking.type']
            stock_location_obj = self.env['stock.location']

            warehouse_id = self.removal_warehouse_id or False
            fba_warehouse_id = self.fba_warehouse_id or False
            if not warehouse_id or not fba_warehouse_id:
                return True

            unsellable_route_id = self.create_unsellable_route(warehouse_id, fba_warehouse_id) or False
            sellable_route_id = self.create_sellable_route(warehouse_id, fba_warehouse_id) or False
            if unsellable_route_id and sellable_route_id:
                vals = {
                    'removal_disposition': 'Return',
                    'unsellable_route_id': unsellable_route_id.id,
                    'sellable_route_id': sellable_route_id.id,
                }
                self.removal_order_config_ids = [(0, 0, vals)]

            disp_picking_type_id = stock_picking_type_obj.search(
                [('warehouse_id', '=', warehouse_id.id), ('code', '=', 'outgoing')], limit=1)
            disp_location_id = stock_location_obj.search([('usage', '=', 'inventory'), ('scrap_location', '=', True)],
                                                         limit=1)
            if disp_picking_type_id and disp_location_id:
                vals = {
                    'removal_disposition': 'Disposal',
                    'location_id': disp_location_id.id,
                    'picking_type_id': disp_picking_type_id.id,
                }
                self.removal_order_config_ids = [(0, 0, vals)]

        return True

    def _fba_count_all(self):
        inbound_shipment_plan_ept_obj = self.env['inbound.shipment.plan.ept']
        inbound_shipment_ept_obj = self.env['amazon.inbound.shipment.ept']
        for instance in self:
            instance.fba_sale_order_count = len(instance.amazon_fba_sale_order_ids)
            instance.fba_quotation_count = len(instance.fba_quotation_ids)
            instance.fba_order_count = len(instance.fba_order_ids)
            instance.fba_return_delivery_order_count = len(instance.fba_return_delivery_order_ids)

            draft_inbound_shipment_plans = inbound_shipment_plan_ept_obj.search(
                [('instance_id', '=', instance.id), ('state', '=', 'draft')])
            instance.count_draft_inbound_shipment_plan = len(draft_inbound_shipment_plans)
            approved_inbound_shipment_plans = inbound_shipment_plan_ept_obj.search(
                [('instance_id', '=', instance.id), ('state', '=', 'plan_approved')])
            instance.count_approved_inbound_shipment_plan = len(approved_inbound_shipment_plans)

            working_inbound_shipments = inbound_shipment_ept_obj.search(
                [('shipment_plan_id.instance_id', '=', instance.id), ('state', '=', 'WORKING')])
            instance.count_working_inbound_shipment = len(working_inbound_shipments)
            shipped_inbound_shipments = inbound_shipment_ept_obj.search(
                [('shipment_plan_id.instance_id', '=', instance.id), ('state', '=', 'SHIPPED')])
            instance.count_shipped_inbound_shipment = len(shipped_inbound_shipments)
            cancelled_inbound_shipments = inbound_shipment_ept_obj.search(
                [('shipment_plan_id.instance_id', '=', instance.id), ('state', '=', 'CANCELLED')])
            instance.count_cancelled_inbound_shipment = len(cancelled_inbound_shipments)
            closed_inbound_shipments = inbound_shipment_ept_obj.search(
                [('shipment_plan_id.instance_id', '=', instance.id), ('state', '=', 'CLOSED')])
            instance.count_closed_inbound_shipment = len(closed_inbound_shipments)

    def _count_all(self):
        for instance in self:
            instance.product_count = len(instance.ept_product_ids)
            instance.sale_order_count = len(instance.amazon_sale_order_ids)
            instance.picking_count = len(instance.picking_ids)
            instance.invoice_count = len(instance.invoice_ids)
            instance.exported_product_count = len(instance.exported_product_ids)
            instance.ready_to_expor_product_count = len(instance.ready_to_expor_product_ids)

            instance.quotation_count = len(instance.quotation_ids)
            instance.order_count = len(instance.order_ids)
            instance.confirmed_picking_count = len(instance.confirmed_picking_ids)
            instance.assigned_picking_count = len(instance.assigned_picking_ids)
            instance.partially_available_picking_count = len(
                instance.partially_available_picking_ids)
            instance.done_picking_count = len(instance.done_picking_ids)
            instance.open_invoice_count = len(instance.open_invoice_ids)
            instance.paid_invoice_count = len(instance.paid_invoice_ids)
            instance.refund_invoice_count = len(instance.refund_invoice_ids)

    color = fields.Integer(string='Color Index')

    exported_product_ids = fields.One2many('amazon.product.ept', 'instance_id',
                                           string='Exported Products',
                                           domain=[('exported_to_amazon', '=', True)])
    exported_product_count = fields.Integer(compute='_count_all', string="Exported Product")

    ready_to_expor_product_ids = fields.One2many('amazon.product.ept', 'instance_id',
                                                 domain=[('exported_to_amazon', '=', False)],
                                                 string="Ready To Export")
    ready_to_expor_product_count = fields.Integer(compute='_count_all', string="Ready For Export")

    # amazon_browse_node_ids = fields.One2many('amazon.browse.node.ept', 'instance_id',
    # string='Categories')
    node_count = fields.Integer(compute='_count_all', string="Browse Node")
    ept_product_ids = fields.One2many('amazon.product.ept', 'instance_id', string='Product')
    product_count = fields.Integer(compute='_count_all', string="Products")
    amazon_sale_order_ids = fields.One2many('sale.order', 'amz_instance_id', string='Order')
    sale_order_count = fields.Integer(compute='_count_all', string="Orders")
    picking_ids = fields.One2many('stock.picking', 'amazon_instance_id', string="Picking")
    picking_count = fields.Integer(compute='_count_all', string="Pickings")
    invoice_ids = fields.One2many('account.invoice', 'amazon_instance_id', string="Invoice")
    invoice_count = fields.Integer(compute='_count_all', string="Invoices")

    quotation_ids = fields.One2many('sale.order', 'amz_instance_id',
                                    domain=[('state', 'in', ['draft', 'sent'])], string="Quotation")
    quotation_count = fields.Integer(compute='_count_all', string="Quotations")

    order_ids = fields.One2many('sale.order', 'amz_instance_id',
                                domain=[('state', 'not in', ['draft', 'sent', 'cancel'])],
                                string="Sales Order")
    order_count = fields.Integer(compute='_count_all', string="Sales Orders")

    confirmed_picking_ids = fields.One2many('stock.picking', 'amazon_instance_id',
                                            domain=[('state', '=', 'confirmed')],
                                            string="Confirm Picking")
    confirmed_picking_count = fields.Integer(compute='_count_all', string="Confirm Pickings")
    assigned_picking_ids = fields.One2many('stock.picking', 'amazon_instance_id',
                                           domain=[('state', '=', 'assigned')],
                                           string="Assigned Picking")
    assigned_picking_count = fields.Integer(compute='_count_all', string="Assigned Pickings")
    partially_available_picking_ids = fields.One2many('stock.picking', 'amazon_instance_id',
                                                      domain=[
                                                          ('state', '=', 'partially_available')],
                                                      string="Partially Available Picking")
    partially_available_picking_count = fields.Integer(compute='_count_all',
                                                       string="Partially Available Pickings")
    done_picking_ids = fields.One2many('stock.picking', 'amazon_instance_id',
                                       domain=[('state', '=', 'done')], string="Done Picking")
    done_picking_count = fields.Integer(compute='_count_all', string="Done Pickings")

    open_invoice_ids = fields.One2many('account.invoice', 'amazon_instance_id',
                                       domain=[('state', '=', 'open'),
                                               ('type', '=', 'out_invoice')], string="Open Invoice")
    open_invoice_count = fields.Integer(compute='_count_all', string="Open Invoices")

    paid_invoice_ids = fields.One2many('account.invoice', 'amazon_instance_id',
                                       domain=[('state', '=', 'paid'),
                                               ('type', '=', 'out_invoice')], string="Paid Invoice")
    paid_invoice_count = fields.Integer(compute='_count_all', string="Paid Invoices")

    refund_invoice_ids = fields.One2many('amazon.order.refund.ept', 'instance_id',
                                         string="Refund Invoice")
    refund_invoice_count = fields.Integer(compute='_count_all', string="Refund Invoices")

    @api.multi
    def test_amazon_connection(self):
        proxy_data = self.seller_id.get_proxy_server()
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        flag = False

        kwargs = {'merchant_id': self.merchant_id and str(self.merchant_id) or False,
                  'auth_token': self.auth_token and str(self.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'test_amazon_connection',
                  'dbuuid': dbuuid,
                  'amazon_marketplace_code': self.country_id.amazon_marketplace_code or self.country_id.code,
                  'proxies': proxy_data, }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/verify_iap', params=kwargs)
        if response.get('result'):
            flag = response.get('result')
        else:
            raise Warning(response.get('reason'))

        if flag:
            raise Warning('Service working properly')
        return True

    @api.multi
    def update_changes(self):
        return True

    @api.multi
    def write(self, vals):
        res = super(amazon_instace_ept, self).write(vals)
        if 'access_key' in vals or 'secret_key' in vals or \
                'market_place_id' in vals or 'merchant_id' in vals or \
                'pro_advt_access_key' in vals or 'pro_advt_scrt_access_key' in vals or \
                'pro_advt_associate_tag' in vals:
            user_object = self.env.user
            for instance in self:
                partner_ids = []
                for follower in instance.message_follower_ids:
                    partner_ids.append(follower.partner_id.id)
                body = 'Amazon credentials are updated by %s.' % (user_object.name)
                instance.message_post(body=body, subject='Amazon Credentials Updated',
                                      message_type='notification', partner_ids=partner_ids)
        return res

    @api.multi
    def show_amazon_credential(self):
        form = self.env.ref('amazon_ept.amazon_instance_credential_form', False)
        return {
            'name': _('Amazon MWS Credential'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.instance.ept',
            'view_id': form.id,
            'nodestroy': True,
            'target': 'new',
            'context': {},
            'res_id': self and self.ids[0] or False,
        }

    @api.multi
    def action_view_products(self):
        action = self.env.ref('amazon_ept.action_amazon_product_ept', False)
        result = action and action.read()[0] or {}
        result['domain'] = "[('instance_id','in',[" + ','.join(map(str, self.ids)) + "])]"
        return result

    #     @api.multi
    #     def action_view_browse_node(self):
    #         action = self.env.ref('amazon_ept.action_amazon_browse_node_ept', False)
    #         result = action and action.read()[0] or {}
    #         result['domain'] = "[('instance_id','in',[" + ','.join(map(str, self.ids)) + "])]"
    #         return result

    @api.one
    @api.constrains('warehouse_id', 'company_id', 'fba_warehouse_id', 'company_id')
    def onchange_company_warehouse_id(self):
        if self.warehouse_id and self.company_id and self.warehouse_id.company_id.id != self.company_id.id:
            raise Warning(
                "Company in warehouse is different than the selected company."
                " Selected Company and Warehouse company must be same.")

    @api.onchange('company_id')
    def onchange_company_id(self):
        vals = {}
        domain = {}
        if self.company_id:
            journals = self.env['account.journal'].search(
                [('company_id', '=', self.company_id.id), ('type', 'in', ['cash', 'bank'])])
            domain['settlement_report_journal_id'] = [('id', 'in', journals.ids)]
        else:
            domain['settlement_report_journal_id'] = [('id', 'in', [])]
        vals.update({'domain': domain})
        return vals

    @api.model
    def auto_create_outbound_order(self, args={}):
        """
            This function trigger to instance wise automatic create out-bound orders.
            @return: True
        """

        amazon_seller_obj = self.env['amazon.seller.ept']
        amazon_instance_obj = self.env['amazon.instance.ept']
        sale_order_obj = self.env['sale.order']
        amazon_product_obj = self.env['amazon.product.ept']

        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        active_seller_id = args.get('seller_id', False)
        seller = active_seller_id and amazon_seller_obj.search(
            [('id', '=', active_seller_id)]) or False
        instance_ids = seller and amazon_instance_obj.search([('seller_id', '=', seller.id)])

        if seller:

            """Changes by Dhruvi all these fields are fetched according to seller wise."""
            fulfillment_action = seller.fulfillment_action
            shipment_service_level_category = seller.shipment_service_level_category
            fulfillment_policy = seller.fulfillment_policy
            notify_by_email = seller.notify_by_email or False

            for instance in instance_ids:
                fba_warehouse = instance.fba_warehouse_id or False

                """Changes by Dhruvi
                    default_fba_partner_id is fetched according to seller wise."""
                def_fba_partner_id = seller.def_fba_partner_id or False

                _amazon_sale_order_domain = [
                    ('warehouse_id', '=', fba_warehouse and fba_warehouse.id or False),
                    ('partner_id', '!=', def_fba_partner_id and def_fba_partner_id.id or False),
                    ('state', '=', 'draft')
                ]

                sale_orders = sale_order_obj.search(_amazon_sale_order_domain)
                for sale_order in sale_orders:
                    if not sale_order.order_line:
                        continue

                    if not sale_order.amz_fulfillment_instance_id:
                        sale_order.write({
                            'amz_instance_id': instance.id,
                            'amz_fulfillment_instance_id': instance.id,
                            'amz_fulfillment_action': fulfillment_action,
                            'warehouse_id': fba_warehouse and fba_warehouse.id or False,
                            'pricelist_id': instance.pricelist_id and
                                            instance.pricelist_id.id or False,
                            'amz_fulfillment_policy': fulfillment_policy,
                            'amz_shipment_service_level_category': shipment_service_level_category,
                            'amz_is_outbound_order': True,
                            'notify_by_email': notify_by_email,
                            'amazon_reference': sale_order.name,
                            'note': sale_order.note or sale_order.name

                        })

                    create_order = True
                    data = sale_order.get_data()
                    for line in sale_order.order_line:
                        if line.product_id.type == 'service':
                            continue
                        if line.product_id:
                            amz_product = amazon_product_obj.search(
                                [('product_id', '=', line.product_id and line.product_id.id),
                                 ('instance_id', '=', instance.id), ('fulfillment_by', '=', 'AFN')],
                                limit=1)
                            if not amz_product:
                                create_order = False
                                break
                            line.write({'amazon_product_id': amz_product.id})
                    if create_order:
                        kwargs = {'merchant_id': seller.merchant_id and str(seller.merchant_id) or False,
                                  'auth_token': seller.auth_token and str(seller.auth_token) or False,
                                  'app_name': 'amazon_ept',
                                  'account_token': account.account_token,
                                  'emipro_api': 'auto_create_outbound_order',
                                  'dbuuid': dbuuid,
                                  'amazon_marketplace_code': seller.country_id.amazon_marketplace_code or
                                                             seller.country_id.code,
                                  'data': data, }

                        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
                        if response.get('reason'):
                            pass
                        else:
                            self._cr.commit()

        return True

    """Here We have checked if root node exist or not.
        If root node is not exist then we can create root node as an base(parent) node
    """

    @api.model
    def check_root_node_exist(self, records):
        vals = {}
        browse_node = False
        browse_node_obj = self.env['amazon.browse.node.ept']
        for record in records:
            browse_node = browse_node_obj.search(
                [('ama_category_code', '=', record.eco_category_code),
                 ('country_id', '=', self.country_id.id),
                 ('name', '=', record.name)])
            if not browse_node:
                vals = {'ama_category_code': record.eco_category_code,
                        'name': record.name,
                        'country_id': self.country_id.id}
                browse_node_obj.create(vals)
        return True

    """Here We Import child browse node from an product advertising api"""

    @api.multi
    def import_browse_node_ept(self):
        base_browse_node_obj = self.env['amazon.base.browse.node.ept']
        records = base_browse_node_obj.search([('country_id', '=', self.country_id.id)])
        self.check_root_node_exist(records)
        return True

    #     @api.multi
    #     def import_sales_order_ept(self):
    #         self.env['sale.order'].import_sales_order(self)
    #         #self.write({'order_last_sync_on':datetime.now()})
    #         return True

    #     @api.model
    #     def auto_import_sale_order_ept(self):
    #         sale_order_obj=self.env['sale.order']
    #         ctx = dict(self._context) or {}
    #         instance_id = ctx.get('instance_id',False)
    #         if instance_id:
    #             instance=self.search([('id','=',instance_id)])
    #             sale_order_obj.import_sales_order(instance)
    #             instance.write({'order_last_sync_on':datetime.now()})
    #         return True

    @api.multi
    def update_order_status(self):
        self.env['sale.order'].amz_update_order_status(self.seller_id, [self.market_place_id])
        self.write({'shipment_last_sync_on': datetime.now()})
        return True

    @api.multi
    def export_stock_levels(self):
        self.env['amazon.product.ept'].export_stock_levels(self)
        self.write({'inventory_last_sync_on': datetime.now()})
        return True

#     @api.model
#     def auto_export_inventory_ept(self):
#         amazon_product_obj=self.env['amazon.product.ept']
#         ctx = dict(self._context) or {}
#         instance_id = ctx.get('instance_id',False)
#         if instance_id:
#             instance=self.search([('id','=',instance_id)])
#             amazon_product_obj.export_stock_levels(instance)
#             instance.write({'inventory_last_sync_on':datetime.now()})
# 
#         return True
