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
  "name"                 :  "Website Refer And Earn FAQ",
  "summary"              :  "Odoo Website Refer And Earn FAQ allows you to add the frequently asked questions regarding Referral Points.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Saurabh Gupta",
  "website"              :  "https://store.webkul.com/Odoo-Website-Refer-And-Earn-FAQ.html",
  "description"          :  """ Website Refer And Earn Frequently Asked Question
Odoo Website Refer And Earn FAQ
Website Refer And Earn FAQ
FAQ for Refer And Earn
Refer And Earn FAQ
Refer And Earn FAQ in Odoo Website
Refer And Earn Frequently Asked Questions in Odoo
Referral Points FAQ
Earn Referral Points FAQ
Refer a friend FAQ
Referral Bonus FAQ
Referral FAQ""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=refer_and_earn_faq",
  "depends"              :  ['refer_and_earn'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/refer_and_earn_faq_template.xml',
                             'views/refer_and_earn_faq_view.xml',
                             'data/sequence_data.xml',
                            ],
  "demo"                 :  ['data/demo_data_faq.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  12,
  "currency"             :  "EUR",
}