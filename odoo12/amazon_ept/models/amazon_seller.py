# from __builtin__ import True
from datetime import datetime, date
from odoo import models, fields, api
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
from odoo.addons.iap.models import iap

from ..endpoint import DEFAULT_ENDPOINT

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}


class amazon_seller_ept(models.Model):
    _name = "amazon.seller.ept"
    _description = 'amazon.seller.ept'

    # added by Dhruvi
    help_fulfillment_action = """ 
        Ship - The fulfillment order ships now

        Hold - An order hold is put on the fulfillment order.3

        Default: Ship in Create Fulfillment
        Default: Hold in Update Fulfillment    
    """

    help_fulfillment_policy = """ 

        FillOrKill - If an item in a fulfillment order is determined to be unfulfillable before 
                    any shipment in the order moves to the Pending status (the process of picking 
                    units from inventory has begun), then the entire order is considered 
                    unfulfillable. However, if an item in a fulfillment order is determined 
                    to be unfulfillable after a shipment in the order moves to the Pending status, 
                    Amazon cancels as much of the fulfillment order as possible

        FillAll - All fulfillable items in the fulfillment order are shipped. 
                The fulfillment order remains in a processing state until all items are either 
                shipped by Amazon or cancelled by the seller

        FillAllAvailable - All fulfillable items in the fulfillment order are shipped. 
            All unfulfillable items in the order are cancelled by Amazon.

        Default: FillOrKill
    """

    @api.model
    def _default_journal(self):
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', list(filter(None, list(map(TYPE2JOURNAL.get, inv_types))))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    """Added by Dhruvi [28-08-2018]
    method to set default value for default fba customer"""

    @api.model
    def _get_default_fba_partner_id(self):

        try:
            return self.env.ref('amazon_ept.amazon_fba_pending_order')
        except:
            pass

    @api.model
    def _get_default_fba_auto_workflow(self):
        try:
            return self.env.ref('auto_invoice_workflow_ept.automatic_validation_ept')
        except:
            pass

    auto_process_shipment_report = fields.Boolean(string='Auto Process Shipment Report?')
    auto_import_shipment_report = fields.Boolean(string='Auto Import Shipment Report?')
    shipping_report_last_sync_on = fields.Datetime("Last Shipping Report Request Time")
    inventory_report_last_sync_on = fields.Datetime("Last Inventory Report Request Time")
    return_report_last_sync_on = fields.Datetime("Last Return Report Request Time")
    auto_process_return_report = fields.Boolean(string='Auto Process Return Report?')
    auto_import_return_report = fields.Boolean(string='Auto Import Return Report?')
    auto_check_cancel_order = fields.Boolean(string='Auto chack canceled order in Amazon?')
    auto_import_fba_pending_order = fields.Boolean(string='Auto Import FBA Pending Order?')
    fba_order_last_sync_on = fields.Datetime("Last FBA Order Sync Time")
    fba_pending_order_last_sync_on = fields.Datetime("Last FBA Pending Order Sync Time")
    auto_import_inboud_shipment_status = fields.Boolean(
        string='Auto Import FBA Inbound Shipment Item Status?')
    auto_update_small_parcel_tracking = fields.Boolean(
        'Auto Update Small Parcel(Non Partnered) Tracking')
    reimbursement_customer_id = fields.Many2one("res.partner", string="Reimbursement Customer")
    reimbursement_product_id = fields.Many2one("product.product", string="Product")
    sale_journal_id = fields.Many2one('account.journal', string='Sales Journal',
                                      default=_default_journal, domain=[('type', '=', 'sale')])
    auto_update_ltl_parcel_tracking = fields.Boolean("Auto Update Ltl Parcel Tracking",
                                                     default=False, copy=False)
    reimbursed_warehouse_id = fields.Many2one("stock.warehouse", string="Reimbursed warehouse id")

    is_another_soft_create_fba_shipment = fields.Boolean(
        string="Does another software create the FBA shipment reports?", default=False)
    fba_shipment_report_days = fields.Integer("Default Shipment Request Report Days", default=3)

    def_fba_partner_id = fields.Many2one('res.partner',
                                         string='Default Customer for FBA pending order',
                                         default=_get_default_fba_partner_id)
    fba_auto_workflow_id = fields.Many2one('sale.workflow.process.ept', string='Auto Workflow (FBA)',
                                           default=_get_default_fba_auto_workflow)
    # Outbound Order
    is_auto_create_outbound_order = fields.Boolean(string="Auto Create Outbound Order ?",
                                                   default=False,
                                                   help="This box is ticked to automatically create "
                                                        "Outbound Order.")
    fulfillment_action = fields.Selection([('Ship', 'Ship'), ('Hold', 'Hold')],
                                          string="Fulfillment Action", help=help_fulfillment_action)
    shipment_service_level_category = fields.Selection(
        [('Expedited', 'Expedited'), ('NextDay', 'NextDay'), ('SecondDay', 'SecondDay'),
         ('Standard', 'Standard'),
         ('Priority', 'Priority'), ('ScheduledDelivery', 'ScheduledDelivery')], "Shipment Category",
        help="Amazon shipment category")
    fulfillment_policy = fields.Selection(
        [('FillOrKill', 'FillOrKill'), ('FillAll', 'FillAll'),
         ('FillAllAvailable', 'FillAllAvailable')], string="Fulfillment Policy",
        help=help_fulfillment_policy)
    notify_by_email = fields.Boolean("Notify By Email", default=False,
                                     help="If true then system will notify by email to followers")
    unsellable_location_id = fields.Many2one('stock.location', string="Unsellable Location")

    # added by dhaval
    is_default_odoo_sequence_in_sales_order_fba = fields.Boolean(
        "Is default Odoo Sequence In Sales Orders (FBA) ?")

    # Added by Twinkal [29-07-2019]
    is_pan_european = fields.Boolean('Is Pan European ?')
    # Added by Twinkal [30-07-2019]
    is_reserved_qty_included_inventory_report = fields.Boolean(
        string='Is Reserved Qyantity to be included FBA Live Inventory Report?')
    validate_stock_inventory_for_report = fields.Boolean(
        "Auto Validate Amazon FBA Live Stock Report")
    auto_import_product_stock = fields.Boolean(
        "Auto Import Amazon FBA Live Stock Report")
    auto_process_fba_live_stock_report = fields.Boolean(
        string='Auto Process FBA Live Stock Report?')

    # added by twinkal 20 august 2019
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')],
                                      'Fulfillment By ?', default='FBM')

    is_another_soft_create_fba_inventory = fields.Boolean(
        string="Does another software create the FBA Inventory reports?", default=False)

    """
    Add Field 'fulfillment_latency' for export inventory process
    @author: Deval Jagad (21/12/2019)
    """
    fulfillment_latency = fields.Integer('Fullfillment Latency')


    other_pan_europe_country_ids = fields.Many2many('res.country', 'other_pan_europe_country_seller_rel',
                                                    'res_marketplace_id',
                                                    'country_id', "Other Pan Europe Countries")

    "Added by twinkal[5/12/2019]"
    cron_count = fields.Integer("Scheduler Count",
                                compute="get_scheduler_list",
                                help="This Field relocates Scheduler Count.")

    def list_of_seller_cron(self):
        seller_cron = self.env['ir.cron'].search([('amazon_seller_cron_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(seller_cron.ids) + " )]",
            'name': 'Cron Scheduler',
            'view_mode': 'tree,form',
            'res_model': 'ir.cron',
            'type': 'ir.actions.act_window',
        }
        return action

    def fbm_cron_configuration_action(self):
        action = self.env.ref('amazon_ept.action_wizard_fbm_cron_configuration_ept').read()[0]
        context = {
            'amz_seller_id': self.id,
            'amazon_selling': self.amazon_selling
        }
        action['context'] = context
        return action

    def fba_cron_configuration_action(self):
        action = self.env.ref('amazon_ept.action_wizard_fba_cron_configuration_ept').read()[0]
        context = {
            'amz_seller_id': self.id,
            'amazon_selling': self.amazon_selling
        }
        action['context'] = context
        return action

    def global_cron_configuration_action(self):
        action = self.env.ref('amazon_ept.action_wizard_global_cron_configuration_ept').read()[0]
        context = {
            'amz_seller_id': self.id,
            'amazon_selling': self.amazon_selling
        }
        action['context'] = context
        return action

    @api.model
    def auto_import_fba_pending_sale_order_ept(self, args={}):
        sale_order_obj = self.env['sale.order']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.browse(int(seller_id))
            sale_order_obj.import_fba_pending_sales_order(seller)
            seller.write({'fba_order_last_sync_on': datetime.now()})
        return True

    @api.model
    def auto_check_cancel_order_in_amazon(self, args={}):
        sale_order_obj = self.env['sale.order']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.env['amazon.seller.ept'].browse(int(seller_id))
            sale_order_obj.with_context({'auto_process': True}).check_cancel_order_in_amazon(seller)
        return True

    @api.model
    def get_scheduler_list(self):
        seller_cron = self.env['ir.cron'].search([('amazon_seller_cron_id', '=', self.id)])
        for record in self:
            record.cron_count = len(seller_cron.ids)

    @api.model
    def auto_import_fba_shipment_status_ept(self, args={}):
        inbound_shipment_obj = self.env['amazon.inbound.shipment.ept']
        seller_id = args.get('seller_id', False)
        if seller_id:
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller_id)])
            shipments = inbound_shipment_obj.search([('state', 'not in',
                                                      ['draft', 'CLOSED', 'CANCELLED', 'DELETED',
                                                       'ERROR', 'WORKING']), (
                                                         'shipment_plan_id.instance_id', 'in',
                                                         instances.ids)])
            for shipment in shipments:
                shipment.with_context(is_auto_process=True).check_status()
                self._cr.commit()
            shipments = inbound_shipment_obj.search(
                [('closed_date', '!=', False), ('state', 'in', ['CLOSED']),
                 ('shipment_plan_id.instance_id.check_status_days', '>', 0),
                 ('shipment_plan_id.instance_id', 'in', instances.ids),
                 ('is_finally_closed', '=', False)])
            for shipment in shipments:
                instance = shipment.shipment_plan_id.instance_id
                closed_date = datetime.strptime(shipment.closed_date, "%Y-%m-%d")
                closed_date = date(day=closed_date.day, month=closed_date.month,
                                   year=closed_date.year)
                closed_date = closed_date + relativedelta(days=instance.check_status_days)
                today_date = date.today()
                if today_date <= closed_date:
                    shipment.with_context(is_auto_process=True).check_status()
                    self._cr.commit()
                over_days = (today_date - closed_date).days
                if over_days >= 0:
                    shipment.write({'is_finally_closed': True})

            shipments = inbound_shipment_obj.search(
                [('state', 'not in', ['draft', 'CLOSED', 'CANCELLED', 'DELETED', 'ERROR']),
                 ('shipment_plan_id.instance_id', 'in', instances.ids), ('is_partnered', '=', True),
                 ('transport_state', 'in', ['CONFIRMING', 'CONFIRMED'])])
            for shipment in shipments:
                shipment.with_context(is_auto_process=True).check_status()
                self._cr.commit()
        return True

    def _get_default_company_id(self):
        return self.env.user.company_id.id

    """Added by Dhruvi [28-08-2018]
    Defualt value set for all shipment fees"""

    @api.model
    def _get_default_shipment_amzon_fee(self):
        return self.env.ref('amazon_ept.product_product_amazon_shipping_ept')

    @api.model
    def _get_default_gift_wrapper_fee(self):
        return self.env.ref('amazon_ept.product_product_amazon_giftwrapper_fee')

    @api.model
    def _get_default_promotion_discount(self):
        return self.env.ref('amazon_ept.product_product_amazon_promotion_discount')

    @api.model
    def _get_default_shipment_discount(self):
        return self.env.ref('amazon_ept.product_product_amazon_shipment_discount')

    @api.model
    def _get_default_payment_term(self):
        return self.env.ref('account.account_payment_term_immediate')

    @api.model
    def _get_default_auto_workflow(self):
        return self.env.ref('auto_invoice_workflow_ept.automatic_validation_ept')

    name = fields.Char(size=120, string='Name', required=True)
    access_key = fields.Char("Access Key")
    secret_key = fields.Char("Secret Key")
    merchant_id = fields.Char("Merchant Id")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=_get_default_company_id)
    order_last_sync_on = fields.Datetime("Last FBM Order Sync Time")



    pro_advt_access_key = fields.Char("Pro Access Key")
    pro_advt_scrt_access_key = fields.Char("Secret Access Key")
    pro_advt_associate_tag = fields.Char("Associate Tag")
    country_id = fields.Many2one('res.country', string="Region",
                                 domain="[('amazon_marketplace_code','!=',False)]")
    warehouse_ids = fields.One2many('stock.warehouse', 'seller_id', string='Warehouses')
    marketplace_ids = fields.One2many('amazon.marketplace.ept', 'seller_id', string='Marketplaces')

    stock_auto_export = fields.Boolean(string="Stock Auto Export?")
    settlement_report_auto_create = fields.Boolean("Auto Create Settlement Report ?", default=False)
    settlement_report_auto_process = fields.Boolean("Auto Process Settlement Report ?",
                                                    default=False)
    auto_send_invoice = fields.Boolean("Auto Send Invoice Via Email ?", default=False)
    shipment_last_sync_on = fields.Datetime("Last Shipment Sync Time")
    order_auto_update = fields.Boolean("Auto Update Order Shipment ?", default=False)
    settlement_report_last_sync_on = fields.Datetime("Settlement Report Last Sync Time")
    transaction_line_ids = fields.One2many('amazon.transaction.line.ept', 'seller_id',
                                           'Transactions')
    create_new_product = fields.Boolean('Allow to create new product if not found in odoo ?',
                                        default=False)
    auto_send_refund = fields.Boolean("Auto Send Refund Via Email ?", default=False)
    # Proxy Server Fields
    proxy_server_type = fields.Selection([('http', 'Http'),
                                          ('https', 'Https'),
                                          ('ftp', 'Ftp')], string='Server Type')
    proxy_server_url = fields.Char('URL')
    proxy_server_port = fields.Char('Port')

    order_auto_import_xml_or_flat = fields.Boolean(string='Auto Import FBM Order?')
    import_shipped_fbm_orders = fields.Boolean(
        "Import FBM Shipped Orders")  # import shipped   order xml
    auto_process_sale_order_report = fields.Boolean(
        string='Auto Process FBM Sale Order Report?')  # process report
    is_another_soft_create_fbm_reports = fields.Boolean(
        string="Does another software create the FBM reports?", default=False)
    create_sale_order_from_flat_or_xml_report = fields.Selection(
        [('api', 'API'), ('xml', 'Xml'), ('flat', 'Flat'), ],
        string="Create FBM Sale order from which Report?", default='api')
    instance_ids = fields.One2many("amazon.instance.ept", "seller_id", "Instances")

    # added by Dhruvi
    global_channel_id = fields.Many2one('global.channel.ept', string='Global Channel')

    shipment_charge_product_id = fields.Many2one("product.product", "Shipment Fee",
                                                 domain=[('type', '=', 'service')],
                                                 default=_get_default_shipment_amzon_fee)
    gift_wrapper_product_id = fields.Many2one("product.product", "Gift Wrapper Fee",
                                              domain=[('type', '=', 'service')],
                                              default=_get_default_gift_wrapper_fee)
    promotion_discount_product_id = fields.Many2one("product.product", "Promotion Discount",
                                                    domain=[('type', '=', 'service')],
                                                    default=_get_default_promotion_discount)
    ship_discount_product_id = fields.Many2one("product.product", "Shipment Discount",
                                               domain=[('type', '=', 'service')],
                                               default=_get_default_shipment_discount)
    order_auto_import = fields.Boolean(string='Auto Order Import?')
    auto_create_return_picking = fields.Boolean("Auto Create Return Picking ?", default=True)
    auto_create_refund = fields.Boolean("Auto Create Refund ?", default=True)

    is_default_odoo_sequence_in_sales_order = fields.Boolean(
        "Is default Odoo Sequence in Sales Orders ?")
    order_prefix = fields.Char(size=10, string='Order Prefix')
    fba_order_prefix = fields.Char(size=10, string='FBA Order Prefix')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term',
                                      default=_get_default_payment_term)
    auto_workflow_id = fields.Many2one('sale.workflow.process.ept', string='Auto Workflow (FBM)',
                                       default=_get_default_auto_workflow)
    condition = fields.Selection([('New', 'New'),
                                  ('UsedLikeNew', 'UsedLikeNew'),
                                  ('UsedVeryGood', 'UsedVeryGood'),
                                  ('UsedGood', 'UsedGood'),
                                  ('UsedAcceptable', 'UsedAcceptable'),
                                  ('CollectibleLikeNew', 'CollectibleLikeNew'),
                                  ('CollectibleVeryGood', 'CollectibleVeryGood'),
                                  ('CollectibleGood', 'CollectibleGood'),
                                  ('CollectibleAcceptable', 'CollectibleAcceptable'),
                                  ('Refurbished', 'Refurbished'),
                                  ('Club', 'Club')], string="Condition", default='New', copy=False)

    # added by dhaval
    import_shipped_fbm_orders_date = fields.Datetime("Import Shipped FBM Order Time")
    last_import_fbm_order_days = fields.Integer(string="Last Import FBM Order Days")
    developer_id = fields.Many2one('amazon.developer.details.ept', string="Developer ID")
    developer_name = fields.Char("Developer Name")
    # commented by twinkal
    #     is_own_developer_account = fields.Boolean(string="Is Own Developer Account", default=False)
    auth_token = fields.Char("Auth Token")

    auto_create_fba_stock_adj_report = fields.Boolean(
        string="Auto Create FBA Stock Adjustment Report ?")
    auto_process_fba_stock_adj_report = fields.Boolean(
        string='Auto Process FBA Stock Adjustment Report ?')
    stock_adjustment_report_last_sync_on = fields.Datetime(
        "Last Stock Adjustment Report Request Time")
    stock_adjustment_config_ids = fields.One2many('amazon.stock.adjustment.config', 'seller_id',
                                                  string="Stock Adjustment Configuration")
    inv_adjustment_report_days = fields.Integer("Inv Adjustment Report Days", default=3)

    removal_order_report_last_sync_on = fields.Datetime("Last Removal Order Report Request Time")
    auto_create_removal_order_report = fields.Boolean(string="Auto Create Removal Order Report ?")
    auto_process_removal_report = fields.Boolean(string='Auto Process FBA Removal Order Report ?')
    fba_recommended_removal_report_last_sync_on = fields.Datetime(
        "Last FBA Recommended  Report Request Time")
    auto_import_fba_recommended_report = fields.Boolean(
        'Auto FBA Recommended Removal Order Report ?')
    auto_process_fba_recommended_removal_report = fields.Boolean(
        'Auto Process FBA Recommended Removal Order Report ?')
    aggrement_order_id = fields.Many2one('sale.order', string='Aggrement Order Ref')

    # added by twinkal
    state = fields.Selection([
        ('new', 'New'),
        ('sent', 'Aggrement Sent'),
        ('sign', 'Signed'),

    ], string='Status', readonly=True, copy=False, index=True, default='new')

    removal_order_report_days = fields.Integer("Removal Order Report Days", default=3,
                                               help="Days of report to import Removal Order Report")

    customer_return_report_days = fields.Integer("Customer Return Report Days", default=3,
                                                 help="Days of report to import Customer Return Report")

    live_inv_adjustment_report_days = fields.Integer("Live Inv Adjustment Report Days", default=3,
                                                     help="Days of report to import Live inventory Report")

    """
    Add Field is_vat_inclusive_activated for Import FBM order 
    If true then doesn't add tax of amazon api into price
    @author: Deval Jagad (01/01/2020)
    """
    is_vat_inclusive_activated = fields.Boolean(string='Is vat inclusive service activated?',
                                                help="If True then not consider tax amount with price from api")

    @api.onchange('create_sale_order_from_flat_or_xml_report')
    def hide_menu(self):
        records = self.search([('id', '!=', self.id)])
        visible_menu = False
        for record in records:
            if record.create_sale_order_from_flat_or_xml_report in ['xml', 'flat']:
                visible_menu = True
        if visible_menu:
            return True
        return False

    @api.model
    def auto_update_order_status_ept(self, args={}):
        sale_order_obj = self.env['sale.order']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.search([('id', '=', seller_id)])
            sale_order_obj.amz_update_order_status(seller)
            seller.write({'shipment_last_sync_on': datetime.now()})
        return True

    @api.model
    def auto_export_inventory_ept(self, args={}):
        amazon_product_obj = self.env['amazon.product.ept']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.search([('id', '=', seller_id)])
            if not seller:
                return True
            instances = self.env['amazon.instance.ept'].search([('seller_id', '=', seller.id)])
            for instance in instances:
                amazon_product_obj.export_stock_levels(instance)
                instance.write({'inventory_last_sync_on': datetime.now()})
        return True

    @api.model
    def get_proxy_server(self):
        proxy_data = {}
        if self.proxy_server_type and self.proxy_server_url and self.proxy_server_port:
            url = self.proxy_server_url
            if len(url.split("//")) == 2:
                proxy_data = {self.proxy_server_type: "%s:%s" % (
                    self.proxy_server_url, self.proxy_server_port)}
            else:
                proxy_data = {self.proxy_server_type: "%s://%s:%s" % (
                    self.proxy_server_type, self.proxy_server_url, self.proxy_server_port)}
        return proxy_data

    def prepare_marketplace_vals(self, marketplace, participations_dict):
        """
        Prepatation of values of marketplaces to create in odoo
        :param marketplace: dict{}
        :param participations_dict: dict{}
        :return: {}
        """
        currency_obj = self.env['res.currency']
        lang_obj = self.env['res.lang']
        country_obj = self.env['res.country']
        country_code = marketplace.get('DefaultCountryCode', {}).get('value')
        name = marketplace.get('Name', {}).get('value', '')
        domain = marketplace.get('DomainName', {}).get('value', '')
        lang_code = marketplace.get('DefaultLanguageCode', {}).get('value', '')
        currency_code = marketplace.get('DefaultCurrencyCode', {}).get('value', '')
        marketplace_id = marketplace.get('MarketplaceId', {}).get('value', '')
        currency_id = currency_obj.search([('name', '=', currency_code)])
        if not currency_id:
            currency_id = currency_id.search([('name', '=', currency_code), ('active', '=', False)])
            currency_id.write({'active': True})
        lang_id = lang_obj.search([('code', '=', lang_code)])
        country_id = country_obj.search([('code', '=', country_code)])
        return {
            'seller_id': self.id,
            'name': name,
            'market_place_id': marketplace_id,
            'is_participated': participations_dict.get(marketplace_id, False),
            'domain': domain,
            'currency_id': currency_id and currency_id[0].id or False,
            'lang_id': lang_id and lang_id[0].id or False,
            'country_id': country_id and country_id[0].id or self.country_id and self.country_id.id or False,
        }

    @api.multi
    def load_marketplace(self):
        proxy_data = self.get_proxy_server()
        marketplace_obj = self.env['amazon.marketplace.ept']
        account = self.env['iap.account'].search([('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        marketplace_list = ['A2Q3Y263D00KWC', 'A2EUQ1WTGCTBG2', 'A1AM78C64UM0Y8', 'ATVPDKIKX0DER', 'A2VIGQ35RCS4UG',
                            'A1PA6795UKMFR9', 'ARBP9OOSHTCHU', 'A1RKKUPIHCS9HS', 'A13V1IB3VIYZZH', 'A1F83G8C2ARO7P',
                            'A21TJRUUN4KGV', 'APJ6JRA9NG5V4', 'A33AVAJ2PDY3EV', 'A19VAU5U5O7RUS', 'A39IBJ37TRP1C6',
                            'A1VC38T7YXB528', 'A17E79C6D8DWNP','A1805IZSGTT6HS']

        kwargs = {'merchant_id': self.merchant_id and str(self.merchant_id) or False,
                  'auth_token': self.auth_token and str(self.auth_token) or False,
                  'app_name': 'amazon_ept',
                  'account_token': account.account_token,
                  'emipro_api': 'load_marketplace',
                  'dbuuid': dbuuid,
                  'amazon_selling': self.amazon_selling,
                  'amazon_marketplace_code': self.country_id.amazon_marketplace_code or self.country_id.code,
                  'proxies': proxy_data,
                  }

        response = iap.jsonrpc(DEFAULT_ENDPOINT + '/iap_request', params=kwargs)
        if response.get('reason'):
            raise Warning(response.get('reason'))
        else:
            values = response.get('result')
            for value in values:
                participations = values[value].get('participations')
                marketplaces = values[value].get('marketplaces')
                participations_dict = dict(map(lambda x: (
                    x.get('MarketplaceId', {}).get('value', ''),
                    x.get('SellerId', {}).get('value', False)),
                                               participations))
                for marketplace in marketplaces:
                    marketplace_id = marketplace.get('MarketplaceId', {}).get('value', '')
                    if marketplace_id in marketplace_list:
                        vals = self.prepare_marketplace_vals(marketplace, participations_dict)
                        marketplace_rec = marketplace_obj.search(
                            [('seller_id', '=', self.id), ('market_place_id', '=', marketplace_id)])
                        if marketplace_rec:
                            marketplace_rec.write(vals)
                        else:
                            marketplace_obj.create(vals)
        return True

    def amazon_instance_list(self):
        instance_obj = self.env['amazon.instance.ept'].search([('seller_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(instance_obj.ids) + " )]",
            'name': 'Active Instance',
            'view_mode': 'tree,form',
            'res_model': 'amazon.instance.ept',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.model
    def auto_import_sale_order_ept(self, args):
        sale_order_obj = self.env['sale.order']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = self.search([('id', '=', seller_id)])
            seller.write({'order_last_sync_on': datetime.now()})
            if seller.order_auto_import and seller.create_sale_order_from_flat_or_xml_report == 'api':
                sale_order_obj.with_context({'is_auto_process': True}).import_sales_order(seller)

        return True

    @api.model
    def auto_import_xml_or_flat_sale_order_ept(self, args={}):
        sale_order_obj = self.env['sale.order']
        seller_id = args.get('seller_id', False)
        flag = False
        if seller_id:
            seller = self.browse(seller_id)
            if seller.order_auto_import_xml_or_flat:
                if seller.create_sale_order_from_flat_or_xml_report == 'flat':
                    flag = True
                    if args.get('is_auto_process'):
                        sale_order_obj.with_context(
                            {'is_auto_process': True}).import_sales_order_by_flat_report(seller)
                    else:
                        sale_order_obj.import_sales_order_by_flat_report(seller)
                if seller.create_sale_order_from_flat_or_xml_report == 'xml':
                    flag = True
                    sale_order_obj.with_context(
                        {'is_auto_process': True}).import_sales_order_by_xml_report(seller)

            flag and seller.write({'order_last_sync_on': datetime.now()})
        return True


class global_channel_ept(models.Model):
    _inherit = 'global.channel.ept'

    @api.model
    def create_global_channel(self, seller):
        channel_vals = {'name': seller.name}
        res = self.create(channel_vals)
        seller.update({'global_channel_id': res.id})
