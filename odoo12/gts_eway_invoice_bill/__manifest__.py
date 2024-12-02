# -*- encoding: utf-8 -*-

{
    'name': 'GST EwayBill',
    'version': '12.0.0.1',
    'category': 'Integration',
    'description': """
        module to allow Eway Bill integration with Taxpro
        Documentation
        https://help.taxprogsp.co.in/ewb/authentication_url___method_get_.htm?ms=AgI%3D&st=MA%3D%3D&sct=MA%3D%3D&mw=MjQw&ms=AgI%3D&st=MA%3D%3D&sct=MA%3D%3D&mw=MjQw
    """,
    'author': 'Geo Technosoft',
    'sequence': 1,
    'website': 'https://www.geotechnosoft.com',
    'depends': ['base', 'sale_management', 'stock', 'purchase', 'contacts', 'web_notify', 'l10n_in',
                'delivery', 'account'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'data/uom_mapping.xml',
        'data/uom_data.xml',
        'data/sub_supply_type_data.xml',
        'wizard/vehicle_view.xml',
        'wizard/consolidate_view.xml',
        'wizard/cancel_bill_view.xml',
        'wizard/extend_validity_wizard_view.xml',
        'wizard/update_tax_view.xml',
        'views/eway_configuration_view.xml',
        'views/transporter_view.xml',
        # 'views/unit_quantity_code_view.xml',
        'views/uom_mapping_view.xml',
        'views/uom_uom_views.xml',
        'views/state_view.xml',
        'views/company_view.xml',
        # 'views/stock_picking_view.xml',
        'views/account_invoice_views.xml',
        'views/res_partner_view.xml',
        'views/stock_warehouse.xml',
        # 'views/transportation_menu.xml',
    ],
    'application': True,
    'installable': True,
}
