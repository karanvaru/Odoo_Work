# -*- coding: utf-8 -*-
{
    "name": "Activities To-Do Interface",
    "version": "12.0.1.0.3",
    "category": "Productivity",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/activities-to-do-interface-316",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "data/data.xml",
        "wizard/do_with_feedback.xml",
        "wizard/create_new_activity.xml",
        "views/mail_activity_todo.xml",
        "views/res_users.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to process activities one-by-one in a single interface",
    "description": """
    This is the tool to combine all user activities in a single view to process them one-by-one. It let users avoid excess browsing and work efficiently

    The tool might be useful with the <a href=
'https://apps.odoo.com/apps/modules/12.0/recurrent_activities'>module 'Recurring Activities'</a>
    To-do list is available from any Odoo screen to start undertake activities in 2 clicks
    For each activity it is possible to select a required action: to mark as done, to close with feedback, to cancel, to skip and to get back afterwards, to create a new activity based on current data. All actions work in the same way as for the standard activity widget
    From a current to-do activity you may access a related document (e.g. opportunity, task) in a single click  
    The tool let users observe progress in real-time to feel satisfaction of each action done
    Users might select by their own which activity types should be inside to-do list. For example, to work with emails and calls but not with meetings. Configuration is applied per each user individually
    Activities' to-do list is reached in 2 clicks
    Work with activities one by one without extra browsing
    Users feel satisfaction of done job
    Enter feedback to done activity
    Users select their own activity types to work with
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
}