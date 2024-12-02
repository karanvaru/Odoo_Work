{
    'name': "Search Product and Picking",
    'summary': 'Search Product and Picking',
    'description': """
        Search Product and Picking
    """,
    "version": "14.8",
    "category": "Warehouse",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'stock',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/barcode_search_wizard_view.xml',
        'views/picking_search_action.xml',
        'views/template.xml'
    ],
    'qweb': ['static/src/xml/dashboard.xml'],
    "application": False,
    'installable': True,
}
