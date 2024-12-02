# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Employee Number Sequence",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Human Resources",
    "summary": """
Employee Sequence No Module, Employee Unique Number App, Employee Sequence Code,
Manage Employees Sequence, Employee Sequence Number, Employee Unique No,
Generate Employee Unique Code, Add Sequence On Employee Odoo
""",
    "description": """It's difficult to manage lots of employees without a unique sequence number. This module auto-generates the employee number sequence. You can change patterns in employee sequence numbers. When you create a new employee, the sequence number assigned automatically. You can allocate multiple employee sequence numbers in a single click.""",
    "version": "16.0.1",
    "depends": [
        "hr",
    ],
    "application": True,
    "data": [
        'data/employee_seq_data.xml',
        'views/res_config_setting_view.xml',
        'views/hr_employee_view.xml',
    ],

    "images": ["static/description/background.png"],
    "auto_install": False,
    "installable": True,
    "currency": "EUR",
    "price": "10"
}
