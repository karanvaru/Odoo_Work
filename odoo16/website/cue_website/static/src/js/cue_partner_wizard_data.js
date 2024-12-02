odoo.define('cue_website.cue_partner_wizard_data', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
    var _t = core._t;
	var DynamicCuePartnerWizard = publicWidget.Widget.extend({
		selector: '.cue_partner_wizard_box',
		start: function() {
			var self = this;
			$('.thanks_partner_div').hide();
			let partner_city = self.el.querySelector('#partner_city');

            $('.partner_state').on('change', function(ev) {
                var partner_state = $('#partner_state').val();
                    self._rpc({
                    route: '/cue_wizard_partner_state/',
                    params: {
                        'partner_state': partner_state,
                    }
                    }).then(html => {
                        partner_city.innerHTML = ""
                        partner_city.innerHTML = html.message
                    })
            })

			$('.submit_partner_wizard_data').on('click', function(ev) {
                var name = $('#partner_fn').val();
                var phone = $('#partner_phone').val();
                var status = $('#partner_status').val();
                var city = $('#partner_city').val();
                var partner_state = $('#partner_state').val();
                var regex =/^[0-9]{10}$/;

                if(!name || !phone || !city ||(!regex.test(phone))){
                    self.displayNotification({
                        type: 'warning',
                        message: _t('Please Fill Proper Data.'),
                        sticky: false,
                    });
                }
                else{
                    self._rpc({
				        route: '/cue_partner_wizard_submit/',
				        params: {
				            'name': name,
				            'phone': phone,
				            'status': status,
				            'city': city,
							'state_id': partner_state
				        }
                    })
                    $('.partner_details').hide();
                    $('.thanks_partner_div').show();
                }
			})
		},
	});
	publicWidget.registry.DynamicCuePartnerWizard = DynamicCuePartnerWizard;
});





//odoo.define('cue_website.cue_partner_wizard_data', function(require) {
//	'use.strict';
//	var ajax = require('web.ajax');
//	var publicWidget = require('web.public.widget');
//	var core = require('web.core');
//    var _t = core._t;
//	var DynamicCuePartnerWizard = publicWidget.Widget.extend({
//		selector: '.cue_partner_wizard_box',
//		start: function() {
//			var self = this;
//			$('.thanks_partner_div').hide();
///*			let partner_city = self.el.querySelector('#partner_city');
//				self._rpc({
//					route: '/PartnerCityWizard/',
//					params: {}
//				}).then(html => {
//					partner_city.innerHTML = ""
//					partner_city.innerHTML = html.message
//				})
//*/			$('.submit_partner_wizard_data').on('click', function(ev) {
//                var name = $('#partner_fn').val();
//                var phone = $('#partner_phone').val();
//                var city = $('#partner_city').val();
//                var exist_partner = $('#exist_partner').val();
//                var regex =/^[0-9]{10}$/;
//
//                if(!name || !phone || !city || !exist_partner ||(!regex.test(phone))){
//                    self.displayNotification({
//                        type: 'warning',
//                        message: _t('Please Fill Proper Data.'),
//                        sticky: false,
//                    });
//                }
//                else{
//                    self._rpc({
//				        route: '/cue_partner_wizard_submit/',
//				        params: {
//				            'name': name,
//				            'phone': phone,
//				            'city': city,
//				            'exist_partner': exist_partner,
//				        }
//                    })
//
//                    $('.partner_details').hide();
//                    $('.thanks_partner_div').show();
//                }
//
////                $('.s_popup_close').on('click', function(ev) {
////                     location.replace(location.pathname);
////			    })
//			})
//			      $('.s_popup_close').on('click', function(ev) {
//                     location.replace(location.pathname);
//			    })
//
//		},
//	});
//	publicWidget.registry.DynamicCuePartnerWizard = DynamicCuePartnerWizard;
//});
