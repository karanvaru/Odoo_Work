odoo.define('sh_auto_part_vehicle.website_sale', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
    var wSaleUtils = require("website_sale.utils");
    require('website_sale.website_sale');
    publicWidget.registry.WebsiteSale.include({
        read_events: {
            "click .sh_js_add_cart": "_onClickAddDirectCart",
        },


 		/**
	     * Add product to cart and reload the carousel.
	     * @private
	     * @param {Event} ev
	     */
	    _onClickAddDirectCart: function (ev) {
	        var self = this;
			var $btn = $(ev.currentTarget);
			var productID = $btn.attr("product-product-id");
			var product_id =parseInt(productID)
	        this._rpc({
	            route: "/shop/cart/update_json",
	            params: {
	                product_id: product_id,
	                add_qty: 1
	            },
	        }).then(function (data) {
	            var $navButton = $('header .o_wsale_my_cart').first();
				$(".my_cart_quantity").text(data.cart_quantity);
				var $img = $btn.parents(".main").find('.varinat_image_main');
                if ($img){
                    wSaleUtils.animateClone($(".o_wsale_my_cart"), $img, 20, 10);
                }
	            //var fetch = self._fetchData();
	            //var animation = wSaleUtils.animateClone($navButton, $(ev.currentTarget).parents('.card'), 25, 40);
	            /*Promise.all([fetch, animation]).then(function (values) {
	                wSaleUtils.updateCartNavBar(data);
	                if (self.add2cartRerender) {
	                     self._render();
	                }
	            });*/
	        });
	    },
        
    });
});
