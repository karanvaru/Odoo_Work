console.log("++++++++++++++++++1111111")

odoo.define('cue_website.cue_tech_space', function(require){
    'use.strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    var DynamicProductSnippet =  publicWidget.Widget.extend({
        selector: '.template_cue_tech_specs',
        start: function() {
            console.log("+++++++++++++++++++")
            var self  = this;
            let cue_product = this.el.querySelector('.cue_product');

            if(cue_product){
                self._rpc({
                    route: '/cue_product_search/',
                    params:{}
                }).then(html=>{
                    cue_product.innerHTML = html.message
                })
}
        },
});

    publicWidget.registry.DynamicProductSnippet = DynamicProductSnippet;

});
