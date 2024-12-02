# -*- coding: utf-8 -*-
{
    "name": "Helpdesk Check List and Approval Process",
    "version": "12.0.2.0.1",
    "category": "Helpdesk",
    "author": "RDP",
    "website": "https://www/rdp.in/",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "crm"
    ],
    "data": [
        # "security/security.xml",
        "security/ir.model.access.csv",
        "views/helpdesk_stage.xml",
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_chek_list.xml",
       
    ],
   
    "summary": "The tool to make sure required jobs are carefully done on this Helpdesk stage",
    "description": """
    Helpdesk checklist for stages
""",
   
   
}