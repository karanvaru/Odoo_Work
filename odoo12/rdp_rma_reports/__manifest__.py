    #Developed by RDP-Dayanithi
{
    'name': 'RDP Part360 RMA Reports',
    'version': '12.0.0.0',
    'author': 'RDP',
    'company': 'RDP',
    'website': 'http://www.rdp.in',
    'category': 'Accounting',
    'summary': 'RDP RMA Part360 Reports',
    'description': """ RDP RMA Reports Based on Stages and Opendays """,
    'depends': ['rdp_part360'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',

        # 'views/rma_stage_reports.xml',
        'views/rma_part360_reports.xml',
    ],
    # 'images': [''],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
