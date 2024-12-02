# -*- coding: utf-8 -*-
{
    "name": "Recurring Activities",
    "version": "12.0.1.0.3",
    "category": "Productivity",
    "author": "faOtools",
    "website": "https://faotools.com/apps/12.0/recurring-activities-336",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/recurrent_activity_template.xml",
        "views/view.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to plan and generate recurring activities according to the flexible timetable rules",
    "description": """
For the full details look at static/description/index.html

* Features * 
- Recurrent activity for any existing Odoo object
- Configurable recurrence
- Secured activities

* Extra Notes *
- How flexible recurrence might be
- Access for activity recurrence rules


#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "44.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=107&ticket_version=12.0&url_type_id=3",
}