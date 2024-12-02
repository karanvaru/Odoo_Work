odoo.define('bi_website_shop_product_filter.filter', function(require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var sAnimations = require('website.content.snippets.animation');
    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var websale = require('website_sale.website_sale');

    sAnimations.registry.WebsiteSaleFilter = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.oe_website_sale',
        read_events: {   
            'change form.js_filtervalue input, form.js_filtervalue select': '_onChangeFilter',
        },

        _onChangeFilter: function (ev) {
            
            if (!ev.isDefaultPrevented()) {
                
                ev.preventDefault();
                $(ev.currentTarget).closest("form").submit();
            }
        },
    });

});