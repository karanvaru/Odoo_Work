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
  "name"                 :  "Website Product Stock",
  "summary"              :  "The module allows you to display whether a product is in stock or out of stock on the basis of in hand or forecasted quantity in Odoo.",
  "category"             :  "Website",
  "version"              :  "1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Product-Stock.html",
  "description"          :  """Odoo Website Product Stock
Show out of stock message
Show in stock message
Show product Quantity update
Order out of stock product on website""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_stock",
  "depends"              :  [
                             'website_sale',
                             'stock',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/res_config_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'data/stock_config_demo.xml',
                             'views/website_stock_extension.xml',
                             'views/templates.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}