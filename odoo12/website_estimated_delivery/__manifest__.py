# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
{
  "name"                 :  "Website Estimated Delivery",
  "summary"              :  "Show estimated delivery time for products based on zipcodes",
  "category"             :  "Website",
  "version"              :  "2.0.01",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo-Website-Estimated-Delivery.html",
  "description"          :  "http://webkul.com/blog/odoo-website-estimated-delivery-2/",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_estimated_delivery&version=12.0&custom_url=/",
  "depends"              :  [
                             'website_sale_delivery',
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'views/website_estimated_delivery_view.xml',
                             'views/estimated_deliver_conf_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/templates.xml',
                             'security/ir.model.access.csv',
                            ],
  "demo"                 : ['data/demo_data.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  45,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}