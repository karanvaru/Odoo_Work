{
    'name': 'RDP Helpdesk Process Improvement',
    'version': '12.0.0.1',
    'category': 'Project',
    'author': 'RDP',
    'summary': 'This module help us to improve Helpdesk Process Improvement',
    'website': 'www.rdp.in',
    'sequence': '10',
    'description': """
     This module help us to improve Helpdesk Process Improvement'
    """,
    'depends': ['base', 'mail', 'helpdesk', 'rdp_helpdeskquality_audit', 'rdp_ked_escalation', 'five_why', 'rdp_sale_challenges', 'asp_partner', 'product_sar','rdp_global_feedback'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizards/hpi.xml',
        'wizards/hpi_cancel_view.xml',
        'wizards/hpi_future_view.xml',
        'wizards/hpi_kam_escalation_view.xml',
        'wizards/hpi_quality_audit_view.xml',
        'wizards/hpi_five_why_view.xml',
        'wizards/hpi_global_feedback_view.xml',
        'wizards/message_wizard_view.xml',
        'wizards/hpi_sales_challenge_view.xml',
        'wizards/hpi_asp_app_view.xml',
        'wizards/hpi_pspr_view.xml',
        'views/helpdesk_process_improvement_view.xml',
        'views/helpdesk_view.xml',
        'views/quality_audit_hdpi_view.xml',
        'views/kam_escalation_hdpi_view.xml',
        'views/five_why_extended.xml',
        'views/global_feedback_hdpi_view.xml',
        'views/sales_challenge_extended.xml',
        'views/asp_app_extended.xml',
        'views/pspr_extended.xml',
    ],

    # 'license': 'OPL-1',
    'application': True,
    'installable': True,


}