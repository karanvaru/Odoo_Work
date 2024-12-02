from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

_intervalTypes = {
    'work_days': lambda interval: relativedelta(days=interval),
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class FbaCronConfiguration(models.TransientModel):
    _name = "fba.cron.configuration"
    _description = "Amazon FBA Cron Configuration"

    def _get_amazon_seller(self):
        return self.env.context.get('amz_seller_id', False)

    def _get_amazon_selling(self):
        return self.env.context.get('amazon_selling', False)

    amz_seller_id = fields.Many2one(
        'amazon.seller.ept', string='Amazon Seller', default=_get_amazon_seller, readonly=True)
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')],
                                      'Amazon Selling', default=_get_amazon_selling, readonly=True)
    # FBA Import Pending order
    amz_auto_import_fba_pending_order = fields.Boolean(
        string='Auto Request FBA Pending Order ?')
    amz_pending_order_next_execution = fields.Datetime('Import FBA Pending Order Next Execution',
                                                       help='Next execution time')
    amz_pending_order_import_interval_number = fields.Integer(
        'Import FBA Pending Order Interval Number', help="Repeat every x.")
    amz_pending_order_import_interval_type = fields.Selection([('hours', 'Hours'),
                                                               ('days', 'Days')],
                                                              'Import FBA Pending Order Interval Unit')
    amz_pending_order_import_user_id = fields.Many2one("res.users",
                                                       string="Import FBA Pending Order User")
    # FBA check cancel order
    amz_auto_check_cancel_order = fields.Boolean(
        string='Auto Check Canceled FBA Order in Amazon ?')
    amz_cancel_order_next_execution = fields.Datetime(
        'Check Canceled FBA Order in Amazon Next Execution', help='Next execution time')
    amz_cancel_order_interval_number = fields.Integer(
        'Check Canceled FBA Order in Amazon Interval Number', help="Repeat every x.")
    amz_cancel_order_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                      'Check Canceled FBA Order in Amazon Interval Unit')
    amz_cancel_order_report_user_id = fields.Many2one("res.users",
                                                      string="Check Canceled FBA Order in Amazon User")
    # FBA Shipment Report
    amz_auto_import_shipment_report = fields.Boolean(
        string='Auto Request FBA Shipment Report?')
    amz_ship_report_import_next_execution = fields.Datetime(
        'Import FBA Shipment Report Next Execution', help='Next execution time')
    amz_ship_report_import_interval_number = fields.Integer(
        'Import FBA Shipment Report Interval Number', help="Repeat every x.")
    amz_ship_report_import_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                            'Import FBA Shipment Report Interval Unit')
    amz_ship_report_import_user_id = fields.Many2one("res.users",
                                                     string="Import FBA Shipment Report User")

    # FBA download and process report
    amz_auto_process_shipment_report = fields.Boolean(
        string='Download and Process FBA Shipment Report ?')
    amz_ship_report_process_next_execution = fields.Datetime(
        'Process FBA Shipment Report Next Execution', help='Next execution time')
    amz_ship_report_process_interval_number = fields.Integer(
        'Process FBA Shipment Report Interval Number', help="Repeat every x.")
    amz_ship_report_process_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                             'Process FBA Shipment Report Interval Unit')
    amz_ship_report_process_user_id = fields.Many2one("res.users",
                                                      string="Process FBA Shipment Report User")

    # Auto Create Removal Order Report
    auto_create_removal_order_report = fields.Boolean(
        string="Auto Request Removal Order Report ?")
    fba_removal_order_next_execution = fields.Datetime(
        'Auto Create Removal Order Report Next Execution', help='Next execution time')
    fba_removal_order_interval_number = fields.Integer(
        'Auto Create Removal Order Report Interval Number', help="Repeat every x.")
    fba_removal_order_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                       'Auto Create Removal Order Report Interval Unit')
    fba_removal_order_user = fields.Many2one(
        "res.users", string="Auto Create Removal Order Report User", help="Select the user.")

    # Auto Process FBA Removal Order Report
    auto_process_removal_report = fields.Boolean(
        string='Download and Process FBA Removal Order Report ?')
    fba_removal_order_process_next_execution = fields.Datetime(
        'Auto Process FBA Removal Order Report Next Execution', help='Next execution time')
    fba_removal_order_process_interval_number = fields.Integer(
        'Auto Process FBA Removal Order Report Interval Number', help="Repeat every x.")
    fba_removal_order_process_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                               'Auto Process FBA Removal Order Report Interval Unit')
    fba_removal_order_process_user = fields.Many2one(
        "res.users", string="Auto Process FBA Removal Order Report User", help="Select the user.")

    # FBA Customer Return Report
    amz_auto_import_return_report = fields.Boolean(
        string='Auto Request FBA Customer Return Report ?')
    amz_return_report_import_next_execution = fields.Datetime(
        'Import FBA Customer Return Report Next Execution', help='Next execution time')
    amz_return_report_import_interval_number = fields.Integer(
        'Import FBA Customer Return Report Interval Number', help="Repeat every x.")
    amz_return_report_import_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                              'Import FBA Customer Return Report Interval Unit')
    amz_return_report_import_user_id = fields.Many2one("res.users",
                                                       string="Import FBA Customer Return Report User")

    # Process and download return report
    amz_auto_process_return_report = fields.Boolean(
        string='Download and Process FBA Customer Returns?')
    amz_return_process_report_next_execution = fields.Datetime(
        'Process FBA Customer Return Next Execution', help='Next execution time')
    amz_return_process_report_interval_number = fields.Integer(
        'Process FBA Customer Return Interval Number', help="Repeat every x.")
    amz_return_process_report_interval_type = fields.Selection([('hours', 'Hours'),
                                                                ('days', 'Days')],
                                                               'Process FBA Customer Return Interval Unit')
    amz_return_process_report_user_id = fields.Many2one("res.users",
                                                        string="Process FBA Customer Return User")

    # Live Stock Report
    amz_stock_auto_import_by_report = fields.Boolean(
        string='Auto Request FBA Live Stock Report?')
    amz_inventory_import_next_execution = fields.Datetime(
        'Import FBA Live Stock Report Next Execution', help='Next execution time')
    amz_inventory_import_interval_number = fields.Integer(
        'Import FBA Live Stock Report Interval Number', help="Repeat every x.")
    amz_inventory_import_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                          'Import FBA Live Stock Report Interval Unit')
    amz_inventory_import_user_id = fields.Many2one("res.users",
                                                   string="Import FBA Live Stock Report User")

    # Download and process Live Stock Report
    amz_auto_process_fba_live_stock_report = fields.Boolean(
        string='Download and Process FBA Live Stock Report?')
    amz_process_fba_live_stock_next_execution = fields.Datetime(
        'Process FBA Live Stock Report Next Execution', help='Next execution time')
    amz_process_fba_live_stock_interval_number = fields.Integer(
        'Process FBA Live Stock Report Interval Number', help="Repeat every x.")
    amz_process_fba_live_stock_interval_type = fields.Selection([('hours', 'Hours'),
                                                                 ('days', 'Days')],
                                                                'Process FBA Live Stock Report Interval Unit')
    amz_process_fba_live_stock_user_id = fields.Many2one("res.users",
                                                         string="Process FBA Live Stock Report User")

    # Request FBA Stock Adjustment Report
    auto_create_fba_stock_adj_report = fields.Boolean(
        string="Auto Request FBA Stock Adjustment Report ?")
    fba_stock_adj_report_next_execution = fields.Datetime(
        'Auto Create Stock Adjustment Report Next Execution', help='Next execution time')
    fba_stock_adj_report_interval_number = fields.Integer(
        'Auto Create Stock Adjustment Report Interval Number', help="Repeat every x.")
    fba_stock_adj_report_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                          'Auto Create Stock Adjustment Report Interval Unit')

    # FBA Stock Process and download
    auto_process_fba_stock_adj_report = fields.Boolean(
        string='Download and Process FBA Stock Adjustment Report ?')
    fba_stock_adj_report_process_next_execution = fields.Datetime(
        'Auto Process Stock Adjustment Report Next Execution', help='Next execution time')
    fba_stock_adj_report_process_interval_number = fields.Integer(
        ' Auto Process Stock Adjustment Report Interval Number', help="Repeat every x.")
    fba_stock_adj_report_process_interval_type = fields.Selection([('hours', 'Hours'), ('days', 'Days')],
                                                                  'Auto Process Stock Adjustment Report Interval Unit')

    @api.onchange("amz_seller_id")
    def onchange_amazon_seller_id(self):
        amz_seller = self.amz_seller_id
        self.update_amz_pending_order_cron_field(amz_seller)
        self.update_amz_cancel_order_cron_field(amz_seller)
        self.update_amz_shipment_report_cron_field(amz_seller)
        self.update_amz_shipment_process_report_cron_field(amz_seller)
        self.update_amz_removal_order_report_cron_field(amz_seller)
        self.update_amz_removal_report_process_cron_field(amz_seller)
        self.update_amz_return_report_cron_field(amz_seller)
        self.update_amz_return_report_process_cron_field(amz_seller)
        self.update_amz_fba_live_report_cron_field(amz_seller)
        self.update_amz_fba_live_report_process(amz_seller)
        self.update_amz_fba_stock_auto_import_cron_field(amz_seller)
        self.update_amz_fba_stock_adj_process(amz_seller)

    def update_amz_pending_order_cron_field(self, amz_seller):
        try:
            amz_pending_order_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_pending_order_seller_%d' % (amz_seller.id))
        except:
            amz_pending_order_cron_exist = False
        if amz_pending_order_cron_exist:
            self.amz_auto_import_fba_pending_order = amz_pending_order_cron_exist.active or False
            self.amz_pending_order_import_interval_number = amz_pending_order_cron_exist.interval_number or False
            self.amz_pending_order_import_interval_type = amz_pending_order_cron_exist.interval_type or False
            self.amz_pending_order_next_execution = amz_pending_order_cron_exist.nextcall or False
            self.amz_pending_order_import_user_id = amz_pending_order_cron_exist.user_id.id or False

    def update_amz_cancel_order_cron_field(self, amz_seller):
        try:
            amz_cancel_order_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_auto_check_canceled_order_in_amazon_seller_%d' % (amz_seller.id))
        except:
            amz_cancel_order_cron_exist = False
        if amz_cancel_order_cron_exist:
            self.amz_auto_check_cancel_order = amz_cancel_order_cron_exist.active or False
            self.amz_cancel_order_interval_number = amz_cancel_order_cron_exist.interval_number or False
            self.amz_cancel_order_interval_type = amz_cancel_order_cron_exist.interval_type or False
            self.amz_cancel_order_next_execution = amz_cancel_order_cron_exist.nextcall or False
            self.amz_cancel_order_report_user_id = amz_cancel_order_cron_exist.user_id.id or False

    def update_amz_shipment_report_cron_field(self, amz_seller):
        try:
            amz_check_shipement_report_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_shipment_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_shipement_report_cron_exist = False

        if amz_check_shipement_report_cron_exist:
            self.amz_auto_import_shipment_report = amz_check_shipement_report_cron_exist.active or False
            self.amz_ship_report_import_interval_number = amz_check_shipement_report_cron_exist.interval_number or False
            self.amz_ship_report_import_interval_type = amz_check_shipement_report_cron_exist.interval_type or False
            self.amz_ship_report_import_next_execution = amz_check_shipement_report_cron_exist.nextcall or False
            self.amz_ship_report_import_user_id = amz_check_shipement_report_cron_exist.user_id.id or False

    def update_amz_shipment_process_report_cron_field(self, amz_seller):
        try:
            amz_check_shipement_process_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_process_amazon_fba_shipment_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_shipement_process_cron_exist = False
        if amz_check_shipement_process_cron_exist:
            self.amz_auto_process_shipment_report = amz_check_shipement_process_cron_exist.active or False
            self.amz_ship_report_process_interval_number = amz_check_shipement_process_cron_exist.interval_number or False
            self.amz_ship_report_process_interval_type = amz_check_shipement_process_cron_exist.interval_type or False
            self.amz_ship_report_process_next_execution = amz_check_shipement_process_cron_exist.nextcall or False
            self.amz_ship_report_process_user_id = amz_check_shipement_process_cron_exist.user_id.id or False

    def update_amz_removal_order_report_cron_field(self, amz_seller):
        try:
            amz_check_removal_order_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_create_fba_removal_order_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_removal_order_cron_exist = False
        if amz_check_removal_order_cron_exist:
            self.auto_create_removal_order_report = amz_check_removal_order_cron_exist.active or False
            self.fba_removal_order_interval_number = amz_check_removal_order_cron_exist.interval_number or False
            self.fba_removal_order_interval_type = amz_check_removal_order_cron_exist.interval_type or False
            self.fba_removal_order_next_execution = amz_check_removal_order_cron_exist.nextcall or False
            self.fba_removal_order_user = amz_check_removal_order_cron_exist.user_id.id or False

    def update_amz_removal_report_process_cron_field(self, amz_seller):
        try:
            amz_check_removal_process_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_process_fba_removal_order_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_removal_process_cron_exist = False
        if amz_check_removal_process_cron_exist:
            self.auto_process_removal_report = amz_check_removal_process_cron_exist.active or False
            self.fba_removal_order_process_interval_number = amz_check_removal_process_cron_exist.interval_number or False
            self.fba_removal_order_process_interval_type = amz_check_removal_process_cron_exist.interval_type or False
            self.fba_removal_order_process_next_execution = amz_check_removal_process_cron_exist.nextcall or False
            self.fba_removal_order_process_user = amz_check_removal_process_cron_exist.user_id.id or False

    def update_amz_return_report_cron_field(self, amz_seller):
        try:
            amz_check_return_customer_report_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_auto_import_customer_return_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_return_customer_report_cron_exist = False
        if amz_check_return_customer_report_cron_exist:
            self.amz_auto_import_return_report = amz_check_return_customer_report_cron_exist.active or False
            self.amz_return_report_import_interval_number = amz_check_return_customer_report_cron_exist.interval_number or False
            self.amz_return_report_import_interval_type = amz_check_return_customer_report_cron_exist.interval_type or False
            self.amz_return_report_import_next_execution = amz_check_return_customer_report_cron_exist.nextcall or False
            self.amz_return_report_import_user_id = amz_check_return_customer_report_cron_exist.user_id.id or False

    def update_amz_return_report_process_cron_field(self, amz_seller):
        try:
            amz_check_return_report_process_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_auto_process_customer_return_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_return_report_process_cron_exist = False
        if amz_check_return_report_process_cron_exist:
            self.amz_auto_process_return_report = amz_check_return_report_process_cron_exist.active or False
            self.amz_return_process_report_interval_number = amz_check_return_report_process_cron_exist.interval_number or False
            self.amz_return_process_report_interval_type = amz_check_return_report_process_cron_exist.interval_type or False
            self.amz_return_process_report_next_execution = amz_check_return_report_process_cron_exist.nextcall or False
            self.amz_return_process_report_user_id = amz_check_return_report_process_cron_exist.user_id.id or False

    def update_amz_fba_live_report_cron_field(self, amz_seller):
        try:
            amz_check_live_stock_report_process_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_import_stock_from_amazon_fba_live_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_live_stock_report_process_cron_exist = False

        if amz_check_live_stock_report_process_cron_exist:
            self.amz_stock_auto_import_by_report = amz_check_live_stock_report_process_cron_exist.active or False
            self.amz_inventory_import_interval_number = amz_check_live_stock_report_process_cron_exist.interval_number or False
            self.amz_inventory_import_interval_type = amz_check_live_stock_report_process_cron_exist.interval_type or False
            self.amz_inventory_import_next_execution = amz_check_live_stock_report_process_cron_exist.nextcall or False
            self.amz_inventory_import_user_id = amz_check_live_stock_report_process_cron_exist.user_id.id or False

    def update_amz_fba_live_report_process(self, amz_seller):
        try:
            amz_check_live_stock_process_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_process_fba_live_stock_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_live_stock_process_cron_exist = False

        if amz_check_live_stock_process_cron_exist:
            self.amz_auto_process_fba_live_stock_report = amz_check_live_stock_process_cron_exist.active or False
            self.amz_process_fba_live_stock_interval_number = amz_check_live_stock_process_cron_exist.interval_number or False
            self.amz_process_fba_live_stock_interval_type = amz_check_live_stock_process_cron_exist.interval_type or False
            self.amz_process_fba_live_stock_next_execution = amz_check_live_stock_process_cron_exist.nextcall or False
            self.amz_process_fba_live_stock_user_id = amz_check_live_stock_process_cron_exist.user_id.id or False

    def update_amz_fba_stock_auto_import_cron_field(self, amz_seller):
        try:
            amz_check_stock_report_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_create_fba_stock_adjustment_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_stock_report_cron_exist = False

        if amz_check_stock_report_cron_exist:
            self.auto_create_fba_stock_adj_report = amz_check_stock_report_cron_exist.active or False
            self.fba_stock_adj_report_interval_number = amz_check_stock_report_cron_exist.interval_number or False
            self.fba_stock_adj_report_interval_type = amz_check_stock_report_cron_exist.interval_type or False
            self.fba_stock_adj_report_next_execution = amz_check_stock_report_cron_exist.nextcall or False

    def update_amz_fba_stock_adj_process(self, amz_seller):
        try:
            amz_check_stock_adj_cron_exist = amz_seller and self.env.ref(
                'amazon_ept.ir_cron_process_fba_stock_adjustment_report_seller_%d' % (amz_seller.id))
        except:
            amz_check_stock_adj_cron_exist = False
        if amz_check_stock_adj_cron_exist:
            self.auto_process_fba_stock_adj_report = amz_check_stock_adj_cron_exist.active or False
            self.fba_stock_adj_report_process_interval_number = amz_check_stock_adj_cron_exist.interval_number or False
            self.fba_stock_adj_report_process_interval_type = amz_check_stock_adj_cron_exist.interval_type or False
            self.fba_stock_adj_report_process_next_execution = amz_check_stock_adj_cron_exist.nextcall or False

    def save_cron_configuration(self):
        amazon_seller = self.amz_seller_id
        vals = {}
        self.auto_import_fba_pending_order(amazon_seller)

        self.auto_fba_check_cancel_order(amazon_seller)

        self.auto_fba_import_shipment_report(amazon_seller)

        self.auto_fba_process_shipment_report(amazon_seller)

        self.setup_removal_order_report_create_cron(amazon_seller)

        self.setup_removal_order_report_process_cron(amazon_seller)

        self.setup_auto_import_customer_return_report(amazon_seller)

        self.setup_auto_process_customer_return_report(amazon_seller)

        self.setup_amz_seller_live_stock_cron(amazon_seller, self.amz_auto_process_fba_live_stock_report,
                                              self.amz_process_fba_live_stock_interval_type,
                                              self.amz_process_fba_live_stock_interval_number,
                                              self.amz_process_fba_live_stock_next_execution,
                                              self.amz_process_fba_live_stock_user_id, 'FBA',
                                              'ir_cron_process_fba_live_stock_report')

        self.setup_amz_seller_live_stock_cron(amazon_seller, self.amz_stock_auto_import_by_report,
                                              self.amz_inventory_import_interval_type,
                                              self.amz_inventory_import_interval_number,
                                              self.amz_inventory_import_next_execution,
                                              self.amz_inventory_import_user_id, 'FBM',
                                              'ir_cron_import_stock_from_amazon_fba_live_report')

        self.setup_stock_adjustment_report_create_cron(amazon_seller)

        self.setup_stock_adjustment_report_process_cron(amazon_seller)
        vals['auto_import_fba_pending_order'] = self.amz_auto_import_fba_pending_order or False
        vals['auto_check_cancel_order'] = self.amz_auto_check_cancel_order or False
        vals['auto_import_shipment_report'] = self.amz_auto_import_shipment_report or False
        vals['auto_process_shipment_report'] = self.amz_auto_process_shipment_report or False
        vals['auto_create_removal_order_report'] = self.auto_create_removal_order_report or False
        vals['auto_process_removal_report'] = self.auto_process_removal_report or False
        vals['auto_import_return_report'] = self.amz_auto_import_return_report or False
        vals['auto_process_return_report'] = self.amz_auto_process_return_report or False
        vals['auto_import_product_stock'] = self.amz_stock_auto_import_by_report or False
        vals['auto_process_fba_live_stock_report'] = self.amz_auto_process_fba_live_stock_report or False
        vals['auto_create_fba_stock_adj_report'] = self.auto_create_fba_stock_adj_report or False
        vals['auto_process_fba_stock_adj_report'] = self.auto_process_fba_stock_adj_report or False
        amazon_seller.write(vals)

    def auto_import_fba_pending_order(self, amazon_seller):
        if self.amz_auto_import_fba_pending_order and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_pending_order_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_pending_order_import_interval_number,
                'interval_type': self.amz_pending_order_import_interval_type,
                'nextcall': self.amz_pending_order_next_execution,
                'user_id': self.amz_pending_order_import_user_id.id,
                'code': "model.auto_import_fba_pending_sale_order_ept({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id), 'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_import_amazon_fba_pending_order',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Import Amazon Pending Orders'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_import_amazon_fba_pending_order_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_pending_order_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def auto_fba_check_cancel_order(self, amazon_seller):

        if self.amz_auto_check_cancel_order and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_check_canceled_order_in_amazon_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_cancel_order_interval_number,
                'interval_type': self.amz_cancel_order_interval_type,
                'nextcall': self.amz_cancel_order_next_execution,
                'user_id': self.amz_cancel_order_report_user_id.id,
                'code': "model.auto_check_cancel_order_in_amazon({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id), 'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_auto_check_canceled_order_in_amazon',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Import Amazon Check Cancel Orders'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_auto_check_canceled_order_in_amazon_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_check_canceled_order_in_amazon_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def auto_fba_import_shipment_report(self, amazon_seller):
        if self.amz_auto_import_shipment_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_shipment_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_ship_report_import_interval_number,
                'interval_type': self.amz_ship_report_import_interval_type,
                'nextcall': self.amz_ship_report_import_next_execution,
                'user_id': self.amz_ship_report_import_user_id.id,
                'code': "model.auto_import_shipment_report({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id), 'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_import_amazon_fba_shipment_report',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Import Amazon FBA Shipment Report'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_import_amazon_fba_shipment_report_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_import_amazon_fba_shipment_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def auto_fba_process_shipment_report(self, amazon_seller):
        if self.amz_auto_process_shipment_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_process_amazon_fba_shipment_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_ship_report_process_interval_number,
                'interval_type': self.amz_ship_report_process_interval_type,
                'nextcall': self.amz_ship_report_process_next_execution,
                'user_id': self.amz_ship_report_process_user_id.id,
                'code': "model.auto_process_shipment_report({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id), 'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_process_amazon_fba_shipment_report',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Process Amazon FBA Shipment Report'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_process_amazon_fba_shipment_report_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_process_amazon_fba_shipment_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_removal_order_report_create_cron(self, seller):
        if self.auto_create_removal_order_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref('amazon_ept.ir_cron_create_fba_removal_order_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.fba_removal_order_interval_number,
                'interval_type': self.fba_removal_order_interval_type,
                'nextcall': self.fba_removal_order_next_execution,
                'code': "model.auto_import_removal_order_report({'seller_id':%d})" % (seller.id),
                'user_id': self.fba_removal_order_user and self.fba_removal_order_user.id,
                'amazon_seller_cron_id': seller.id
            }

            if cron_exist:
                cron_exist.write(vals)
            else:
                inv_report_cron = self.env.ref(
                    'amazon_ept.ir_cron_create_fba_removal_order_report', raise_if_not_found=False)
                if not inv_report_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + seller.name + ' : Create Amazon Removal Order Report'
                vals.update({'name': name})
                new_cron = inv_report_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_create_fba_removal_order_report_seller_%d' % (
                                                      seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })
        else:
            cron_exist = self.env.ref('amazon_ept.ir_cron_create_fba_removal_order_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_removal_order_report_process_cron(self, seller):
        if self.auto_process_removal_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref('amazon_ept.ir_cron_process_fba_removal_order_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.fba_removal_order_process_interval_number,
                'interval_type': self.fba_removal_order_process_interval_type,
                'nextcall': self.fba_removal_order_process_next_execution,
                'code': "model.auto_process_removal_order_report({'seller_id':%d})" % (seller.id),
                'user_id': self.fba_removal_order_process_user and self.fba_removal_order_process_user.id,
                'amazon_seller_cron_id': seller.id
            }
            if cron_exist:
                cron_exist.write(vals)
            else:
                inv_report_cron = self.env.ref(
                    'amazon_ept.ir_cron_process_fba_removal_order_report', raise_if_not_found=False)
                if not inv_report_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + seller.name + ' : Process Removal Order Report'
                vals.update({'name': name})
                new_cron = inv_report_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_process_fba_removal_order_report_seller_%d' % (
                                                      seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })
        else:
            cron_exist = self.env.ref('amazon_ept.ir_cron_process_fba_removal_order_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_auto_import_customer_return_report(self, amazon_seller):
        if self.amz_auto_import_return_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_import_customer_return_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_return_report_import_interval_number,
                'interval_type': self.amz_return_report_import_interval_type,
                'nextcall': self.amz_return_report_import_next_execution,
                'user_id': self.amz_return_report_import_user_id.id,
                'code': "model.auto_import_return_report({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id),
                'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_auto_import_customer_return_report',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Import Amazon FBA Customer Return Report'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_auto_import_customer_return_report_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_import_customer_return_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_auto_process_customer_return_report(self, amazon_seller):
        if self.amz_auto_process_return_report and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_process_customer_return_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.amz_return_process_report_interval_number,
                'interval_type': self.amz_return_process_report_interval_type,
                'nextcall': self.amz_return_process_report_next_execution,
                'user_id': self.amz_return_process_report_user_id.id,
                'code': "model.auto_process_return_order_report({'seller_id':%d, 'is_auto_process': True})" % (
                    amazon_seller.id), 'amazon_seller_cron_id': amazon_seller.id}
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_order_cron = self.env.ref('amazon_ept.ir_cron_auto_process_customer_return_report',
                                                 raise_if_not_found=False)
                if not import_order_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + amazon_seller.name + ' : Process Amazon FBA Customer Return Report'
                vals.update({'name': name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_auto_process_customer_return_report_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            cron_exist = self.env.ref(
                'amazon_ept.ir_cron_auto_process_customer_return_report_seller_%d' % (
                    amazon_seller.id),
                raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_amz_seller_live_stock_cron(self, amazon_seller, auto_import, interval_type, interval_number,
                                         next_call, cron_user, prefix, cron_xml_id,
                                         module='amazon_ept'):
        if auto_import and self.amazon_selling not in ['FBM']:
            cron_exist = self.env.ref(module + '.' + cron_xml_id + '_seller_%d' % (amazon_seller.id),
                                      raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': interval_number,
                'interval_type': interval_type,
                'nextcall': next_call,
                'code': "model.({'seller_id':%d})" % (amazon_seller.id),
                'user_id': cron_user and cron_user.id,
                'amazon_seller_cron_id': amazon_seller.id

            }

            if cron_xml_id == 'ir_cron_import_stock_from_amazon_fba_live_report':
                vals.update({
                    'code': "model.auto_import_amazon_fba_live_stock_report({'seller_id':%d})" % (
                        amazon_seller.id)
                })
            if cron_xml_id == 'ir_cron_process_fba_live_stock_report':
                vals.update({
                    'code': "model.auto_process_amazon_fba_live_stock_report({'seller_id':%d})" % (
                        amazon_seller.id)
                })
            if cron_exist:
                cron_exist.write(vals)
            else:
                import_return_cron = self.env.ref(module + '.' + cron_xml_id,
                                                  raise_if_not_found=False)
                if not import_return_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')
                cron_name = import_return_cron.name.replace(
                    '(Do Not Delete)', '')
                name = prefix and prefix + '-' + amazon_seller.name + ' : ' + \
                       cron_name or amazon_seller.name + ' : ' + cron_name
                vals.update({'name': name})
                new_cron = import_return_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': module,
                                                  'name': cron_xml_id + '_seller_%d' % (
                                                      amazon_seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })
        else:
            cron_exist = self.env.ref(module + '.' + cron_xml_id + '_seller_%d' % (amazon_seller.id),
                                      raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_stock_adjustment_report_create_cron(self, seller):
        if self.auto_create_fba_stock_adj_report:
            cron_exist = self.env.ref('amazon_ept.ir_cron_create_fba_stock_adjustment_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.fba_stock_adj_report_interval_number,
                'interval_type': self.fba_stock_adj_report_interval_type,
                'nextcall': self.fba_stock_adj_report_next_execution,
                'code': "model.auto_import_stock_adjustment_report({'seller_id':%d})" % (seller.id),
                'amazon_seller_cron_id': seller.id
            }

            if cron_exist:
                # vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                inv_report_cron = self.env.ref(
                    'amazon_ept.ir_cron_create_fba_stock_adjustment_report', raise_if_not_found=False)
                if not inv_report_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + seller.name + ' : Create Amazon Stock Adjustment Report'
                vals.update({'name': name})
                new_cron = inv_report_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_create_fba_stock_adjustment_report_seller_%d' % (
                                                      seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })
        else:
            cron_exist = self.env.ref('amazon_ept.ir_cron_create_fba_stock_adjustment_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_stock_adjustment_report_process_cron(self, seller):
        if self.auto_process_fba_stock_adj_report:
            cron_exist = self.env.ref('amazon_ept.ir_cron_process_fba_stock_adjustment_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            vals = {
                'active': True,
                'interval_number': self.fba_stock_adj_report_process_interval_number,
                'interval_type': self.fba_stock_adj_report_process_interval_type,
                'nextcall': self.fba_stock_adj_report_process_next_execution,
                'code': "model.auto_process_stock_adjustment_report({'seller_id':%d})" % (seller.id),
                'amazon_seller_cron_id': seller.id
            }
            if cron_exist:
                cron_exist.write(vals)
            else:
                inv_report_cron = self.env.ref(
                    'amazon_ept.ir_cron_process_fba_stock_adjustment_report', raise_if_not_found=False)
                if not inv_report_cron:
                    raise Warning(
                        'Core settings of Amazon are deleted, please upgrade Amazon module to back this settings.')

                name = 'FBA-' + seller.name + ' : Process Stock Adjustment Report'
                vals.update({'name': name})
                new_cron = inv_report_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'amazon_ept',
                                                  'name': 'ir_cron_process_fba_stock_adjustment_report_seller_%d' % (
                                                      seller.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })
        else:
            cron_exist = self.env.ref('amazon_ept.ir_cron_process_fba_stock_adjustment_report_seller_%d' % (
                seller.id), raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active': False})
        return True
