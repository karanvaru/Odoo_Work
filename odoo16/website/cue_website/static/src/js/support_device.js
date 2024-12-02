odoo.define('cue_website.Support', function(require){
    'use.strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var DynamicSnippet =  publicWidget.Widget.extend({
        selector: '.supported_devices',
        start: function() {
            let supportdv = this.el.querySelector('#support_device_row');
            if (supportdv){
                supportdv.innerHTML = "<div>!!! No Device Found !!!</div>"
                this._rpc({
                    route: '/supportdevice/',
                    params:{}
                }).then(data=>{
                    let html = ``
                    data.forEach(data=>{
                    html += `<div class="col-lg-2 mb-4">
                                <div class="d-flex align-items-center">
                                    <div class="cubes">
                                        <div class="box">
                                            console.log("+++++++++++++++supporttttttt",data)
                                            <img class="img_class"  src="data:image/png;base64,${data.logo}"/>
                                            <p class="name_class"><b>${data.name}</b></p>
                                        </div>
                                    </div>
                                </div>
                            </div>`
                        })
                    supportdv.innerHTML = html
                })
            }
        },
});

    publicWidget.registry.DynamicSnippetWebiner = DynamicSnippet;
    return DynamicSnippet

});