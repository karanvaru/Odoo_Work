//odoo.define('ki_purchase_line_search.listview', function (require) {
//    "use strict";
//
//    var list_render = require('web.ListRenderer');
////    list_render = list_render.include({
////
////        events: _.extend({}, list_render.prototype.events, {
////            'input .order_line_filter': '_order_line_filter',
////        }),
////
////        init: function (parent, state, params) {
////            this.model = state.model
////            this._super(parent, state, params);
////
////        },
////
////        _order_line_filter: function () {
////            var input = document.getElementById("order_line_input").value;
////            var table = document.getElementsByClassName("o_list_table table table-sm table-hover table-striped")
////            var filter = input.toUpperCase();
////            if (input) {
////                for (var i = 0; i < table[0].rows.length; i++) {
////                    if (table[0].rows[i].className.indexOf("o_data_row") > -1) {
////                        var txtValue = table[0].rows[i].textContent || table[0].rows[i].innerText;
////                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
////
////                            table[0].rows[i].hidden = false
////                        }
////                        else {
////
////                            table[0].rows[i].hidden = true
////                        }
////                    }
////                }
////            }
////            else {
////                for (var i = 0; i < table[0].rows.length; i++) {
////
////                    table[0].rows[i].hidden = false
////                }
////            }
////        },
////
////        _renderView: function () {
////            var current_model = this.model
////	        return this._super.apply(this, arguments).then(() => {
////	            if (current_model == "purchase.order.line") {
////	            	var $div_row = $('<div class="row mt8 mb8">')
////	                $div_row.append($('<div style="text-align:right;" class="col-sm-6">').append($('<label style="margin-top:5px;font-weight: bold;">Search :</label>')));
////	                $div_row.append($('<div class="col-sm-6">').append($('<input class="order_line_filter" type="text" id="order_line_input" placeholder="Search by Purchase lines..." style="width: 50%;">')));
////	            	this.$el.prepend($div_row)
////	            }
////	        });
////	    },
////    });
//});
//
