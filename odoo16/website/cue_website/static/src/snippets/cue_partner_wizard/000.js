odoo.define('cue_website.s_partner_popup', function (require) {
'use strict';

	const publicWidget = require('web.public.widget');

	publicWidget.registry.popup.include({
		/**
		 * @override
		 */
        read_events: {
			'click .s_popup_close': '_onCallToAction',
		},

		_bindPopup: function () {
			if(this.$target.hasClass('__not_bind')) {
				return;
			}else {
			    this._super.apply(this, arguments);
			}
		},
         async _onCallToAction(ev) {
             location.replace(location.pathname);
		}
	});

});