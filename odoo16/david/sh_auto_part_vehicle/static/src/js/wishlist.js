odoo.define('sh_auto_part_vehicle.wishlist_js', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
require('website_sale_wishlist.wishlist');

publicWidget.registry.ProductWishlist.include({

    /**
     * @private
     */
     _addNewProducts: function ($el) {
        var self = this;
        var productID = $el.data('product-product-id');
        if ($el.hasClass('o_add_wishlist_dyn')) {
            productID = $el.parent().find('.product_id').val();
            // for ecomate custom code
            productID = $el.closest('#product_details').find('.js_product').find('.product_id').val();         
            if (!productID) { // case List View Variants
                productID = $el.parent().find('input:checked').first().val();
            }
            // for ecomate custom code

            if (!productID) { // case List View Variants
                productID = $el.parent().find('input:checked').first().val();
            }
            productID = parseInt(productID, 10);
        }
		var otherBtn = $el.data('other-btn');
		
        var $form = $el.closest('form');
        var templateId = $form.find('.product_template_id').val();
        // when adding from /shop instead of the product page, need another selector
        if (!templateId) {
            templateId = $el.data('product-template-id');
        }
		
        $el.prop("disabled", true).addClass('disabled');
        var productReady = this.selectOrCreateProduct(
            $el.closest('form'),
            productID,
            templateId,
            false
        );
        productReady.then(function (productId) {
            productId = parseInt(productId, 10);
            
            if (productId && !_.contains(self.wishlistProductIDs, productId)) {
                return self._rpc({
                    route: '/shop/wishlist/add',
                    params: {
                        product_id: productId,
                    },
                }).then(function () {
                    var $navButton = $('header .o_wsale_my_wish').first();
                    // ecomate
                    // in order to make wishlist counter proper when adding from snippet.
                    var wishDef = $.get('/shop/wishlist', {
                        count: 1,
                    }).then(function (res) {
                        self.wishlistProductIDs = JSON.parse(res);
                        self._updateWishlistView();
						
						//Shop
						if($el.closest('form') && !otherBtn){
							wSaleUtils.animateClone($navButton, $el.closest('form'), 25, 40);
						}
						//detail page						
						if ($el.parents('section#product_detail').find('.row #o-carousel-product .carousel-item.h-100.active').length && !otherBtn) {
							wSaleUtils.animateClone($("header .o_wsale_my_wish"), $el.parents('section#product_detail').find('.row #o-carousel-product .carousel-item.h-100.active'), 20, 10);
	                    }
						
						//detail alternate table
						else if ($el.parents('.main').find('.varinat_image_main').length && otherBtn) {
							wSaleUtils.animateClone($("header .o_wsale_my_wish"), $el.parents('.main').find('.varinat_image_main'), 20, 10);
	                    }
                    });
						
                }).guardedCatch(function () {
                    $el.prop("disabled", false).removeClass('disabled');
                });
            }
        }).guardedCatch(function () {
            $el.prop("disabled", false).removeClass('disabled');
        });
    },

});
});