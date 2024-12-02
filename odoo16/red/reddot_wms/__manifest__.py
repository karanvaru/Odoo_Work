# -*- coding: utf-8 -*-
{
    'name': "Reddot WMS",
    'summary': """
        To add reports and features specifically for ReddotDistribution""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Douglas Tabut",
    'website': "https://www.reddotdistribution.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Inventory',
    'version': '0.2',
    'installable': True,
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['delivery','product','stock','ob_freight_management_system','web','product_images', 'multi_level_approval', 'multi_level_approval_configuration'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/wms_security.xml',
        'data/ir_sequence.xml',
        'report/custom_deliveryslip_report.xml',
        'views/pre_alerts.xml',
        'views/stock_picking_views.xml',
        'views/freight_order.xml',
        'views/pickings_report.xml',
        'views/report_deliveryslip_inherit.xml',
        'views/stock_location.xml',
        'views/stock_route.xml',
        'views/custom_clearance.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_order.xml',
        'views/product_template.xml',
        'views/server_actions.xml',
        'views/po_template.xml',
        'views/notifications.xml',
        'views/purchase_order_lines.xml',
        'views/product_category.xml'
    ],
    # 'web.assets_backend': [
    #             'reddot_wms/static/views/*.js',
    #             'reddot_wms/static/views/*.xml'
    # ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
