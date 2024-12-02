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
  "name"                 :  "Website Product Tags",
  "summary"              :  """The Odoo user can assign the tags to the website products so the customers can filter the products using the product tags.""",
  "category"             :  "Website",
  "version"              :  "0.2",
  "sequence"             :  1.0,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-Product-Tags.html",
  "description"          :  """Odoo Website Product Tags
Odoo Filter Products By Tags
Website Sort products with tags
POS product tags
Add products tags to POS products
Categorize with tags in POS
Create product tags in POS""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_product_tags&version=12.0&custom_url=/shop",
  "depends"              :  [
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/template.xml',
                             'views/wk_product_tags.xml',
                             'views/res_config.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'data/data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}