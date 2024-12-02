from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.iap.models import iap
import requests
import logging
from ..endpoint import DEFAULT_ENDPOINT

_logger = logging.getLogger(__name__)



class amazon_instance_config(models.TransientModel):
    _name = 'res.config.amazon.instance'
    _description = 'res.config.amazon.instance'

    name = fields.Char("Instance Name")
    seller_id = fields.Many2one('amazon.seller.ept', string='Seller')
    marketplace_id = fields.Many2one('amazon.marketplace.ept', string='Marketplace',
                                     domain="[('seller_id','=',seller_id),"
                                            "('is_participated','=',True)]")

    @api.multi
    def create_amazon_instance(self):
        instance_exist = self.env['amazon.instance.ept'].search(
            [('seller_id', '=', self.seller_id.id),
             ('marketplace_id', '=', self.marketplace_id.id),
             ])
        if instance_exist:
            raise Warning('Instance already exist with given Credential.')

        if self.seller_id.company_id:
            company_id = self.seller_id.company_id.id
        else:
            company_id = self.env.user.company_id and self.env.user.company_id.id or False

        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', company_id)])
        if warehouse:
            warehouse_id = warehouse[0].id
        else:
            warehouse = self.env['stock.warehouse'].search([])
            warehouse_id = warehouse and warehouse[0].id
        marketplace = self.marketplace_id
        vals = {
            'name': self.name,
            'marketplace_id': marketplace.id,
            'seller_id': self.seller_id.id,
            'warehouse_id': warehouse_id,
            'company_id': company_id,
            'producturl_prefix': "https://%s/dp/" % self.marketplace_id.name
        }
        try:
            instance = self.env['amazon.instance.ept'].create(vals)
            instance.import_browse_node_ept()  # Import the browse node for selected country
        except Exception as e:
            raise Warning(
                'Exception during instance creation.\n %s' % (str(e)))

        action = self.env.ref('amazon_ept.action_amazon_configuration', False)
        result = action and action.read()[0] or {}

        ctx = result.get('context', {}) and eval(result.get('context'))
        ctx.update({'default_seller_id': instance.seller_id.id})
        # ctx.update({'default_seller_id': instance.seller_id.id,
        # 'default_instance_id': instance.id})
        result['context'] = ctx
        return result


