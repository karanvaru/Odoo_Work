from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class amazon_marketplace_config(models.TransientModel):
    _name = 'res.config.amazon.marketplace'
    _description = 'res.config.amazon.marketplace'

    marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                       'res_config_amazon_marketplace_rel', 'res_marketplace_id',
                                       'amazon_market_place_id', string="Marketplaces")
    seller_id = fields.Many2one('amazon.seller.ept', string='Seller')
    # Field added by Twinkal [29-07-2019]
    is_pan_european_program_activated = fields.Boolean(
        'Is Pan European Program Activated ?')
    is_other_pan_europe_country = fields.Boolean('Is other Pan Europe Country ?')
    is_european_region = fields.Boolean('Is European Region ?', compute='_compute_region', default=False)
    other_pan_europe_country = fields.Many2many('res.country', 'other_pan_europe_country_rel', 'res_marketplace_id',
                                                'country_id', "Other Pan Europe Countries")

    @api.depends('marketplace_ids')
    def _compute_region(self):
        is_euopean = self.seller_id.marketplace_ids.filtered(
            lambda x: x.market_place_id in ['A2VIGQ35RCS4UG', 'A1PA6795UKMFR9', 'ARBP9OOSHTCHU', 'A1RKKUPIHCS9HS',
                                            'A13V1IB3VIYZZH', 'A1F83G8C2ARO7P', 'A21TJRUUN4KGV', 'APJ6JRA9NG5V4',
                                            'A17E79C6D8DWNP', 'A33AVAJ2PDY3EV'])
        if is_euopean:
            self.is_european_region = True
        else:
            self.is_european_region = False

    """Added by Dhruvi [29-08-2018]
    Method to search FBM warehouse [default or according to seller wise or according to 
    company of user and is_fba should be False]"""

    @api.multi
    def search_amazon_warehouse(self, company_id):
        default_warehouse = self.sudo().env.ref('stock.warehouse0')
        warehouse_obj = self.env['stock.warehouse']
        warehouse_id = False
        if default_warehouse.active:
            if self.seller_id.company_id == default_warehouse.company_id:
                warehouse_id = default_warehouse.id
            else:
                warehouse = warehouse_obj.search(
                    [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)])
                if warehouse:
                    warehouse_id = warehouse[0].id
        else:
            warehouse = warehouse_obj.search(
                [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)])
            if warehouse:
                warehouse_id = warehouse[0].id
            else:
                raise Warning('Warehouse not found for %s Company. Create a New Warehouse' % (
                    company_id.name))

        return warehouse_id

    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        marketplace_id = self._context.get('deactive_marketplace')
        if self.seller_id.is_pan_european:
            self.is_pan_european_program_activated = True
            self.is_other_pan_europe_country = True
            self.other_pan_europe_country = self.seller_id.other_pan_europe_country_ids.ids
        return {'domain': {'marketplace_ids': [('id', 'in', marketplace_id)]}}

    def prepare_amazon_marketplace_vals(self, marketplace, unsellable_location, warehouse_id):
        """
        Prepare dictionary for amazon marketplace instance
        :param marketplace: amazon.marketplace.ept()
        :return: vals {}
        """
        res_lang_obj = self.env['res.lang']
        company_id = self.seller_id.company_id
        lang_id = res_lang_obj.search([('code', '=', self._context.get('lang'))])
        if not lang_id:
            lang_id = res_lang_obj.search([('active', '=', True)], limit=1)
        vals = {
            'name': marketplace.name,
            'marketplace_id': marketplace.id,
            'seller_id': self.seller_id.id,
            'warehouse_id': warehouse_id,
            'company_id': company_id.id,
            'producturl_prefix': "https://%s/dp/" % marketplace.name,
            'ending_balance_description': 'Transfer to Bank',
            'lang_id': lang_id.id,
            'unsellable_location_id': unsellable_location and unsellable_location.id or False
        }
        return vals

    def prepare_journal_vals(self, marketplace, code):
        journal_values = {
            'name': marketplace.name + "(%s)" % self.seller_id.name,
            'type': 'bank',
            'code': code,
            'currency_id': (
                    marketplace.currency_id or marketplace.country_id.currency_id).id,
            'company_id': self.seller_id.company_id.id
        }
        return journal_values

    def prepare_pricelist_vals(self, marketplace):
        pricelist_values = {
            'name': marketplace.name + " Pricelist(%s)" % self.seller_id.name,
            'discount_policy': 'with_discount',
            'company_id': self.seller_id.company_id.id,
            'currency_id': (marketplace.currency_id or marketplace.country_id.currency_id).id,
        }
        return pricelist_values

    def create_unsellable_location(self):
        stock_location_obj = self.env['stock.location']

        unsellable_vals = {
            'name': self.seller_id.name + " Unsellable",
            'usage': 'internal',
            'company_id': self.seller_id.company_id.id
        }
        unsellable_location = stock_location_obj.create(unsellable_vals)
        return unsellable_location

    def search_fbm_warehouse(self, company_id):
        """
        Search amazon warehouse from odoo warehouses.
        :param company_id:
        :return:
        """
        warehouse_obj = self.env['stock.warehouse']
        default_warehouse = self.sudo().env.ref('stock.warehouse0')
        if default_warehouse.active:
            if self.seller_id.company_id == default_warehouse.company_id:
                warehouse_id = default_warehouse.id
            else:
                warehouse = warehouse_obj.search(
                    [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)], limit=1)
                warehouse_id = warehouse.id
        else:
            warehouse = warehouse_obj.search(
                [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)])
            if warehouse:
                warehouse_id = warehouse[0].id
            else:
                raise Warning('Warehouse not found for %s Company. Create a New Warehouse' % (
                    company_id.name))

        return warehouse_id

    def prepare_partner_vals(self, name, country):
        vals = {
            'name': name,
            'country_id': country.id
        }
        return vals

    def get_fba_warehouse(self, view_location_id, lot_stock_id, marketplace, unsellable_location, country=False):
        amazon_fulfillment_code_obj = self.env['amazon.fulfillment.country.rel']
        stock_warehouse_obj = self.env['stock.warehouse']
        partner_obj = self.env['res.partner']
        if marketplace:
            if marketplace.name.find('.') != -1:
                name = marketplace.name.rsplit('.', 1)
                code = name[1]
            else:
                code = marketplace.name
        else:
            code = country.code
        code = "%s%s" % (code, self.seller_id.id)

        vals = self.prepare_partner_vals(code, country)
        partner = partner_obj.create(vals)
        # partner name warehouse name
        # partner country
        vals = {'name': 'FBA %s(%s)' % (marketplace and marketplace.name or country.name, self.seller_id.name),
                'is_fba_warehouse': True,
                'code': code[0:5],
                'company_id': self.seller_id.company_id.id,
                'seller_id': self.seller_id.id,
                'unsellable_location_id': unsellable_location and unsellable_location.id or False,
                'partner_id': partner and partner.id or False
                }
        fba_warehouse_id = stock_warehouse_obj.create(vals)
        location_id = fba_warehouse_id.lot_stock_id
        if view_location_id and lot_stock_id:
            fba_warehouse_id.write({'view_location_id': view_location_id, 'lot_stock_id': lot_stock_id})
            fba_warehouse_id.route_ids.mapped('rule_ids').filtered(
                lambda l: l.location_src_id.id == location_id.id).write({'location_src_id': lot_stock_id})
        amazon_fulfillment_code_obj.load_fulfillment_code(marketplace and marketplace.country_id or country,
                                                          self.seller_id.id,
                                                          fba_warehouse_id.id)
        return fba_warehouse_id

    def get_location_for_pan_eu(self):
        stock_location_obj = self.env['stock.location']
        view_location_id = False
        lot_stock_id = False
        instance_found = self.seller_id.instance_ids.filtered(lambda l: l.fba_warehouse_id != False)
        if not instance_found:
            loc_vals = self.create_view_type_location()
            view_location_id = stock_location_obj.create(loc_vals).id
            lot_loc_vals = self.create_internal_type_location(view_location_id)
            lot_stock_id = stock_location_obj.create(lot_loc_vals).id
        else:
            view_location_id = instance_found[0].fba_warehouse_id.view_location_id.id
            lot_stock_id = instance_found[0].fba_warehouse_id.lot_stock_id.id

        return view_location_id, lot_stock_id

    def create_or_set_journal_and_pricelist(self, marketplace, vals):
        """
        create or set settlement report journal and pricelist and
         set ending balance account  set in ERP
        :return: True
        """

        account_journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        product_pricelist_obj = self.env['product.pricelist']
        if marketplace.name.find('.') != -1:
            name = marketplace.name.rsplit('.', 1)
            code = name[1]
        else:
            code = marketplace.name
        code = "%s%s" % (self.seller_id.name, code)
        journal_id = account_journal_obj.search(
            [('code', '=', code[0:5]), ('company_id', '=', self.seller_id.company_id.id)])
        if journal_id:
            vals.update({'settlement_report_journal_id': journal_id.id})
        else:
            journal_values = self.prepare_journal_vals(marketplace, code[0:5])
            settlement_journal_id = account_journal_obj.create(
                journal_values)
            if not settlement_journal_id.currency_id.active:
                settlement_journal_id.currency_id.active = True
            vals.update(
                {'settlement_report_journal_id': settlement_journal_id.id})

        ending_balance = account_obj.search(
            [('company_id', '=', self.seller_id.company_id.id), ('reconcile', '=', True), (
                'user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id),
             ('deprecated', '=', False)], limit=1)
        vals.update({'ending_balance_account_id': ending_balance.id})

        pricelist_values = self.prepare_pricelist_vals(marketplace)
        pricelist_id = product_pricelist_obj.create(pricelist_values)
        vals.update({'pricelist_id': pricelist_id.id})
        return vals

    def create_view_type_location(self):
        loc_vals = {'name': self.seller_id.name,
                    'usage': 'view',
                    'company_id': self.seller_id.company_id.id,
                    'location_id': self.env.ref('stock.stock_location_locations').id
                    }
        return loc_vals

    def create_internal_type_location(self, view_location_id):
        lot_loc_vals = {'name': ('Stock'),
                        'active': True,
                        'usage': 'internal',
                        'company_id': self.seller_id.company_id.id,
                        'location_id': view_location_id}
        return lot_loc_vals


    @api.multi
    def create_amazon_marketplace(self):
        """
        Create Amazon Marketplace instance in ERP
        :return: True
        """

        amazon_instance_obj = self.env['amazon.instance.ept']
        view_location_id = False
        lot_stock_id = False

        if self.seller_id.is_pan_european:
            if not self.is_pan_european_program_activated:
                raise Warning('This Seller is pan European %s Please checked is pan European' % (
                    self.seller_id.name))

        unsellable_location = self.create_unsellable_location()
        warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
        if self.is_pan_european_program_activated:
            view_location_id, lot_stock_id = self.get_location_for_pan_eu()

        for marketplace in self.marketplace_ids:
            instance_exist = amazon_instance_obj.search(
                [('seller_id', '=', self.seller_id.id),
                 ('marketplace_id', '=', marketplace.id),
                 ])

            if instance_exist:
                raise Warning(
                    'Instance already exist for %s with given Credential.' % (marketplace.name))

            instance_values = self.prepare_amazon_marketplace_vals(marketplace, unsellable_location, warehouse_id)
            instance_values = self.create_or_set_journal_and_pricelist(marketplace, instance_values)

            fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id, marketplace, unsellable_location,
                                                      marketplace.country_id)
            instance_values.update({'fba_warehouse_id': fba_warehouse_id.id})
            amazon_instance_obj.create(instance_values)
            self.auto_configure_stock_adjustment()

        if self.is_pan_european_program_activated:
            self.seller_id.write({'is_pan_european': self.is_pan_european_program_activated,
                                  'is_european_region': self.is_european_region,
                                  'is_other_pan_europe_country': self.is_other_pan_europe_country,
                                  'other_pan_europe_country_ids': [(6, 0, self.other_pan_europe_country.ids)]})

        if self.is_other_pan_europe_country:
            for country in self.other_pan_europe_country:
                if self.seller_id.warehouse_ids.filtered(lambda l: l.partner_id.country_id.id == country.id):
                    continue
                self.get_fba_warehouse(view_location_id, lot_stock_id, False, unsellable_location, country)
        action = self.env.ref('amazon_ept.action_amazon_configuration', False)
        result = action and action.read()[0] or {}
        ctx = result.get('context', {}) and eval(result.get('context'))
        ctx.update({'default_seller_id': self.seller_id.id})
        result['context'] = ctx
        return True

    def auto_configure_stock_adjustment(self):
        """
        This Method relocate auto configure stock adjustment configuration.
        :param seller: This Argument relocate amazon seller.
        :return: This Method return Boolean(True/False).
        """
        stock_warehouse_obj = self.env['stock.warehouse']
        stock_location_obj = self.env['stock.location']
        amazon_stock_reason_group = self.env['amazon.adjustment.reason.group'].search([])
        stock_adj_email_template = self.env.ref('amazon_ept.email_template_amazon_stock_adjustment_email_ept')
        amz_seller_id = self.seller_id.id
        amz_stock_adjustment_config = self.env['amazon.stock.adjustment.config'].search(
            [('seller_id', '=', amz_seller_id), ('group_id', 'in', amazon_stock_reason_group.ids)])
        if not amz_stock_adjustment_config:
            for stock_reason_group in amazon_stock_reason_group:
                if stock_reason_group.name == 'Damaged Inventory':
                    amazon_warehouse = self.seller_id.warehouse_ids.filtered(
                        lambda l: l.partner_id.country_id.id == self.seller_id.country_id.id)
                    if not amazon_warehouse:
                        amazon_warehouse = stock_warehouse_obj.search([('seller_id', '=', amz_seller_id)], limit=1)
                    amz_warehouse_lot_stock_id = amazon_warehouse.lot_stock_id
                    self.create_adjustment_config(amz_seller_id, stock_reason_group, amz_warehouse_lot_stock_id)

                if stock_reason_group.name == 'Unrecoverable Inventory':
                    location_type = 'inventory'
                    unrecoverable_inv_location = self.search_stock_location(location_type)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group, unrecoverable_inv_location)
                if stock_reason_group.name == 'Inbound Shipment Receive Adjustments':
                    location_type = 'transit'
                    shipment_transit_location = self.search_stock_location(location_type)
                    if not shipment_transit_location:
                        loc_vals = {
                            'name': 'FBA Transit Location %s(%s)' % (
                                self.seller_id.country_id.name, self.seller_id.name),
                            'usage': 'transit',
                            'company_id': self.seller_id.company_id.id,
                            'location_id': self.env.ref('stock.stock_location_locations').id
                        }
                        shipment_transit_location = stock_location_obj.create(loc_vals)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group, shipment_transit_location)
                if stock_reason_group.name == 'Software Corrections':
                    if stock_adj_email_template:
                        location_id = False
                        is_send_email = True
                        self.create_adjustment_config(amz_seller_id, stock_reason_group, location_id, is_send_email,
                                                      stock_adj_email_template)
                if stock_reason_group.name == 'Transferring ownership':
                    location_type = 'customer'
                    customer_location = self.search_stock_location(location_type)
                    if customer_location:
                        self.create_adjustment_config(amz_seller_id, stock_reason_group, customer_location)
                if stock_reason_group.name == 'Catalogue Management':
                    if stock_adj_email_template:
                        location_id = False
                        is_send_email = True
                        self.create_adjustment_config(amz_seller_id, stock_reason_group, location_id, is_send_email,
                                                      stock_adj_email_template)
                if stock_reason_group.name == 'Misplaced and Found':
                    loc_vals = {
                        'name': 'FBA Lost by Amazon %s(%s)' % (self.seller_id.country_id.name, self.seller_id.name),
                        'usage': 'internal',
                        'company_id': self.seller_id.company_id.id,
                        'location_id': self.env.ref('stock.stock_location_locations').id
                    }
                    misplaced_transit_location = stock_location_obj.create(loc_vals)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group, misplaced_transit_location)
        return True

    def search_stock_location(self, location_type):
        """
        This Method relocate search stock location based on location type.
        :param location_type: This Argument relocate location type of stock location.
        :return: This Method return search result of stock location.
        """
        stock_location_obj = self.env['stock.location']
        return stock_location_obj.search([('usage', '=', location_type)], limit=1)

    def create_adjustment_config(self, seller, stock_reason_group, location_id, is_send_email=False,
                                 email_template_id=False):
        """
        This Method relocate create stock adjustment configuration seller wise.
        :param seller: This Argument relocate amazon seller.
        :param stock_reason_group: This Argument relocate amazon stock reason group.
        :param location_id: This Argument location id.
        :param is_send_email: This Argument relocate is send email True.
        :param email_template_id: This Argument relocate email template id of stock adjustment.
        :return: This Argument return Boolean(True/False).
        """
        amz_stock_adjustment_config = self.env['amazon.stock.adjustment.config']
        amz_stock_adjustment_config.create(
            {'seller_id': seller and seller, 'group_id': stock_reason_group and stock_reason_group.id,
             'is_send_email': is_send_email,
             'email_template_id': email_template_id and email_template_id.id,
             'location_id': location_id and location_id.id})
        return True
