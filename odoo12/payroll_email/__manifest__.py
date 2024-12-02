# -*- coding: utf-8 -*-
###################################################################################
#    Payroll Email Project 
#
#    E-Soft Solution
#    Copyright (C) 2018-TODAY  E-Soft Solution (<https://www.sagarnetwork.com>).
#    Author: Sagar Jayswal (<https://www.sagarnetwork.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; See the GNU Affero General Public 
#    License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Payroll Email/Mass E-mail',
    'version': '12.0.1.0.0',
    'summary': """Helps to send payroll Slip to Employees through Email.""",
    'description': 'This module helps you to send payslip through Email.',
    'category': 'Generic Modules/Human Resources',
    'author': 'E-soft Solution',
    'company': 'E-Soft Solution',
    'website': "https://www.sagarnetwork.com",
    'depends': ['base', 'hr_payroll', 'mail', 'hr'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/hr_payroll.xml',
        'views/hr_payslip_wizard_view.xml',
        'views/hr_mass_payroll_wizard.xml'
        
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
