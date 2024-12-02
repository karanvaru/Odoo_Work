# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Website Warranty Management 2.0",
  "summary"              :  """The module allows you to Provide, document and track product warranty In the Odoo. The user can add warranty information on the product page of Odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo-Website-Warranty-Management.html",
  "description"          :  """Odoo Website Warranty Management
Manage warranty in Odoo
Product warranty on Website
Add warranty information on product page
Provide warranty on Odoo products
renew product warranty in odoo
Warranty clause on odoo website.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=warranty_management",
  "depends"              :  [
                             'website_sale',
                             'sale_management',
                             'stock',
                            ],
  "data"                 :  [
                             'security/warranty_management.xml',
                             'security/ir.model.access.csv',
                             'data/ir_sequence_data.xml',
                             'report/report_warranty_registration.xml',
                             'report/warranty_report.xml',
                             'data/mail_template_data.xml',
                             'data/data.xml',
                             'views/product_views.xml',
                             'views/warranty_registeration.xml',
                             'views/warranty_history_view.xml',
                             'views/res_partner_views.xml',
                             'views/sale_views.xml',
                             'views/sale_portal_templates.xml',
                             'views/warranty_templates.xml',
                             'views/stock_picking_views.xml',
                             'views/res_config_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "active"               :  False,
  "application"          :  True,
  "installable"          :  True,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}