{
    'name': 'RDP CRM Leads Dashboard',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP ',
    'summary': 'This module help us to develop Leads Dashboard',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to develop Leads Dashboard
    """,
    'depends': ['base', 'crm'],
    'data': [
         'views/leads_button.xml',
         'views/oppurtunity_buttons_view.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}