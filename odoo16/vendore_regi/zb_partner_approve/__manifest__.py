# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2024 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Partner Approval',
    'summary': """This module helps to manage the Customer / Supplier approval process with Draft & Approve Stages. Sales Order / Purchase Order can be confirmed & Invoice can be Posted only when the Partner is in Approved Stage.""",
    'version': '17.0.0.0.2',
    'category': 'Extra Tools',
    "website": "http://www.zbeanztech.com/",
    'description': """
            This module helps to manage the Customer / Supplier approval process with Draft & Approve Stages. Sales Order / Purchase Order can be confirmed & Invoice can be Posted only when the Partner is in Approved Stage..
    """,
    'author': 'ZestyBeanz Technologies',
    'maintainer': 'ZestyBeanz Technologies',
    'support': 'support@zbeanztech.com',
    'license': 'LGPL-3',
    'icon': "/zb_partner_approve/static/description/icon.png",
    'images': ['static/description/banners/banner.gif',],
    'currency': 'USD',
    'price': 0.0,
    'depends': ['base','sale','purchase','account'],
    'data': [
        'security/security.xml',
        'views/res_partner.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
