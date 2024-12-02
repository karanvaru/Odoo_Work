# -*- coding: utf-8 -*-
{
    "name": "Purchase Order Approval Check Lists",
    "version": "12.0.1.0.1",
    "category": "Purchases",
    "author": "faOtools",
    "website": "https://faotools.com/apps/12.0/purchase-order-approval-check-lists-372",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "purchase"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
        "views/check_company_list.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure a purchase order is ready for the next stage",
    "description": """
For the full details look at static/description/index.html

* Features * 
- Check lists per order state and company
- Purchase multi approval flow
- Approval history
- Indicative checklist to-do
- Super checklist user

* Extra Notes *
- How check list points might be missed
- When Odoo would warn purchase users to confirm check lists


#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "40.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=121&ticket_version=12.0&url_type_id=3",
}