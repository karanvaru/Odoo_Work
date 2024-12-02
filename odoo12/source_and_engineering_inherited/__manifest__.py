{
    'name': 'Source And Engineering',
    'version': '12.0.1.0.0',
    'sequence': -140, 'author': 'eldho mathew',
    'company': 'rdp',
    'depends': ['base', 'hr', 'mail','source_and_eng','ki_source_eng_time_tracking'],
    'data': [
        'security/ir.model.access.csv',
        'views/source_engineering_inherited.xml'
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
