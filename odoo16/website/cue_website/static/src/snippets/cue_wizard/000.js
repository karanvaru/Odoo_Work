odoo.define('cue_website.s_popup', function (require) {
'use strict';

	const publicWidget = require('web.public.widget');

	publicWidget.registry.popup.include({
		/**
		 * @override
		 */
		_bindPopup: function () {
			if(this.$target.hasClass('__not_bind')) {
				return;
			}else {
			    this._super.apply(this, arguments);
			}
		},
	});

});