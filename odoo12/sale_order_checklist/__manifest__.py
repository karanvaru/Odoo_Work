# -*- coding: utf-8 -*-
{
    "name": "Sale Order Approval Check Lists",
    "version": "12.0.1.0.1",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/12.0/sale-order-approval-check-lists-370",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/crm_team.xml",
        "views/sale_order.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure a sale order is ready for the next stage",
    "description": """
For the full details look at static/description/index.html

* Features * 
- Check lists per sales team and order state
- Sale order multi approval flow
- Approval history
- Indicative checklist to-do
- Super checklist user

* Extra Notes *
- How check list points might be missed
- When Odoo would warn salespersons to confirm check lists


#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "48.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=120&ticket_version=12.0&url_type_id=3",
}