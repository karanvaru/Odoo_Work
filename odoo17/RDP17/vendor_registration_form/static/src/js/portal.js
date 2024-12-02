odoo.define('vendor_registration_form.portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var utils = require('web.utils');

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
    selector: '.o_membership_details',
    events: {
        'change select[name="country_id"]': '_onVendorCountryChange',
        'change input#profile_img': '_onVendorImage',
		'change input.vendor_product_category': '_onVendorProductCategory',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        this.$state = this.$('select[name="state_id"]');
        this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        this._adaptAddressForm();
        this._onVendorImage()
        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _adaptAddressForm: function () {
        var $country = this.$('select[name="country_id"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
        this.$state.parent().toggle(nb >= 1);
    },

    /**
     * @private
     */
    _onVendorCountryChange: function () {
        this._adaptAddressForm();
    },

    /**
     * @private
     */
    _onVendorImage: function (ev) {
        const file = document.querySelector('input[type=file]').files[0];
        const preview = document.querySelector('img[id="slide-image"]');
        const reader = new FileReader();
        reader.addEventListener("load", function () {
            // convert image file to base64 string
            preview.src = reader.result;
        }, false);

        if (file) {
            reader.readAsDataURL(file);
        } else {
            preview.src = '/base/static/img/avatar_grey.png';
        }
    },

	/**
	* @private
	*/
	_onVendorProductCategory: function(){
		var VendorProductCategory = [];
		$.each($("input[class='vendor_product_category']:checked"), function(){
			VendorProductCategory.push($(this).val());
		});
		$("#vendor_product_category").val(VendorProductCategory)
	},

});
});