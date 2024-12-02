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
  "name"                 :  "Website Pre-Order",
  "summary"              :  "The customers can place pre-orders for the selected products on the Odoo website which are out of stock.",
  "category"             :  "Website",
  "version"              :  "1.0.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Pre-Order.html",
  "description"          :  """Odoo Website Pre-Order
Place pre-orders on website
Pre orders on odoo
Advanced orders on website
Odoo pre orders
Odoo website advanced orders
Order out of stock product
Out of stock orders
Odoo back orders
Website backorders""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_preorder&lout=1&custom_url=/",
  "depends"              :  [
                             'website_stock',
                             'website_sale_delivery',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'security/website_preorder_security.xml',
                             'data/pre_order_mail_template.xml',
                             'data/preorder_config_demo.xml',
                             'wizard/notify_preorder_line.xml',
                             'views/res_config_view.xml',
                             'views/template.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/inherit_product_view.xml',
                            ],
  "demo"                 :  [
                             'data/preorder_product_demo.xml',
                             'demo/sale_order_demo_data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  60,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
