# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One POS Reports",
    "author": "Softhealer Technologies",
    "license": "OPL-1",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "16.0.3",
    "category": "Extra Tools",
    "summary": "POS Sales Report Based On Analysis,Compare Customer By Sales Report,Compare Products Based On Selling, Salesperson Wise Payment Report,Point Of Sale Report By User,Sales Report By Tax,Sale Report By Date And Time,Point Of Sale Reports,POS Report Odoo",
    "description": """ All in one POS(Point Of Sale) report useful to provide different POS and payment reports to do analysis. A POS analysis report shows the trends that occur in a company's sales volume over time. In its most basic form, a sales analysis report shows whether sales are increasing or declining. At any time during the fiscal year, sales managers may analyze the trends in the report to determine the best course of action. POS reports are a record of POS activity over a particular period. """,
    "depends": ["point_of_sale", "account", "pos_hr"],
    
    "data": [

        
        "sh_pos_z_report/security/ir.model.access.csv",
        "sh_pos_z_report/views/pos_config_views.xml", 
        "sh_pos_z_report/views/res_config_settings_views.xml", 
        "sh_pos_z_report/reports/report_zdetails.xml",
        "sh_pos_z_report/reports/pos_z_report_detail.xml",
        "sh_pos_z_report/views/pos_session_z_report.xml",
        "sh_pos_z_report/wizard/pos_z_report_wizard.xml",
        "sh_pos_z_report/views/res_users_views.xml",
        "sh_pos_z_report/views/hr_employee_views.xml",

        'sh_day_wise_pos/security/ir.model.access.csv',
        'sh_day_wise_pos/wizard/sh_pos_order_report_views.xml',
        'sh_day_wise_pos/report/sh_day_wise_pos_report_templates.xml',
        'sh_day_wise_pos/views/sh_day_wise_pos_views.xml',

        "sh_payment_pos_report/security/sh_payment_pos_report_doc_groups.xml",
        "sh_payment_pos_report/security/ir.model.access.csv",
        "sh_payment_pos_report/wizard/sh_pos_payment_report_wizard_views.xml",
        "sh_payment_pos_report/report/sh_payment_pos_report_doc_report_templates.xml",
        "sh_payment_pos_report/views/sh_payment_report_views.xml",

        "sh_pos_report_user/security/ir.model.access.csv",
        "sh_pos_report_user/wizard/sh_pos_report_user_wizard_views.xml",
        "sh_pos_report_user/report/sh_user_report_doc_report_templates.xml",
        "sh_pos_report_user/views/sh_pos_report_user_views.xml",

        "sh_top_pos_customer/security/ir.model.access.csv",
        "sh_top_pos_customer/wizard/sh_tc_pos_top_customer_wizard_views.xml",
        "sh_top_pos_customer/report/sh_tc_pos_doc_report_templates.xml",
        "sh_top_pos_customer/views/sh_top_pos_customer_views.xml",

        "sh_top_pos_product/security/ir.model.access.csv",
        "sh_top_pos_product/wizard/sh_tsp_top_pos_product_wizard_views.xml",
        "sh_top_pos_product/views/sh_tsp_top_pos_product_views.xml",
        "sh_top_pos_product/report/sh_top_pos_product_doc_views.xml",

        "sh_pos_profitability_report/security/sh_pos_profitibility_report_groups.xml",
        "sh_pos_profitability_report/report/pos_order_line_views.xml",

        "sh_customer_pos_analysis/security/ir.model.access.csv",
        'sh_customer_pos_analysis/report/sh_cus_pos_analysis_doc_report_templates.xml',
        'sh_customer_pos_analysis/wizard/sh_pos_analysis_wizard_views.xml',
        'sh_customer_pos_analysis/views/sh_customer_pos_analysis_views.xml',

        "sh_pos_by_category/security/ir.model.access.csv",
        "sh_pos_by_category/report/sh_pos_by_category_doc_report_templates.xml",
        "sh_pos_by_category/wizard/sh_pos_category_wizard_views.xml",
        "sh_pos_by_category/views/sh_pos_by_product_category_views.xml",

        "sh_pos_invoice_summary/security/ir.model.access.csv",
        "sh_pos_invoice_summary/report/sh_pos_inv_summary_doc_report_templates.xml",
        "sh_pos_invoice_summary/wizard/sh_pos_inv_summary_wizard_views.xml",
        "sh_pos_invoice_summary/views/sh_pos_invoice_summary_views.xml",

        "sh_pos_product_profit/security/ir.model.access.csv",
        "sh_pos_product_profit/report/sh_pos_product_profit_doc_report_templates.xml",
        "sh_pos_product_profit/wizard/sh_pos_product_profit_wizard_views.xml",
        "sh_pos_product_profit/views/sh_pos_product_profit_views.xml",

        "sh_product_pos_indent/security/ir.model.access.csv",
        "sh_product_pos_indent/report/sh_pos_product_indent_doc_report_templates.xml",
        "sh_product_pos_indent/wizard/sh_pos_product_indent_wizard_views.xml",
        "sh_product_pos_indent/views/sh_product_pos_indent_views.xml",

        'sh_pos_sector_report/security/ir.model.access.csv',
        'sh_pos_sector_report/wizard/sh_pos_section_report_wizard_views.xml',
        'sh_pos_sector_report/views/sh_pos_sector_views.xml',

    ],
    'assets': {'point_of_sale.assets': [
            "sh_pos_reports/static/sh_pos_z_report/src/js/**/*",
            "sh_pos_reports/static/sh_pos_z_report/src/scss/pos.scss",
            "sh_pos_reports/static/sh_pos_z_report/src/xml/**/*",
        ]
    },
    "images": ["static/description/background.gif", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 70,
    "currency": "EUR"
}
