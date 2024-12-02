odoo.define('website_stock.website_stock_main', function(require) {
    "use strict";

    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.WebsiteStockMain = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.oe_website_sale',

        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var $oe_website_sale = $('.oe_website_sale');
            var $js_quantity = $oe_website_sale.find('.css_quantity.input-group.oe_website_spinner');
            self._websiteStockMain($js_quantity);
            $oe_website_sale.on('change', function(ev) {
                self._websiteStockMain($js_quantity);
            });
            return def;
        },

        _websiteStockMain: function ($js_quantity) {
            if ($("input[name='product_id']").is(':radio'))
                var product = $("input[name='product_id']:checked").attr('value');
            else
                var product = $("input[name='product_id']").attr('value');
            var value = $('#' + product).attr('value');
            var allow = $('#' + product).attr('allow');
            $('.stock_info_div').hide();
            $('#' + product).show();
            if (value <= 0 && allow === 'deny') {
                $('#add_to_cart').hide();
                $js_quantity.hide();
            } else {
                $('#add_to_cart').show();
                $js_quantity.show();
            }
        },
    });
});


/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* Responsible Developer:- Sunny Kumar Yadav */