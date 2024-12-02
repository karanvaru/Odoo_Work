# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indian - Accounting Custom Reports',
    'version': '1.1',
    'description': """
Accounting reports for India
================================
    """,
    'category': 'Accounting/Localizations/Reporting',
    'depends': ['l10n_in_reports'],
    'data': [
        'security/l10n_in_custom_reports_security.xml',
        'security/ir.model.access.csv',
        'data/account_financial_html_report_data.xml',
        'views/account_invoice_views.xml',
        'views/account_journal_views.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_view.xml',
        'views/port_code_views.xml',
        'views/res_partner_views.xml',
        'views/account_tax_views.xml',
        'views/uom_uom_views.xml',
    ],
    'demo': [],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
}