class amazon_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    """added by Dhruvi [20-08-2018]
    Method to return seller id in marketplace wizard using context"""

    @api.multi
    def generate_buy_pack_url(self):
        url = 'https://iap.odoo.com/iap/1/credit?dbuuid='
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        service_name = 'amazon_ept'
        account = self.env['iap.account'].search(
            [('service_name', '=', 'amazon_ept')])
        if not account:
            account = self.env['iap.account'].create(
                {'service_name': 'amazon_ept'})
        account_token = account.account_token
        url = ('%s%s&service_name=%s&account_token=%s&credit=1') % (
            url, dbuuid, service_name, account_token)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

    @api.multi
    def register_seller(self):
        payload = {'key1': 'value1'}
        url = "https://iap.odoo.emiprotechnologies.com/amazon-seller-registration"
        requests.post(url, data=payload)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

    @api.multi
    def get_customer_credits(self):
        account = self.env['iap.account'].search(
            [('service_name', '=', 'amazon_ept')])
        dbuuid = self.env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')

        if not account:
            self.customer_credits = "Insufficient credit"
        else:
            kwargs = {
                'app_name': 'amazon_ept',
                'account_token': account.account_token,
                'emipro_api': 'get_customer_credits',
                'dbuuid': dbuuid,
            }
            try:
                response = iap.jsonrpc(
                    DEFAULT_ENDPOINT + '/get_customer_credits', params=kwargs)
                credit = response.get('result')
                self.customer_credits = credit
            except:
                pass

    @api.multi
    def create_more_amazon_marketplace(self):
        action = self.env.ref('amazon_ept.res_config_action_amazon_marketplace', False)
        result = action and action.read()[0] or {}
        ctx = result.get('context', {}) and eval(result.get('context'))
        # active_seller = request.session['amz_seller_id']
        if self.amz_seller_id:
            # amazon_active_seller = self.env['amazon.seller.ept'].browse(active_seller)
            market_place_id = self.amz_seller_id.instance_ids.filtered(lambda x: x.market_place_id).mapped(
                'market_place_id')
            marketplace_id = self.env['amazon.marketplace.ept'].search(
                [('seller_id', '=', self.amz_seller_id.id), ('market_place_id', 'not in', market_place_id)])
        ctx.update({'default_seller_id': self.amz_seller_id.id, 'deactive_marketplace': marketplace_id.ids})
        result['context'] = ctx
        return result

    help_fulfillment_action = """ 
        Ship - The fulfillment order ships now

        Hold - An order hold is put on the fulfillment order.3

        Default: Ship in Create Fulfillment
        Default: Hold in Update Fulfillment    
    """

    help_fulfillment_policy = """ 

        FillOrKill - If an item in a fulfillment order is determined to be unfulfillable before any 
                    shipment in the order moves to the Pending status (the process of picking units 
                    from inventory has begun), then the entire order is considered unfulfillable. 
                    However, if an item in a fulfillment order is determined to be unfulfillable 
                    after a shipment in the order moves to the Pending status, Amazon cancels as 
                    much of the fulfillment order as possible

        FillAll - All fulfillable items in the fulfillment order are shipped. 
                The fulfillment order remains in a processing state until all items are either 
                shipped by Amazon or cancelled by the seller

        FillAllAvailable - All fulfillable items in the fulfillment order are shipped.
            All unfulfillable items in the order are cancelled by Amazon.

        Default: FillOrKill
    """

    amz_def_fba_warehouse_id = fields.Many2one(
        'stock.warehouse', string='FBA Warehouse')
    amz_def_fba_partner_id = fields.Many2one('res.partner',
                                             string='Default Customer for FBA pending order')

    amz_fba_auto_workflow_id = fields.Many2one('sale.workflow.process.ept',
                                               string='Auto Workflow (FBA)')

    amz_validate_stock_inventory_for_report = fields.Boolean(
        "Auto Validate Amazon FBA Live Stock Report")

    # Inbound Shipment
    amz_allow_process_unshipped_products = fields.Boolean(
        "Allow Process Unshipped Products in Inbound Shipment ?", default=True)
    amz_update_partially_inbound_shipment = fields.Boolean(
        'Allow Update Partially Inbound Shipment ?', default=False)
    amz_is_allow_prep_instruction = fields.Boolean(
        string="Allow Prep Instructi"
               "on in Inbound Shipment ?", default=False,
        help="Amazon FBA: If ticked then allow to pass the prep-instructions details during create Inbount Shipment Plan in Amazon.")
    amz_check_status_days = fields.Integer("Check Status Days", default=30,
                                           help="System will check status after closed shipment.")

    amz_reimbursed_warehouse_id = fields.Many2one("stock.warehouse",
                                                  string="Reimbursed warehouse id")
    amz_is_another_soft_create_fba_shipment = fields.Boolean(
        string="Does another software create the FBA shipment reports?", default=False)

    amz_is_another_soft_create_fba_inventory = fields.Boolean(
        string="Does another software create the FBA Inventory reports?", default=False)

    # Unsellable Location
    amz_unsellable_location_id = fields.Many2one('stock.location', string="Unsellable Location",
                                                 help="Select instance wise amazon unsellable location")

    amz_fulfillment_action = fields.Selection([('Ship', 'Ship'), ('Hold', 'Hold')],
                                              string="Fulfillment Action",
                                              default="Hold", help=help_fulfillment_action)
    amz_shipment_service_level_category = fields.Selection(
        [('Expedited', 'Expedited'), ('NextDay', 'NextDay'), ('SecondDay', 'SecondDay'),
         ('Standard', 'Standard'),
         ('Priority', 'Priority'), ('ScheduledDelivery', 'ScheduledDelivery')],
        "Shipment Service Category", default='Standard', help="Amazon shipment category")
    amz_fulfillment_policy = fields.Selection(
        [('FillOrKill', 'FillOrKill'), ('FillAll', 'FillAll'),
         ('FillAllAvailable', 'FillAllAvailable')],
        string="Fulfillment Policy", default="FillOrKill", help=help_fulfillment_policy)
    amz_notify_by_email = fields.Boolean("Notify By Email", default=False,
                                         help="If true then system will notify by email to followers")

    # added by dhaval
    amz_is_default_odoo_sequence_in_sales_order_fba = fields.Boolean(
        "Is default Odoo Sequence In Sales Orders (FBA) ?")

    is_global_warehouse_in_fba = fields.Boolean(
        'Allow Create Removal Order In FBA?', help="Allow to create removal order in FBA.")
    removal_warehouse_id = fields.Many2one(
        'stock.warehouse', string="Removal Warehouse", help="Removal Warehouse")

    # Field added by Twinkal [30-07-2019]
    amz_is_reserved_qty_included_inventory_report = fields.Boolean(
        string='Is Reserved Qyantity to be included FBA Live Inventory Report?')

    customer_credits = fields.Char(
        "Customer Credits", compute="get_customer_credits")

    # added by twinkal 20 august 2019
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')],
                                      'Fulfillment By ?', default='FBM')

    amz_seller_id = fields.Many2one(
        'amazon.seller.ept', string='Amazon Seller')
    amz_instance_id = fields.Many2one(
        'amazon.instance.ept', string='Amazon Instance')
    amz_warehouse_id = fields.Many2one(
        'stock.warehouse', string="Amazon Warehouse")
    company_for_amazon_id = fields.Many2one(
        'res.company', string='Company Name')
    amz_country_id = fields.Many2one('res.country', string="Country Name")
    amz_partner_id = fields.Many2one('res.partner', string='Default Customer')
    amz_lang_id = fields.Many2one('res.lang', string='Language Name')
    amz_team_id = fields.Many2one('crm.team', 'Amazon Sales Team')
    amz_auto_workflow_id = fields.Many2one('sale.workflow.process.ept',
                                           string='Amazon Auto Workflow')
    amz_order_prefix = fields.Char(size=10, string='Amazon Order Prefix')
    amz_fba_order_prefix = fields.Char(string='Amazon FBA Order Prefix')

    amz_price_tax_included = fields.Boolean(string='Is Price Tax Included?')

    amz_instance_stock_field = fields.Many2one('ir.model.fields', string='Stock Type',
                                               domain="[('model', 'in', ['product.product', 'product.template']), ('ttype', '=', 'float')]")

    amz_update_stock_on_fly = fields.Boolean("Auto Update Stock On the Fly ?", default=False,
                                             help='If it is ticked, real time stock updated in Amazon.')
    amz_customer_is_company = fields.Boolean(
        "Customer is Company ?", default=False)
    amz_instance_pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist Name')
    amz_payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Term')

    amz_shipment_charge_product_id = fields.Many2one("product.product", "Amazon Shipment Fee",
                                                     domain=[('type', '=', 'service')])
    amz_gift_wrapper_product_id = fields.Many2one("product.product", "Amazon Gift Wrapper Fee",
                                                  domain=[('type', '=', 'service')])
    amz_promotion_discount_product_id = fields.Many2one("product.product",
                                                        "Amazon Promotion Discount",
                                                        domain=[('type', '=', 'service')])
    amz_ship_discount_product_id = fields.Many2one("product.product", "Amazon Shipment Discount",
                                                   domain=[('type', '=', 'service')])

    amz_instance_fiscal_position_id = fields.Many2one('account.fiscal.position',
                                                      string='Fiscal Position Name')
    amz_instance_tax_id = fields.Many2one(
        'account.tax', string='Default Sales Tax')
    amz_instance_settlement_report_journal_id = fields.Many2one('account.journal',
                                                                string='Settlement Report Journal')
    amz_condition = fields.Selection([('New', 'New'),
                                      ('UsedLikeNew', 'UsedLikeNew'),
                                      ('UsedVeryGood', 'UsedVeryGood'),
                                      ('UsedGood', 'UsedGood'),
                                      ('UsedAcceptable', 'UsedAcceptable'),
                                      ('CollectibleLikeNew', 'CollectibleLikeNew'),
                                      ('CollectibleVeryGood',
                                       'CollectibleVeryGood'),
                                      ('CollectibleGood', 'CollectibleGood'),
                                      ('CollectibleAcceptable',
                                       'CollectibleAcceptable'),
                                      ('Refurbished', 'Refurbished'),
                                      ('Club', 'Club')], string="Product Condition", default='New',
                                     copy=False)

    amz_product_ads_account = fields.Boolean(
        'Configure Product Advertising Account ?')
    amz_pro_advt_access_key = fields.Char("Product Advertising Access Key")
    amz_pro_advt_scrt_access_key = fields.Char(
        "Product Advertising Secret Key")
    amz_pro_advt_associate_tag = fields.Char(
        "Product Advertising Associate Tag")

    amz_instance_invoice_tmpl_id = fields.Many2one("mail.template", string="Invoice Template",
                                                   default=False)
    amz_instance_refund_tmpl_id = fields.Many2one("mail.template", string="Refund Template",
                                                  default=False)

    amz_create_new_product = fields.Boolean('Allow to create new product if not found in odoo ?',
                                            default=False)

    amz_instance_manage_multi_tracking_number_in_delivery_order = fields.Boolean(
        "One order can have multiple Tracking Number ?", default=False)
    is_default_odoo_sequence_in_sales_order_fbm = fields.Boolean(
        "Is default Odoo Sequence in Sales Orders (FBM) ?")
    amz_instance_ending_balance_account_id = fields.Many2one('account.account',
                                                             string="Ending Balance Account")
    amz_instance_ending_balance_description = fields.Char(
        "Ending Balance Description")
    amz_create_sale_order_from_flat_or_xml_report = fields.Selection(
        [('api', 'API'), ('xml', 'Xml'), ('flat', 'Flat')], string="Create FBM Sale Order From?",
        default="api")

    amz_order_import_user_id = fields.Many2one(
        "res.users", string="FBM Order Import User")

    amz_import_shipped_fbm_orders = fields.Boolean(
        "Import FBM Shipped Orders")  # import shipped

    amz_is_another_soft_create_fbm_reports = fields.Boolean(
        string="Does another tool create the FBM reports?", default=False)
    amz_group_hide_sale_order_report_menu = fields.Boolean('Hide Sale Order Report Menu',
                                                           compute='hide_menu',
                                                           implied_group='amazon_ept.group_hide_order_report_menu',
                                                           default=False)

    # added by dhruvi
    install_helpdesk = fields.Boolean(
        string="Get Customer message and create helpdesk ticket?")  # for helpdesk support
    manage_customer_returns = fields.Boolean(
        string="Manage customer returns & refunds using RMA?")
    amz_global_channel_id = fields.Many2one(
        'global.channel.ept', string='Global Channel')
    buynow_helpdesk = fields.Boolean(string="Buy now")
    buynow_manage_customer_returns = fields.Boolean(
        string="Buy now Customer Return")
    amz_instance_producturl_prefix = fields.Char(string="Product URL")

    # added by dhaval
    # first time set in Last_FBM_Order_Sync_Time in Seller
    amz_import_shipped_fbm_orders_date = fields.Datetime(
        "Import Shipped FBM Order Time")

    amz_last_import_fbm_order_days = fields.Integer(
        string="Last Import FBM Order Days")

    # Account field
    amazon_property_account_payable_id = fields.Many2one(
        'account.account', string="Account Payable",
        help='This account will be used instead of the default one as the payable account for the current partner')
    amazon_property_account_receivable_id = fields.Many2one('account.account', string="Account Receivable",
                                                            help='This account will be used instead of the default one as the receivable account for the current partner')
    """
    Add Field 'fulfillment_latency' for export inventory process
    @author: Deval Jagad (21/12/2019)
    """
    amz_fulfillment_latency = fields.Integer('Fullfillment Latency')

    # Added by twinkal [04-12-2019]
    amz_reimbursement_customer_id = fields.Many2one("res.partner", string="Reimbursement Customer")
    amz_reimbursement_product_id = fields.Many2one("product.product", string="Product")
    amz_sales_journal_id = fields.Many2one('account.journal', string='Sales Journal',
                                           domain=[('type', '=', 'sale')])

    amz_instance_removal_order = fields.Many2one('amazon.instance.ept', string='Amazon Instance',
                                                 help="Select Amazon Instance For Removal Order")

    """Change by Dhruvi [17-08-2018] default= True for return and refund"""
    amz_auto_create_return_picking = fields.Boolean("Auto Create Return Picking ?", default=True)
    amz_auto_create_refund = fields.Boolean("Auto Create Refund ?", default=True)

    @api.multi
    def hide_menu(self):
        cur_usr = self.env['res.users'].browse(self._uid)
        if cur_usr.has_group('amazon_ept.group_amazon_user_ept'):
            if self.amz_create_sale_order_from_flat_or_xml_report == 'api' and \
                    not self.amz_seller_id.hide_menu():
                self.update({'amz_group_hide_sale_order_report_menu': False})
                return
            self.update({'amz_group_hide_sale_order_report_menu': True})

    @api.one
    @api.constrains('amz_def_fba_warehouse_id', 'company_id')
    def onchange_company_fba_warehouse_id(self):
        if self.amz_def_fba_warehouse_id and self.company_id and \
                self.amz_def_fba_warehouse_id.company_id.id != self.company_for_amazon_id.id:
            raise Warning(
                "Company in FBA warehouse is different than the selected company. "
                "Selected Company and Company in FBA Warehouse must be same.")

    @api.one
    @api.constrains('amz_warehouse_id', 'company_for_amazon_id')
    def onchange_company_warehouse_id(self):
        if self.amz_warehouse_id and self.company_for_amazon_id and \
                self.amz_warehouse_id.company_id.id != self.company_for_amazon_id.id:
            raise Warning(
                "Company in warehouse is different than the selected company. "
                "Selected Company and Company in Warehouse must be same.")

    @api.onchange('amz_seller_id')
    def onchange_amz_seller_id(self):
        vals = {}
        domain = {}
        if self.amz_seller_id:
            seller = self.env['amazon.seller.ept'].browse(
                self.amz_seller_id.id)
            instances = self.env['amazon.instance.ept'].search(
                [('seller_id', '=', self.amz_seller_id.id)])
            vals = self.onchange_amz_instance_id()
            vals['value'][
                'company_for_amazon_id'] = seller.company_id and seller.company_id.id or False
            vals['value']['company_id'] = seller.company_id and seller.company_id.id or False
            vals['value']['amazon_selling'] = seller.amazon_selling and seller.amazon_selling
            vals['value'][
                'amz_is_another_soft_create_fbm_reports'] = seller.is_another_soft_create_fbm_reports or False
            vals['value'][
                'amz_create_sale_order_from_flat_or_xml_report'] = seller.create_sale_order_from_flat_or_xml_report or False

            vals['value']['amz_create_new_product'] = seller.create_new_product or False

            # added by Dhruvi
            vals['value'][
                'amz_global_channel_id'] = seller.global_channel_id and seller.global_channel_id.id or False
            vals['value'][
                'amz_shipment_charge_product_id'] = seller.shipment_charge_product_id and seller.shipment_charge_product_id.id or False
            vals['value'][
                'amz_gift_wrapper_product_id'] = seller.gift_wrapper_product_id and seller.gift_wrapper_product_id.id or False
            vals['value'][
                'amz_promotion_discount_product_id'] = seller.promotion_discount_product_id and seller.promotion_discount_product_id.id or False
            vals['value'][
                'amz_ship_discount_product_id'] = seller.ship_discount_product_id and seller.ship_discount_product_id.id or False
            vals['value']['amz_order_prefix'] = seller.order_prefix and seller.order_prefix
            vals['value']['amz_fba_order_prefix'] = seller.fba_order_prefix or False
            vals['value'][
                'is_default_odoo_sequence_in_sales_order_fbm'] = seller.is_default_odoo_sequence_in_sales_order or False
            vals['value'][
                'amz_payment_term_id'] = seller.payment_term_id and seller.payment_term_id.id or False
            vals['value']['amz_condition'] = seller.condition or 'New'
            vals['value'][
                'amz_auto_workflow_id'] = seller.auto_workflow_id and seller.auto_workflow_id.id or False

            # Added by Twinkal [30-07-2019]
            vals['value'][
                'amz_is_reserved_qty_included_inventory_report'] = seller.is_reserved_qty_included_inventory_report or False
            vals['value'][
                'amz_validate_stock_inventory_for_report'] = seller.validate_stock_inventory_for_report or False

            # added by dhaval
            vals['value'][
                'amz_import_shipped_fbm_orders_date'] = seller.import_shipped_fbm_orders_date or False

            vals['value'][
                'amz_last_import_fbm_order_days'] = seller.last_import_fbm_order_days or False

            vals['value'][
                'amz_reimbursed_warehouse_id'] = seller.reimbursed_warehouse_id.id or False

            vals['value'][
                'amz_is_another_soft_create_fba_shipment'] = seller.is_another_soft_create_fba_shipment or False

            vals['value'][
                'amz_is_another_soft_create_fba_inventory'] = seller.is_another_soft_create_fba_inventory or False
            # added by dhaval
            vals['value'][
                'amz_is_default_odoo_sequence_in_sales_order_fba'] = seller.is_default_odoo_sequence_in_sales_order_fba or False

            vals['value'][
                'amz_def_fba_partner_id'] = seller.def_fba_partner_id and seller.def_fba_partner_id.id or False
            vals['value']['amz_fulfillment_action'] = seller.fulfillment_action or False
            vals['value'][
                'amz_shipment_service_level_category'] = seller.shipment_service_level_category or False
            vals['value']['amz_fulfillment_policy'] = seller.fulfillment_policy or False
            vals['value']['amz_notify_by_email'] = seller.notify_by_email or False
            vals['value'][
                'amz_fba_auto_workflow_id'] = seller.fba_auto_workflow_id and seller.fba_auto_workflow_id.id or False

            """
            Set Fulfillment Latency value from Selected Amazon Seller
            @author: Deval Jagad (21/12/2019)
            """
            vals['value']['amz_fulfillment_latency'] = seller.fulfillment_latency or 0

            vals['value'][
                'amz_reimbursement_customer_id'] = seller.reimbursement_customer_id and seller.reimbursement_customer_id.id or False
            vals['value']['amz_reimbursement_product_id'] = seller.reimbursement_product_id and \
                                                            seller.reimbursement_product_id.id or False
            vals['value']['amz_sales_journal_id'] = seller.sale_journal_id and \
                                                    seller.sale_journal_id.id or False

            vals['value'][
                'amz_auto_create_return_picking'] = seller.auto_create_return_picking or False
            vals['value']['amz_auto_create_refund'] = seller.auto_create_refund or False

            instance_for_removal_order = self.env['amazon.instance.ept'].search([
                ('seller_id', '=', self.amz_seller_id.id),
                ('is_global_warehouse_in_fba', '=', True)])

            if instance_for_removal_order:
                for instance_id in instance_for_removal_order:
                    vals['value'][
                        'is_global_warehouse_in_fba'] = instance_id.is_global_warehouse_in_fba or False
                    vals['value']['amz_instance_removal_order'] = instance_id.id or False
                    vals['value'][
                        'removal_warehouse_id'] = instance_id.removal_warehouse_id and instance_id.removal_warehouse_id.id or False
            else:
                vals['value']['is_global_warehouse_in_fba'] = False
                vals['value']['amz_instance_removal_order'] = False
                vals['value']['removal_warehouse_id'] = False

            not self.amz_instance_id and vals['value'].update(
                {'amz_instance_id': instances and instances[0].id})
            domain['amz_instance_id'] = [('id', 'in', instances.ids)]

        else:
            vals = self.onchange_amz_instance_id()
            vals['value']['amz_instance_id'] = False
            domain['amz_instance_id'] = [('id', 'in', [])]

        vals.update({'domain': domain})
        return vals

    @api.onchange('amz_instance_id')
    def onchange_amz_instance_id(self):
        values = {}
        instance = self.amz_instance_id
        if instance:
            values['amz_instance_id'] = instance.id or False
            values['amz_warehouse_id'] = instance.warehouse_id and \
                                         instance.warehouse_id.id or False
            values['amz_country_id'] = instance.country_id and \
                                       instance.country_id.id or False
            values['amz_partner_id'] = instance.partner_id and \
                                       instance.partner_id.id or False
            values['amz_lang_id'] = instance.lang_id and instance.lang_id.id or False
            values['amz_team_id'] = instance.team_id and instance.team_id.id or False
            values[
                'amz_instance_stock_field'] = instance.stock_field and \
                                              instance.stock_field.id or False
            values[
                'amz_instance_pricelist_id'] = instance.pricelist_id and \
                                               instance.pricelist_id.id or False

            values[
                'amz_instance_fiscal_position_id'] = instance.fiscal_position_id and \
                                                     instance.fiscal_position_id.id or False
            values['amz_instance_tax_id'] = instance.tax_id and instance.tax_id.id or False

            values['amz_update_stock_on_fly'] = instance.update_stock_on_fly or False
            values['amz_customer_is_company'] = instance.customer_is_company or False
            values[
                'amz_instance_settlement_report_journal_id'] = instance.settlement_report_journal_id or False
            values[
                'amz_instance_manage_multi_tracking_number_in_delivery_order'] = instance.manage_multi_tracking_number_in_delivery_order or False
            values['amz_instance_invoice_tmpl_id'] = instance.invoice_tmpl_id.id or False
            values['amz_instance_refund_tmpl_id'] = instance.refund_tmpl_id.id or False
            values['amz_instance_producturl_prefix'] = instance.producturl_prefix or ''

            if instance.pro_advt_access_key and instance.pro_advt_scrt_access_key and instance.pro_advt_associate_tag:
                values['amz_product_ads_account'] = True
            else:
                values['amz_product_ads_account'] = False
            values['amz_pro_advt_access_key'] = instance.pro_advt_access_key or False
            values['amz_pro_advt_scrt_access_key'] = instance.pro_advt_scrt_access_key or False
            values['amz_pro_advt_associate_tag'] = instance.pro_advt_associate_tag or False
            values[
                'amazon_property_account_payable_id'] = instance.amazon_property_account_payable_id and instance.amazon_property_account_payable_id or False
            values[
                'amazon_property_account_receivable_id'] = instance.amazon_property_account_receivable_id and instance.amazon_property_account_receivable_id.id or False
            values[
                'amz_instance_ending_balance_account_id'] = instance.ending_balance_account_id and \
                                                            instance.ending_balance_account_id.id or False
            values[
                'amz_instance_ending_balance_description'] = instance.ending_balance_description or False

            values[
                'amz_def_fba_warehouse_id'] = instance.fba_warehouse_id and instance.fba_warehouse_id.id or False
            """Commented by Twinkal [30-07-2019] as these fields are transfered to seller"""

            values[
                'amz_allow_process_unshipped_products'] = instance.allow_process_unshipped_products or False
            values[
                'amz_update_partially_inbound_shipment'] = instance.update_partially_inbound_shipment or False

            # added by twinkal to merge module  of amazon removal

            values['is_global_warehouse_in_fba'] = instance.is_global_warehouse_in_fba or False

            values['amz_check_status_days'] = instance.check_status_days
            values[
                'amz_unsellable_location_id'] = instance.unsellable_location_id and instance.unsellable_location_id.id or False
            values['amz_is_allow_prep_instruction'] = instance.is_allow_prep_instruction or False

        else:
            values = {'amz_instance_id': False, 'amz_instance_stock_field': False,
                      'amz_country_id': False, 'amz_price_tax_included': False,
                      'amz_lang_id': False, 'amz_warehouse_id': False,
                      'amz_instance_pricelist_id': False, 'amz_partner_id': False}
        return {'value': values}

    @api.multi
    def set_user_fba_fbm_group(self, seller):
        amazon_seller_obj = self.env['amazon.seller.ept']
        amazon_fba_group = self.env.ref('amazon_ept.group_amazon_fba_ept')
        amazon_fbm_group = self.env.ref('amazon_ept.group_amazon_fbm_ept')
        amazon_fba_fbm_group = self.env.ref(
            'amazon_ept.group_amazon_fba_and_fbm_ept')
        amazon_user_group = self.env.ref('amazon_ept.group_amazon_user_ept')
        amazon_manager_group = self.env.ref('amazon_ept.group_amazon_manager_ept')
        user_list = list(set(amazon_user_group.users.ids + amazon_manager_group.users.ids))
        amazon_selling = self.amazon_selling
        if amazon_selling == 'FBA':
            other_seller = amazon_seller_obj.search(
                [('id', '!=', seller.id), ('amazon_selling', '=', 'Both')])
            if other_seller:
                return True
            else:
                other_seller = amazon_seller_obj.search(
                    [('id', '!=', seller.id), ('amazon_selling', '=', 'FBM')])
                amazon_selling = 'Both'

        elif amazon_selling == 'FBM':
            other_seller = amazon_seller_obj.search(
                [('id', '!=', seller.id), ('amazon_selling', '=', 'Both')])
            if other_seller:
                return True
            else:
                other_seller = amazon_seller_obj.search(
                    [('id', '!=', seller.id), ('amazon_selling', '=', 'FBA')])
                amazon_selling = 'Both'

        if amazon_selling == 'FBM':
            amazon_fbm_group.write({'users': [(6, 0, user_list)]})
            amazon_fba_group.write({'users': [(6, 0, [])]})
            amazon_fba_fbm_group.write({'users': [(6, 0, [])]})
        elif amazon_selling == 'FBA':
            amazon_fba_group.write({'users': [(6, 0, user_list)]})
            amazon_fbm_group.write({'users': [(6, 0, [])]})
            amazon_fba_fbm_group.write({'users': [(6, 0, [])]})
        elif amazon_selling == 'Both':
            amazon_fba_fbm_group.write({'users': [(6, 0, user_list)]})
            amazon_fba_group.write({'users': [(6, 0, user_list)]})
            amazon_fbm_group.write({'users': [(6, 0, user_list)]})
        return True

    @api.multi
    def execute(self):
        # added by Dhruvi
        instance = self.amz_instance_id
        values, vals = {}, {}
        res = super(amazon_config_settings, self).execute()
        ctx = {}
        if instance:
            ctx.update({'default_instance_id': instance.id})

            values['warehouse_id'] = self.amz_warehouse_id and self.amz_warehouse_id.id or False
            values['country_id'] = self.amz_country_id and self.amz_country_id.id or False
            values['partner_id'] = self.amz_partner_id and self.amz_partner_id.id or False
            values['lang_id'] = self.amz_lang_id and self.amz_lang_id.id or False
            values['price_tax_included'] = self.amz_price_tax_included or False
            values[
                'stock_field'] = self.amz_instance_stock_field and \
                                 self.amz_instance_stock_field.id or False
            values[
                'pricelist_id'] = self.amz_instance_pricelist_id and \
                                  self.amz_instance_pricelist_id.id or False

            values[
                'fiscal_position_id'] = self.amz_instance_fiscal_position_id and \
                                        self.amz_instance_fiscal_position_id.id or False
            values[
                'settlement_report_journal_id'] = self.amz_instance_settlement_report_journal_id and \
                                                  self.amz_instance_settlement_report_journal_id.id or False
            values['tax_id'] = self.amz_instance_tax_id and self.amz_instance_tax_id.id or False

            values['update_stock_on_fly'] = self.amz_update_stock_on_fly or False
            values['team_id'] = self.amz_team_id and self.amz_team_id.id or False
            values[
                'manage_multi_tracking_number_in_delivery_order'] = self.amz_instance_manage_multi_tracking_number_in_delivery_order or False

            values[
                'ending_balance_account_id'] = self.amz_instance_ending_balance_account_id and \
                                               self.amz_instance_ending_balance_account_id.id or False
            values[
                'ending_balance_description'] = self.amz_instance_ending_balance_description or False
            customer_is_company = True if self.amz_customer_is_company and not self.amz_partner_id else False
            values['customer_is_company'] = customer_is_company
            values['invoice_tmpl_id'] = self.amz_instance_invoice_tmpl_id.id or False
            values['refund_tmpl_id'] = self.amz_instance_refund_tmpl_id.id or False
            values['producturl_prefix'] = self.amz_instance_producturl_prefix or ''
            values[
                'amazon_property_account_payable_id'] = self.amazon_property_account_payable_id.id or False
            values[
                'amazon_property_account_receivable_id'] = self.amazon_property_account_receivable_id.id or False

            if self.amz_product_ads_account:
                values['pro_advt_access_key'] = self.amz_pro_advt_access_key or False
                values['pro_advt_scrt_access_key'] = self.amz_pro_advt_scrt_access_key or False
                values['pro_advt_associate_tag'] = self.amz_pro_advt_associate_tag or False

            self.update_user_groups_ept(
                self.amz_instance_manage_multi_tracking_number_in_delivery_order)

            # Added by twinkal to merge with FBA
            values[
                'fba_warehouse_id'] = self.amz_def_fba_warehouse_id and self.amz_def_fba_warehouse_id.id or False

            values[
                'allow_process_unshipped_products'] = self.amz_allow_process_unshipped_products or False
            values[
                'update_partially_inbound_shipment'] = self.amz_update_partially_inbound_shipment or False
            values['check_status_days'] = self.amz_check_status_days
            values[
                'unsellable_location_id'] = self.amz_unsellable_location_id and self.amz_unsellable_location_id.id or False

            values["is_global_warehouse_in_fba"] = self.is_global_warehouse_in_fba or False

            if self.amz_unsellable_location_id and self.amz_def_fba_warehouse_id:
                self.amz_def_fba_warehouse_id.unsellable_location_id = self.amz_unsellable_location_id.id

            values['is_allow_prep_instruction'] = self.amz_is_allow_prep_instruction or False

            instance.write(values)

        if self.amz_seller_id:
            self.set_user_fba_fbm_group(self.amz_seller_id)
            vals = {}

            vals[
                'create_sale_order_from_flat_or_xml_report'] = self.amz_create_sale_order_from_flat_or_xml_report or False
            vals[
                'is_another_soft_create_fbm_reports'] = self.amz_is_another_soft_create_fbm_reports or False
            vals[
                'global_channel_id'] = self.amz_global_channel_id and self.amz_global_channel_id.id or False

            """added by Dhruvi"""
            vals[
                'shipment_charge_product_id'] = self.amz_shipment_charge_product_id and self.amz_shipment_charge_product_id.id or False
            vals[
                'gift_wrapper_product_id'] = self.amz_gift_wrapper_product_id and self.amz_gift_wrapper_product_id.id or False
            vals[
                'promotion_discount_product_id'] = self.amz_promotion_discount_product_id and self.amz_promotion_discount_product_id.id or False
            vals[
                'ship_discount_product_id'] = self.amz_ship_discount_product_id and self.amz_ship_discount_product_id.id or False
            vals['order_prefix'] = self.amz_order_prefix and self.amz_order_prefix or False
            vals['fba_order_prefix'] = self.amz_fba_order_prefix or False
            vals[
                'is_default_odoo_sequence_in_sales_order'] = self.is_default_odoo_sequence_in_sales_order_fbm or False
            vals['create_new_product'] = self.amz_create_new_product or False
            vals[
                'payment_term_id'] = self.amz_payment_term_id and self.amz_payment_term_id.id or False
            vals['condition'] = self.amz_condition or 'New'
            vals[
                'auto_workflow_id'] = self.amz_auto_workflow_id and self.amz_auto_workflow_id.id or False

            vals[
                'company_id'] = self.amz_seller_id.company_id and self.amz_seller_id.company_id.id or False

            vals[
                'import_shipped_fbm_orders_date'] = self.amz_import_shipped_fbm_orders_date or False
            vals['last_import_fbm_order_days'] = self.amz_last_import_fbm_order_days or False

            vals['reimbursed_warehouse_id'] = self.amz_reimbursed_warehouse_id.id or False
            vals[
                'is_another_soft_create_fba_shipment'] = self.amz_is_another_soft_create_fba_shipment or False

            vals[
                'is_another_soft_create_fba_inventory'] = self.amz_is_another_soft_create_fba_inventory or False

            vals[
                'def_fba_partner_id'] = self.amz_def_fba_partner_id and self.amz_def_fba_partner_id.id or False

            vals['fulfillment_action'] = self.amz_fulfillment_action or False
            vals[
                'shipment_service_level_category'] = self.amz_shipment_service_level_category or False
            vals['fulfillment_policy'] = self.amz_fulfillment_policy or False
            vals['notify_by_email'] = self.amz_notify_by_email or False
            vals[
                'fba_auto_workflow_id'] = self.amz_fba_auto_workflow_id and self.amz_fba_auto_workflow_id.id or False

            vals[
                'is_default_odoo_sequence_in_sales_order_fba'] = self.amz_is_default_odoo_sequence_in_sales_order_fba or False

            vals['auto_create_return_picking'] = self.amz_auto_create_return_picking or False
            vals['auto_create_refund'] = self.amz_auto_create_refund or False

            # Added by Twinkal [31-07-2019]
            vals[
                'is_reserved_qty_included_inventory_report'] = self.amz_is_reserved_qty_included_inventory_report or False
            vals[
                'validate_stock_inventory_for_report'] = self.amz_validate_stock_inventory_for_report or False

            vals['amazon_selling'] = self.amazon_selling or False

            vals[
                'reimbursement_customer_id'] = self.amz_reimbursement_customer_id and self.amz_reimbursement_customer_id.id or False
            vals['reimbursement_product_id'] = self.amz_reimbursement_product_id and \
                                               self.amz_reimbursement_product_id.id or False
            vals['sale_journal_id'] = self.amz_sales_journal_id and self.amz_sales_journal_id.id \
                                      or False
            vals['fulfillment_latency'] = self.amz_fulfillment_latency or False

            if not self.amz_seller_id.order_last_sync_on:
                vals['order_last_sync_on'] = self.amz_import_shipped_fbm_orders_date or False

            self.amz_seller_id.write(vals)
            ctx.update({'default_seller_id': self.amz_seller_id.id})
            # seller = self.amz_seller_id

            if self.is_global_warehouse_in_fba and self.amazon_selling in ['FBA', 'Both']:
                instance_for_removal_order = self.env['amazon.instance.ept'].search(
                    [('seller_id', '=', self.amz_seller_id.id)])
                for instance_id in instance_for_removal_order:
                    if instance_id.id == self.amz_instance_removal_order.id:
                        instance_id.write(
                            {'is_global_warehouse_in_fba': self.is_global_warehouse_in_fba or False,
                             'removal_warehouse_id': self.removal_warehouse_id and self.removal_warehouse_id.id or False})
                        instance_id.write(values)
                        instance_id.configure_amazon_removal_order_routes()
                    else:
                        instance_id.is_global_warehouse_in_fba = False
                        instance_id.removal_warehouse_id = False

        if res and ctx:
            res['context'] = ctx
            res['params'] = {'seller_id': self.amz_seller_id and self.amz_seller_id.id,
                             'instance_id': instance and instance.id or False}
        return res

    @api.multi
    def update_user_groups_ept(self, allow_package_group):
        group = self.sudo().env.ref('stock.group_tracking_lot')
        amazon_user_group = self.sudo().env.ref('amazon_ept.group_amazon_user_ept')
        if allow_package_group:
            if group.id not in amazon_user_group.implied_ids.ids:
                amazon_user_group.sudo().write(
                    {'implied_ids': [(4, group.id)]})
        return True

    def create_amazon_seller_transaction_type(self):
        """
        Create  Amazon Seller Transaction Type in ERP.
        :return:
        """
        action = self.env.ref('amazon_ept.res_config_action_amazon_transaction_type', False)
        result = action and action.read()[0] or {}
        result.update({'res_id': self.amz_seller_id.id})
        return result
