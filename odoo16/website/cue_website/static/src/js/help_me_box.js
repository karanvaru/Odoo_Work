odoo.define('cue_website.help_me_box.js', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	publicWidget.registry.DynamichelpmeSnippet = publicWidget.Widget.extend({
		selector: '.cue_helpme',
		start: function() {
			var self = this;
			$('#help_me_onclick').on('click', function(ev) {
				let helpme = self.el.querySelector('#helpme_click');
				self._rpc({
					route: '/product_tag_custom/',
					params: {}
				}).then(html => {
					helpme.innerHTML = ""
					helpme.innerHTML = html.message
				})
			})
			
			$('.tag_button_next').on('click', function(ev) {
				console.log("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
			})

		},
	});
});

