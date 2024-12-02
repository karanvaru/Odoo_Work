# -*- coding: utf-8 -*-
{
    "name": "Activities Daily Reminder",
    "version": "12.0.1.2.3",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/activities-daily-reminder-242",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "views/mail_activity_view.xml",
        "data/cron.xml",
        "data/mail_activity_data.xml"
    ],
    "summary": "The tool to notify users of assigned to them activities",
    "description": """
    This is the tool to remind users of activities which deadline is today or which deadline has already passed

    Configure your own single-list reminders for any Odoo records using <a href="https://apps.odoo.com/apps/modules/12.0/total_notify/">the tool All-In-One Lists Reminders</a>
    Some email clients / browser might partially spoil the table appearance
    The tool gathers all activities which should be done urgently: today or in the Past
    The reminder is sent <strong>for each user</strong> individually if he/she has such activities
    Notification is done as a <strong>single</strong> email with all activities combined in the table. Each line has a link for an instant access to a <strong>parent</strong> activity record (related opportunity, partner, sales order, etc.). No dozens useless emails
    Only important activities are included into the reminder. Choose activity types which should be considered for reminders
    A reminder is sent once per day, but you can change frequency or time. Look at the 'Configuration' tab
    You may also modify email appearance and set. Look at the 'Configuration' tab
    All activities are combined in a single to-do list
    Choose activity types to be included into reminders
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
}