# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Helpdesk Ticket Timer with Timesheet",
    "version" : "12.0.0.188",
    "category" : "Website",
    "depends" : ['base','helpdesk','helpdesk_sale_timesheet'],
    "author": "BrowseInfo",
    "summary": 'Ticket Timer for Helpdesk Timer for ticket start and stop timer pause helpdesk start helpdesk timer stop helpdesk timer start and stop helpdesk timer helpdesk timesheet timer record timesheet with timer start timesheet timer task timer stop timesheet timer',
    "description": """

        Add timer option on helpdesk ticket as clocker in odoo,
        Start Stop and  Pause helpdesk ticket timer in odoo,
        Start ticket timer wizard or confirmation in odoo,
        Stop ticket timer wizard or confirmation in odoo,
        When two timer start once that time validation generated in odoo,
        User can use one timer at a time in odoo,
    
    """ , 
    "website" : "https://www.browseinfo.in",
    "price": 25,
    "currency": 'EUR',
    "data": [
        'security/ir.model.access.csv',
        'views/view_helpdesk_ticket.xml',
        'views/ticket_assests.xml',
        'wizard/stop_ticket_timer.xml',
        'wizard/start_ticket_timer.xml',
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url" : 'https://youtu.be/3CUxH9_ahtg',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
