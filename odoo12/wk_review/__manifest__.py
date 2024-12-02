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
  "name"                 :  "Website: Product Review",
  "summary"              :  "The module allows you to display customer reviews and feedback on the Odoo website. The customer can also give a thumbs up or thumbs dow to a review.",
  "category"             :  "Website",
  "version"              :  "2.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Product-Review.html",
  "description"          :  """Odoo Website: Product Review
Odoo Website Product Review
Customer ratings on Odoo website
Customer reviews on website
Customer feedback on product page
Odoo share customer product ratings""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_review",
  "depends"              :  [
                             'sale_management',
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/review_security.xml',
                             'security/ir.model.access.csv',
                             'views/review_backend_view.xml',
                             'views/review.xml',
                             'views/res_config_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'data/wk_review_data.xml',
                            ],
  "demo"                 :  ['demo/wk_review_demo_data.xml'],
  "css"                  :  ['static/src/css/review.css'],
  "js"                   :  ['static/src/js/review.js'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}