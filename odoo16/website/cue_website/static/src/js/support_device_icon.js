odoo.define('cue_website.support_device_icon', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');

	var DynamiciconSnippet1 = publicWidget.Widget.extend({
		selector: '.cue_supported_devices',
		read_events: {
			'click .icon_class': '_onCallToAction',
			'change .__category_selection': '_onCallToActionSelection',
		},

		start: function() {
			let categ_icon = this.el.querySelector('#icon_box');
			// this.DataHtml =
			categ_icon.innerHTML = this.DataHtml;
			// if (categ_icon) {
			// 	categ_icon.innerHTML = "<div>!!! No Device Found !!!</div>"
			// 	this._rpc({
			// 		route: '/categorydevice/',
			// 		params: {}
			// 	}).then(html => {
			// 		categ_icon.innerHTML = ""
			// 		categ_icon.innerHTML = html.message
			// 	})
			// }
		},


		/**
		 * @override
		 */
		willStart: function () {
			var self = this;
			let width = $( window ).width();
			let is_mobile = false;
			if(width <= 991) {
				is_mobile = true;
			}
		    var def = this._rpc({
					route: '/categorydevice/',
					params: {is_mobile: is_mobile},
			}).then(html => {
				self.DataHtml = ""
				self.DataHtml = html.message
			})
		    return Promise.all([this._super.apply(this, arguments), def]);
		},

		async _onCallToAction(ev) {
			var id = $(ev.currentTarget).attr('data-id');
			$(ev.currentTarget).parents('.image_box').find('.col').removeClass('active');
			$(ev.currentTarget).parent().addClass('active');
			const searchDomain = [['id', '=', id]];

			this._rpc({
					route: '/categorybrands/',
					params: {'categ_id': id},

				//model: 'product.category',
			//	method: 'search_read',
			//	fields: ['brand_ids'],
			//	args: [searchDomain],
			}).then(res_ids => {
				var brands = $('.brands');
				if (id != 0) {
					var brand_ids = []
					if (res_ids.length != 0) {
						brand_ids = res_ids[0].brand_ids
					}
					for (let i = 0; i < brands.length; i++) {
						var data_id = $(brands[i]).attr('data-id');
						var brand_exist = $.inArray(parseInt(data_id), brand_ids);
						if (id == 0) {
							$(brands[i]).show();
						}
						else if (brand_exist > -1) {
							$(brands[i]).show();
						} else {
							$(brands[i]).hide();
						}

					}
				} else {
					for (let i = 0; i < brands.length; i++) {
						$(brands[i]).show();

					}
				}

			})
		},

		async _onCallToActionSelection(ev) {
			var id = $(ev.currentTarget).val();
			$(ev.currentTarget).parents('.image_box').find('.col').removeClass('active');
			$(ev.currentTarget).parent().addClass('active');
			const searchDomain = [['id', '=', id]];

			this._rpc({
					route: '/categorybrands/',
					params: {'categ_id': id},

				//model: 'product.category',
			//	method: 'search_read',
			//	fields: ['brand_ids'],
			//	args: [searchDomain],
			}).then(res_ids => {
				var brands = $('.brands');
				if (id != 0) {
					var brand_ids = []
					if (res_ids.length != 0) {
						brand_ids = res_ids[0].brand_ids
					}
					for (let i = 0; i < brands.length; i++) {
						var data_id = $(brands[i]).attr('data-id');
						var brand_exist = $.inArray(parseInt(data_id), brand_ids);
						if (id == 0) {
							$(brands[i]).show();
						}
						else if (brand_exist > -1) {
							$(brands[i]).show();
						} else {
							$(brands[i]).hide();
						}

					}
				} else {
					for (let i = 0; i < brands.length; i++) {
						$(brands[i]).show();

					}
				}

			})
		},
	});

	publicWidget.registry.DynamiciconSnippet1 = DynamiciconSnippet1;
	return DynamiciconSnippet1

});


