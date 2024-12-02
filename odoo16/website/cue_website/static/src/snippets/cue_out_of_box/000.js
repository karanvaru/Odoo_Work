odoo.define('cue_website.MarqueBox', function (require) {
'use strict';

const dom = require('web.dom');
var publicWidget = require('web.public.widget');
// var PortalSidebar = require('portal.PortalSidebar');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
const Widget = require('web.Widget');

    publicWidget.registry.MarqueBox = publicWidget.Widget.extend({
        selector: '.__marque_box',
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            self.brand_ids = [];
            this._render();
            return def;
        },
        willStart: function () {
            var self = this;
            var def = this._rpc({
				route: '/prepare_out_of_box_list/',
				params: {}
            }).then(function (result) {
                if(!result) {
                    return;
                }
                /*result = _.pluck(result, 'id');
                const items = result
                const n = 3
                const result_data = [[], [], []]
                const x= Math.ceil(items.length / 3)
                for (let line = 0; line < n; line++) {
                  for (let i = 0; i < x; i++) {
                    const value = items[i + line * x]
                    if (!value) continue
                    result_data[line].push(value)
                  }
                }
                if(result_data[0].length < 7) {
                    let length = 7 - result_data[0].length;
                    let dynamic_array = Array.from({length: length}, () => result[Math.floor(Math.random() * result.length)]);
                    result_data[0] = result_data[0].concat(dynamic_array);
                }
                if(result_data[1].length < 7) {
                    let length = 7 - result_data[1].length;
                    let dynamic_array = Array.from({length: length}, () => result[Math.floor(Math.random() * result.length)]);
                    result_data[1] = result_data[1].concat(dynamic_array);
                }
                if(result_data[2].length < 7) {
                    let length = 7 - result_data[2].length;
                    let dynamic_array = Array.from({length: length}, () => result[Math.floor(Math.random() * result.length)]);
                    result_data[2] = result_data[2].concat(dynamic_array);
                }*/
                self.brand_ids = result['list'];
                self.brands = result['brands'];
            });
            return Promise.all([this._super.apply(this, arguments), def]);
        },
        _render: function () {
            var marque_box = QWeb.render('marque_box', {widget: this});
            this.$el.html(marque_box);
        },
    });
});
