/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('website_preorder.website_preorder_extension', function(require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;

    $(document).ready(function() {
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            var $js_quantity = $(this).find('.css_quantity.input-group.oe_website_spinner');
            var add_qty = $(this).find('input[name="add_qty"]').val();
            var preorder = $('#preorder').data('preorder');
            var preorder_product = $('#preorder_product').data('preorder_product');
            var max_qty_order = $('#max_qty_order').data('max_qty_order');
            if (preorder && preorder_product) {
                $('#add_to_cart_preorder').addClass('js_check_product');
                $('.wk_hidden_stock').removeClass('wk_show_stock');
                $js_quantity.show();
            }
            website_stock_main($js_quantity);
            $(oe_website_sale).on('change', function(ev) {
                website_stock_main($js_quantity);
            });
        });

        function website_stock_main($js_quantity) {
            if ($("input[name='product_id']").is(':radio'))
            {
                var product = $("input[name='product_id']:checked").attr('value');
            }
            else
            {
                var product = $("input[name='product_id']").attr('value');
            }
            var value = $('#' + product).attr('value');
            var allow = $('#' + product).attr('allow');
            var add_qty = $('.oe_website_sale').find('input[name="add_qty"]').val();
            var preorder = $('#preorder').data('preorder');
            var preorder_product = $('#preorder_product').data('preorder_product');
            var minimum_qty = $('#minimum_qty').data('minimum_qty');
            var $product = $('#' + product);
            $('.stock_info_div').hide();
            $('#' + product).show();
            if (value <= 0 && allow === 'deny') {
                if (preorder && preorder_product) {
                    $product.addClass('wk_show_stock');
                    $product.find('#add_to_cart_preorder').removeClass('disabled wk_hidden_stock');
                    $product.find('#add_to_cart_preorder').addClass('js_check_product');
                    $('#add_to_cart').hide();
                    $product.find('#website-stock-div').hide();
                    $product.find('#pre_order_stock_div').show();
                    $js_quantity.show();
                    if (add_qty > max_qty_order) {
                        $js_quantity.prevObject[0].value = parseFloat(max_qty_order)
                    }
                }
                else{
                    $('#add_to_cart').hide();
                    $js_quantity.hide();
                }
            } else {
                if (preorder && preorder_product) {
                    ajax.jsonRpc("/shop/cart/order/check", 'call', {
                        'product_id': product,
                        'value':value,
                        'add_qty':add_qty,
                    }).then(function(result) {
                        if(result){
                            $('#add_to_cart').hide();
                            $product.find('#website-stock-div').hide();
                            $product.find('#pre_order_stock_div').show();
                            $product.find('#add_to_cart_preorder').removeClass('disabled wk_hidden_stock');
                            $product.find('#add_to_cart_preorder').addClass('js_check_product');
                            if (add_qty > max_qty_order) {
                                $js_quantity.prevObject[0].value = parseFloat(max_qty_order)
                            }
                        }
                        else{
                            $product.find('#pre_order_stock_div').hide();
                            $('#add_to_cart').show();
                            $product.find('#website-stock-div').show();
                        }
                    });
                }
                else{
                    $('#add_to_cart').show();
                    $js_quantity.show();
                }
            }
        }
    });
});
