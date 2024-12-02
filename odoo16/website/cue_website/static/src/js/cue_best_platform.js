odoo.define('cue_website.cue_best_platform', function(require){
    'use.strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    var DynamicplatformSnippet =  publicWidget.Widget.extend({
        selector: '.cue_best_platform',
        read_events: {
			'click .platform_image': '_onCallToAction',
		},
        start: function() {
            var self  = this;
            let platform_device = this.el.querySelector('#platform_js');
            if(platform_device){
                self._rpc({
                    route: '/platform_category/',
                    params:{}
                }).then(html=>{
                    platform_device.innerHTML = html.message
                    $('.platform_image:first').trigger('click');
                })
}
        },
         async _onCallToAction(ev) {
			 var category_id = $(ev.currentTarget).attr('data-id');
			 let platform_category_image = this.el.querySelector('#platform_category_image');
			 if(platform_category_image){
                 this._rpc({
                     route: '/platform_category_images/',
                     params:{'categ_id': category_id}
                    }).then(html=>{
                         // platform_category_image.innerHTML = ""
                          platform_category_image.innerHTML = html.message
                    })
             }
	     },






});

    publicWidget.registry.DynamicplatformSnippet = DynamicplatformSnippet;

});

