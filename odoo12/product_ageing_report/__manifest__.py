# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Avinash N.K(odoo@cybrosys.com)
#	         Anusha P P(odoo@cybrosys.com)
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

{
    'name': "Stock Ageing Analysis",
    'version': '12.0.2.0.1',
    'summary': """Product Ageing Analysis With Filterations""",
    'description': """With this module, we can perform stock ageing analysis with optional filters such
                as location, category""",
    'author': "Cybrosys Techno Solutions",
    'website': "https://www.cybrosys.com",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'category': 'Stock',
    'depends': ['product', 'stock'],
    'data': ['views/action_manager.xml',
             'wizard/product_ageing.xml',
             'report/report_ageing_products.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
