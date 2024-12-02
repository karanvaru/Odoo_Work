# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'HR Recruitment History',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'summary': 'Track your recruitment pipelines fulfilled in specific time period',
    'description': """
Recruitment refers to the overall process of attracting, shortlisting, selecting and appointing suitable candidates for jobs (either permanent or temporary) within an organization.

This module is useful for Recruiters and Managers to manage their recruitment's historical data and organizations have the opportunity to use their past data to improve their hiring.

By diving into your recruitment analytics and assessing the data you hold on past new recruits - you can devise a more detailed picture of a desirable new hire.

User'll also be able to:
------------------------

- Know when different recruitments were opened and closed for a specific job position.
- Know how many times recruitments were opened for a specific job position.
- Know how many applications were received for a specific job position in each recruitment process.
- Know applicantion received from which internal and external job sources for a specific job position in each recuitment process.
- Know employee strength for a specific job position in each recuitment process.
- Know how many new employees were required for a specific job position in each recuitment process.
- Know how many new employees were hired for a specific job position in each recuitment process.
- Know total number of forcasted employees for a specific job position in each recuitment process.

Historical Data
===============

It provide a quick overview of past recruitment data for the specific job position related to recruitment's open date, closed date, number of employees, number of expected employees, total forecasted employees, number of applications, number of hired employees and more.

""",
    'author': 'Gritxi Consulting Services Pvt. Ltd',    
    'depends': ['base', 'hr_recruitment'],
    'data': ['security/ir.model.access.csv',
            'views/hr_views.xml',
            'views/hr_recruitment_views.xml',
            'views/hr_job_views.xml'],
    'qweb': [],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'price': 30,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: