odoo.define('cue_website.cue_wizard_data', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
    var _t = core._t;

	var DynamicCueWizard = publicWidget.Widget.extend({
		selector: '.cue_wizard_box',
		start: function() {
			var self = this;
			var city_selected;
			var search_data
			$('.thanks_div').hide();
			let user_city = self.el.querySelector('#user_city');

            $('.user_state').on('change', function(ev) {
                var user_state = $('#user_state').val();
                    self._rpc({
                    route: '/cue_wizard_user_state/',
                    params: {
                        'user_state': user_state,
                    }
                    }).then(html => {
						user_city.innerHTML = ""
						user_city.innerHTML = html.message
					})
            })
			$('.submit_wizard_data').on('click', function(ev) {
                var name = $('#fname').val();
                var phone = $('#phone').val();
                var status = $('#user_status').val();
                var city = $('#user_city').val();
                var user_state = $('#user_state').val();
                var regex =/^[0-9]{10}$/;

                if(!name || !phone || !status|| !city || (!regex.test(phone))){
                    self.displayNotification({
                        type: 'warning',
                        message: _t('Please Fill Proper Data.'),
                        sticky: false,
                    });
                }
                else{
                    self._rpc({
				        route: '/cue_wizard_submit/',
				        params: {
				            'name': name,
				            'phone': phone,
				            'status': status,
				            'city': city,
							'state_id': user_state
				        }
                    })
                    $('.contact_details').hide();
                    $('.thanks_div').show();
                }
			})
		},
	});
	publicWidget.registry.DynamicCueWizard = DynamicCueWizard;
});



//odoo.define('cue_website.cue_wizard_data', function(require) {
//	'use.strict';
//	var ajax = require('web.ajax');
//	var publicWidget = require('web.public.widget');
//	var core = require('web.core');
//    var _t = core._t;
//
//	var DynamicCueWizard = publicWidget.Widget.extend({
//		selector: '.cue_wizard_box',
//		start: function() {
//			var self = this;
//			var city_selected;
//			var search_data
//			$('.thanks_div').hide();
///*
//		    let user_city = self.el.querySelector('#user_city');
//				self._rpc({
//					route: '/UserCityWizard/',
//					params: {}
//				}).then(html => {
//					user_city.innerHTML = ""
//					user_city.innerHTML = html.message
//				})
//*/
//
//			$('.submit_wizard_data').on('click', function(ev) {
//                var name = $('#fname').val();
//                var phone = $('#phone').val();
//                var status = $('#user_status').val();
//                var city = $('#user_city').val();
//                var regex =/^[0-9]{10}$/;
//
//                if(!name || !phone || !status|| !city || (!regex.test(phone))){
//                    self.displayNotification({
//                        type: 'warning',
//                        message: _t('Please Fill Proper Data.'),
//                        sticky: false,
//                    });
//                }
//                else{
//                    self._rpc({
//				        route: '/cue_wizard_submit/',
//				        params: {
//				            'name': name,
//				            'phone': phone,
//				            'status': status,
//				            'city': city,
//				        }
//                    })
//                    $('.contact_details').hide();
//                    $('.thanks_div').show();
//                }
//			})
//			  $('.s_popup_close').on('click', function(ev) {
//                     location.replace(location.pathname);
//			    })
//		},
//	});
//	publicWidget.registry.DynamicCueWizard = DynamicCueWizard;
//
//});
