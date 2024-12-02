# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 202-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Milind Mohan(odoo@cybrosys.com)
#
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
    'name': 'Mobile Service Management Pro',
    'version': '16.0.1.0.0',
    'summary': 'An extended version of the module Mobile Service Management.',
    'description': 'An extended version of the module Mobile Service Management.',
    'category': 'Industries',
    'author': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://www.youtube.com/watch?v=jckdD8o3szQ&list=PLeJtXzTubzj_wOC0fzgSAyGln4TJWKV4k&index=51',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['mobile_service_shop'],
    'data': ['views/mobile_service_pro_views.xml',
             'views/res_config_settings_view.xml',
             'wizard/mobile_service_report.xml',
             'reports/mobile_service_report.xml',
             'reports/mobile_service_template.xml',
             'security/ir.model.access.csv'],
    'assets': {
        'web.assets_backend': [
            '/mobile_service_shop_pro/static/src/js/action_manager.js'],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 99,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
