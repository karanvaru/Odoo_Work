# -*- coding: utf-8 -*-pack
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information
    'name': 'Amazon Odoo Connector',
    'version': '12.0.20',
    'category': 'Sales',
    'license': 'OPL-1',
    'summary' : 'Amazon Odoo Connector helps you integrate & manage your Amazon Seller Account operations from Odoo. Save time, efforts and avoid errors due to manual data entry to boost your Amazon sales with this connector.',

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Dependencies
    'depends': ['auto_invoice_workflow_ept','common_connector_library','sale_stock', 'iap','stock',],

    # Views
    'data': [

             'data/ir_cron.xml',
             #'data/demo_data.csv',
             'data/product_data.xml',
             'data/import_product_attachment.xml',
             'data/amazon.payment.type.option.ept.csv',

             'data/amazon_transaction_type.xml',
             'data/amazon.developer.details.ept.csv',
	         'data/amazon_delivery_carrier_code.xml',

             # added by twinkal to merge with FBA
             'data/amazon_return_reason_data.xml',
             'data/fr_code.xml',
             'data/de_code.xml',
             'data/it_code.xml',
             'data/es_code.xml',
             'data/pl_code.xml',
             'data/uk_code.xml',
             'data/us_code.xml',
             'data/ca_code.xml',
             'data/prep.instruction.csv',
             'data/res_partner_data.xml',
             'data/amazon.adjustment.reason.group.csv',
             'data/amazon.adjustment.reason.code.csv',

             'security/res_groups.xml',
             'view/return_reason.xml',
             'view/res_config_view.xml',
             'view/amazon_seller.xml',
             'security/ir.model.access.csv',

             'view/product_brand_view.xml',
             'view/base_browse_node.xml',
             'view/browse_node.xml',
             'view/product_view.xml',
             'view/process_import_export.xml',
             # added by twinkal
             'view/inbound_shipment_plan.xml',
             'view/amazon_outbound_order_wizard_view.xml',
             'view/sales_view.xml',
             'view/invoice_view.xml',
             'view/settlement_report.xml',
             'report/sale_report_view.xml',
             'view/order_refund_view.xml',
             'view/stock_view.xml',
             'view/stock_inventory.xml',
             'view/inbound_shipment.xml',
             'view/order_return_config_view.xml',
             'view/feed_submission_history.xml',
             'view/amazon_file_process_job.xml',
             # 'view/amazon_report_wizard.xml',

             'view/stock_picking_seller.xml',
             'view/instance_view.xml',

             'view/auto_work_flow_configuration.xml',
             'view/tax_code_view.xml',
             'view/product_wizard_view.xml',
             # addded by twinkal to merger fba module

             'view/inbound_shipment_wizard_view.xml',
             'view/inventory_wizard_view.xml',
             'view/switch_product_wizard_view.xml',

             'view/import_inbound_shipment_report_wizard_view.xml',
             'view/import_product_inbound_shipment_wizard.xml',
             'view/inbound_shipment_details_wizard.xml',
             'view/amazon_live_stock_report_view.xml',
             'view/procurement_group.xml',
             'view/product_ul.xml',

             'view/cancel_order_wizard_view.xml',
             'view/res_country.xml',
             'view/web_templates.xml',
             #code comment by dhaval
             # uncommented by twinkal to merge FBA code and also commented code which daval sir dont want to execute
            'view/stock_quant_package.xml',
             'view/stock_warehouse.xml',
             'view/amazon_transaction.xml',
             'view/delivery.xml',
             'view/active_product_listing_view.xml',
             'view/account_fiscal_position.xml',
             'view/amazon_category.xml',
             #'view/amazon_category_data.xml',
             'view/product_attribute.xml',
             'view/ir_sequence.xml',

             'view/account_move_view.xml',
             'view/account_move_line_view.xml',
             'view/stock_move_view.xml',

            # added by twinkal
            'view/shipping_report.xml',
            'view/order_return_report.xml',
            'view/email_template.xml',

            'view/amazon_stock_adjustment_config.xml',
            'view/import_product_removal_order_wizard.xml',
            'view/removal_order_config.xml',
            'view/removal_order_view.xml',
            'view/removal_order_report.xml',

             'view/mail_subtype.xml',
             'view/inbound_shipment_labels_wizard.xml',
             'view/stock_adjustment_view.xml',
             'view/adjustment_reason.xml',
             'view/amazon_stock_adjustment_group.xml',
             'view/amazon_inbound_import_shipments.xml',

             'security/security.xml',

#            'view/create_removal_orders_wizard_view.xml',
             'view/stock_location_route.xml',
             'view/fba_cron_configuration.xml',
             'view/fbm_cron_configuration.xml',
             'view/global_cron_configuration.xml',
             'view/settlement_report_configure_fees_ept.xml',

             #'data/amazon.base.browse.node.ept.csv',
             #'data/amazon.uom.type.ept.csv',
             #'data/amazon.uom.value.ept.csv',
             #'data/amazon.attribute.ept.csv',
             #'data/amazon.attribute.value.ept.csv',
             #'data/amazon.tax.code.ept.csv',
             #'data/amazon.cspia.warning.ept.csv',

             #'data/amazon.tsd.language.ept.csv',
             #'data/amazon.tsd.warning.ept.csv',
             #'data/amazon.variation.theme.ept.csv',
             #'data/amazon.transaction.type.csv',

             ],
    # Odoo Store Specific
    'images': ['static/description/cover.jpg'],

    #Technical
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://www.emiprotechnologies.com/free-trial?app=amazon-ept&version=12&edition=enterprise',
    'application' : True,
    'price': 479.00,
    'currency': 'EUR',
}
