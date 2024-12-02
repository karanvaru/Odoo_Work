odoo.define('cue_website.support_device_product', function(require){
    'use.strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');





    var DynamicdeviceSnippet =  publicWidget.Widget.extend({
        selector: '.cue_supported_box',
        start: function() {
            let supportdevice = this.el.querySelector('#support_device_id');
                $('.icon_class').on('click', function (ev){
					console.log("dddddddddddddddddddddddddddd",ev)

            if (supportdevice){
                supportdevice.innerHTML = "<div>!!! No Device Found !!!</div>"
                this._rpc({
                    route: '/supportdevices/',
                    params:{}
                }).then(data=>{
                    let html = ``
                    data.forEach(data=>{
                    html += `<div class="col-lg-2 mb-4">
                                <div class="d-flex align-items-center">
                                    <div class="cubes">
                                        <div class="box">
                                            <img class="img_class"  src="data:image/png;base64,${data.logo}"/>
                                            <p class="name_class"><b>${data.name}</b></p>
                                        </div>
                                    </div>
                                </div>
                            </div>`
                        })
					console.log("html ---------",html)
                    supportdevice.innerHTML = html
                    })
            }
                })

        },
});



    publicWidget.registry.DynamicdeviceSnippet = DynamicdeviceSnippet;
    return DynamicdeviceSnippet

    });
