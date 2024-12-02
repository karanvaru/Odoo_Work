/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('website_preorder.website_preorder_validation', function(require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');

    var _t = core._t;
    var temp = '1';

    $(document).ready(function() {

        // $('#wrap').on('click','[href="/shop/checkout"]',function(ev){
        $(".oe_website_sale a[href='/shop/checkout']").on('click', function(ev) {
            var $checkout = $(this);
            ev.preventDefault();
            $('.pre-order-alert').each(function(){
                ev.preventDefault();
                var $this = $(this);
                var $input = $this.prev();
                var preorder_product_id = parseInt($this.find('#preorder_product_id').data('preorder_product_id'), 10);
                var value = parseInt($input.find('.js_quantity').val(), 10);
                ajax.jsonRpc("/minimum/quantity/validation", 'call', {
                    'product_id': preorder_product_id,
                    'set_value': value,
                }).then(function(result) {
                    if(result){
                        $this.show();
                        setTimeout(function() {$this.hide()}, 12000);
                    }
                    else{
                        window.location.href = window.location.origin+'/shop/checkout'
                    }
                });
            });
        });

        if (!$('.oe_website_sale').length) {
            return $.Deferred().reject("DOM doesn't contain '.oe_website_sale'");
        }

        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;
            var preorder_value = $('#preorder_value').data('preorder_value');


            $(oe_website_sale).on("click", '#add_to_cart_preorder', function(event) {
                event.preventDefault();
                event.stopPropagation();
                var $form = $(this).closest('form');
                if ($("input[name='product_id']").is(':radio'))
                    var product_id = $("input[name='product_id']:checked").attr('value');
                else
                    var product_id = $("input[name='product_id']").attr('value');
                var add_qty = parseFloat($form.find('input[type="text"][name="add_qty"]').first().val(), 10);
                var preorder_product = $('#preorder_product').data('preorder_product');
                ajax.jsonRpc("/shop/cart/order", 'call', {
                    'product_id': product_id,
                    'add_qty': add_qty
                }).then(function(result) {
                    if (!result.status) {
                        $('#add_to_cart_preorder').removeClass('a-submit');                        
                        $('#add_to_cart_preorder').popover({
                            content: _t(result.msg),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $('#add_to_cart_preorder').popover('show');
                        setTimeout(function() {
                            $('#add_to_cart_preorder').popover('dispose')
                        }, 3000);
                    } else {
                        $('#add_to_cart_preorder').popover('dispose');
                        temp = add_qty.toString();
                        $form.submit();
                    }
                });
            });
            $(oe_website_sale).off("change", ".oe_cart input.js_quantity")
            $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function(ev) {
                var $input = $(this);
                var value = parseInt($input.val(), 10);
                var $dom = $(this).closest('tr');
                var line_id = parseInt($input.data('line-id'), 10);
                var product_id = parseInt($input.data('product-id'), 10);
                ajax.jsonRpc("/shop/cart/order/check/msg", 'call', {
                    'line_id': line_id,
                    'product_id': parseInt($input.data('product-id'), 10),
                    'set_qty': value
                })
                .then(function(msg) {
                    if (msg) {
                        $dom.popover('dispose');
                        $dom.popover({
                            content: _t("You are Trying to Add More Than Available Quantity of Product."),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $dom.popover('show');
                    } else {
                        $dom.popover('dispose');
                    }
                });
            });
            // function for '/shop/product' page product quantity vailidation on click of add to cart button
            $(oe_website_sale).off("click", "#add_to_cart");
            $(oe_website_sale).on("click", '#add_to_cart', function(event) {
                var $form = $(this).closest('form');
                if ($("input[name='product_id']").is(':radio'))
                    var product_id = $("input[name='product_id']:checked").attr('value');
                else
                    var product_id = $("input[name='product_id']").attr('value');
                var add_qty = parseFloat($form.find('input[type="text"][name="add_qty"]').first().val(), 10);
                var preorder_product = $('#preorder_product').data('preorder_product');
                ajax.jsonRpc("/shop/cart/order", 'call', {
                    'product_id': product_id,
                    'add_qty': add_qty
                }).then(function(result) {
                    if (!result.status) {
                        event.preventDefault(event);
                        window.location.href = "#";
                        $('#add_to_cart').popover({
                            content: _t(result.msg),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $('#add_to_cart').popover('show');
                        setTimeout(function() {
                            $('#add_to_cart').popover('dispose')
                        }, 3000);
                    } else {
                       $('#add_to_cart').popover('dispose');
                       temp = add_qty.toString();
                    }
                });
            });

            // function for '/shop/product' page product quantity vailidation on increment of product quantity
            $(oe_website_sale).find('input[type="text"][name="add_qty"]').off('change');
            $(oe_website_sale).find('input[type="text"][name="add_qty"]').on('change', function(ev)
            {
                var $form = $(this).closest('form');
                if ($("input[name='product_id']").is(':radio'))
                    var product_id = $("input[name='product_id']:checked").attr('value');
                else
                    var product_id = $("input[name='product_id']").attr('value');
                var add_qty =  parseFloat($form.find('input[type="text"][name="add_qty"]').first().val(),10);
                if(!add_qty){
                    $form.find('input[type="text"][name="add_qty"]').first().val(1);
                    return false
                }
                ajax.jsonRpc("/shop/cart/order", 'call',
                {
                    'product_id': product_id,
                    'add_qty': add_qty
                })
                .then(function (result)
                {
                    if(!result.status)
                    {
                        $form.find('input[type="text"][name="add_qty"]').first().val(temp);
                        $('.css_quantity').popover
                        ({
                            content:_t(result.msg),
                            title:_t("WARNING"),
                            placement:"top",
                            trigger:'focus',
                        });
                        $('.css_quantity').popover('show');
                        setTimeout(function() {$('.css_quantity').popover('dispose')},5000);
                    }
                    else
                    {
                        $('.css_quantity').popover('dispose');
                        temp = add_qty.toString();
                    }
                });
            });
            $(oe_website_sale).on('click', 'a.btn.btn-default.btn-xs', function(ev) {
                ev.preventDefault(ev);
                var self = this;
                var $form = $(this).closest('form');
                var $msg = $form.find('.fa-shopping-cart');
                var product_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val(), 10);
                ajax.jsonRpc("/shop/cart/order", 'call', {
                    'product_id': product_id,
                    'add_qty': 1,
                    'set_qty': 1
                })
                .then(function(result) {
                    ev.preventDefault();

                    if (!result.status) {
                        ev.preventDefault();
                        $(self).removeClass('a-submit');
                        $(self).popover({

                            content: _t(result.msg),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $(self).popover('show');
                        setTimeout(function() {
                            $(self).popover('dispose')
                        }, 1000);
                        $(self).removeClass('a-submit');

                    }
                });
            });


            $(oe_website_sale).on("click", ".oe_cart a.js_add_suggested_products", function () {
                var product_preorder_value = $('#product_preorder_value').data('product_preorder_value');
                if (product_preorder_value){
                    $('.js_add_suggested_products').removeClass('a-submit');
                    event.preventDefault(event);
                    window.location.href = "#";
                    $('.js_add_suggested_products').popover({
                        content: _t("Oops, you can not add Preorder Product with other product."),
                        title: _t("WARNING"),
                        placement: "top",
                        trigger: 'focus',
                    });
                    $('.js_add_suggested_products').popover('show');
                    setTimeout(function() {
                        $('#add_to_cart').popover('dispose')
                    }, 3000);
                }
                else {
                   $('#add_to_cart').popover('dispose');
                   $('.js_add_suggested_products').addClass('a-submit');
                }
                $(this).prev('input').val(1).trigger('change');

            });
        });
    });
});
