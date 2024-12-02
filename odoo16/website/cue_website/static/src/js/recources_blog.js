odoo.define('cue_website.resources_blog', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	const dom = require('web.dom');

	var DynamicrecourcesSnippet1 = publicWidget.Widget.extend({
		selector: '.cue_columns',
		read_events: {
			//'click .blog_explore': '_onCallToAction',
		},
		start: function() {
			let resources_blog = this.el.querySelector('.resources_blog');
			if (resources_blog) {
				//resources_blog.innerHTML = "<div>!!! Blog Category Found !!!</div>"
				this._rpc({
					route: '/resources_blog_categories/',
					params: {}
				}).then(html => {
					resources_blog.innerHTML = html.message
		          //  $('.blog_explore:first').trigger('click');

				})
			}
		},
	/*	async _onCallToAction(ev) {
			var blog_id = $(ev.currentTarget).attr('data-id');
			let blog_detail_page = this.el.querySelector('.blog_detail_pages');
			if (blog_detail_page) {
				this._rpc({
					route: '/resources_blog_posts/',
					params: { 'blog_id': blog_id }
				})
					.then(html => {
						blog_detail_page.innerHTML = html.message
					})
			}
		},*/
	});


	publicWidget.registry.ParalaxSlider = publicWidget.Widget.extend({
		selector: '.oe_img_bg',
		start: function() {
			var self = this;
			let backgroundUrl = self.$el[0].style.backgroundImage.slice(4, -1);
			self.$el.css('--backgroundUrl', "url("+backgroundUrl+")");
		},
	});

	publicWidget.registry.BlogContent = publicWidget.Widget.extend({
		selector: '.cue_blog_content',
		start: function() {
			let width = $( window ).width();
			if(width < 992) {
				let wraper = this.$('.s_table_of_content_main > section:first-child');
				var $content = this.$('.s_table_of_content_navbar a');

				var selectList = document.createElement("select");
				selectList.id = "__custom_blog_select";
				wraper.prepend(selectList);

				var option = document.createElement("option");
				option.value = '';
				option.text = 'Jump to a section';
				selectList.appendChild(option);


				$content.each(function() {
					// Every Time Create new option
					option = document.createElement("option");
					option.value = $(this).attr('href');
					option.text = $(this).html();
					selectList.appendChild(option);
				});

				$(selectList).change(function(ev){
					let url = $(ev.currentTarget).val();
					dom.scrollTo(url, {
					    duration: 500,
					    extraOffset: 0,
					});
				});
			}
		},
	});

	publicWidget.registry.DynamicrecourcesSnippet1 = DynamicrecourcesSnippet1;
	return DynamicrecourcesSnippet1

});



