odoo.define('cue_website.cue_partner_location', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var DynamicSnippetLocation = publicWidget.Widget.extend({
		selector: '.cue_partner_location',
		start: function() {
			var self = this;
			var city_selected;
			var search_data
			let dropdown_state = self.el.querySelector('#dropdown_state');
			let dropdown_city = self.el.querySelector('#input_id');
			let main_div_search = self.el.querySelector('#main_div_search');
			if (dropdown_state) {
				self._rpc({
					route: '/partnerlocation/',
					params: {}
				}).then(html => {
					//dropdown_state.innerHTML = ""
					dropdown_state.innerHTML = html.message
					$(dropdown_state).trigger("change");
				})


				$('#dropdown_state').on('change', function(ev) {
					var state_id = $(this).val();

					self._rpc({
						route: '/partnerlocationcity/',
						params: {
							'city_state': state_id
						}
					}).then(html2 => {
						dropdown_city.innerHTML = ""
						dropdown_city.innerHTML = html2.message

					})
				})
				if (main_div_search) {
					this._rpc({
						route: '/ResPartnerInheritList/',
						params: {}

					}).then(html => {
						main_div_search.innerHTML = ""
						main_div_search.innerHTML = html.message
					})
				}

				$('#search_button').on('click', function(ev) {
					var city_selected = $("#input_id option:selected").val();
					var state = $("#dropdown_state option:selected").val();

					var search_data = city_selected.trim()

					self._rpc({
						route: '/ResPartnerInherit/',
						params: {
							"city_select": search_data,
							"state_id": state
						}
					}).then(html => {
						main_div_search.innerHTML = ""
						main_div_search.innerHTML = html.message
					})
				})
			}

		},
	});
	publicWidget.registry.DynamicSnippetLocation = DynamicSnippetLocation;

});
