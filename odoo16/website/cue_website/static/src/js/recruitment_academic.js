odoo.define('cue_website.recruitment_academic', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');

	var Dynamicrecruitment = publicWidget.Widget.extend({
		selector: '.cue_recruitment_forms',
		start: function() {
		var self = this
		let academics_list = self.el.querySelector('#academics_list');
		if (academics_list) {
		    self._rpc({
		    	route: '/RecruitmentAcademicdata/',
			    params: {}
				}).then(html => {
					academics_list.innerHTML = ""
					academics_list.innerHTML = html.message
					academics_list.required = true
			    })
		    }
		},
	});
	publicWidget.registry.Dynamicrecruitment = Dynamicrecruitment;
});
