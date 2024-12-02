{
    'name': 'RDP Million Tasks',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to create million tasks ',
    'website': 'www.rdp.in',
    'sequence': '10',
    'depends': ['base', 'hr_recruitment', 'hr','mail'],
    'data': [

        'security/ir.model.access.csv',
        'views/million_tasks_views.xml',
        'views/job_position_view.xml',
        'data/data.xml'

    ],

    'license': 'OPL-1',
    'application': True,
    'installable': True,


}
