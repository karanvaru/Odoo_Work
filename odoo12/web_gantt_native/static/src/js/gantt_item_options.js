odoo.define('web_gantt_native.ItemOptions', function (require) {
"use strict";

var Widget = require('web.Widget');
var Model = require('web.AbstractModel');
var framework = require('web.framework');

var GanttListOptionsItem = Widget.extend({
    template: "GanttList.options",

        custom_events: {
        'item_order' : 'order_action',
    },

    init: function(parent) {
        this.parent = parent;
        this._super.apply(this, arguments);
    },

    start: function () {
        // var _widget =  this.parent.gantt_timeline_header_widget;
        // var el_widget = _widget.$el;

        if (this.parent.ItemsSorted){

            // var div_manual = $('<div class="text-left task-gantt-item-sort-manual"/>');
            // div_manual.text("Manual Sort");
            // this.$el.append(div_manual);

        } else if (this.parent.state.orderedBy && this.parent.state.orderedBy.length){


            var div_ = $('<div class="text-left task-gantt-item-sort-name"/>');
            div_.text(this.parent.fields[this.parent.state.orderedBy[0].name].string);


            var  div_typer = $('<div class="fa fa-sort-amount-desc task-gantt-item-sort-pointer" aria-hidden="false"></div>');

            if (this.parent.state.orderedBy[0].asc){
                div_typer = $('<div class="fa fa-sort-amount-asc task-gantt-item-sort-pointer" aria-hidden="false"></div>');
            }

            div_.append(div_typer);
            this.$el.append(div_);

        }
    },


    renderElement: function () {
        this._super();

        this.$el.data('parent', this);
        this.$el.on('click', this.proxy('on_global_click'));

    },

    on_global_click: function (ev) {

        if (!ev.isTrigger) { //human detect

            if ($(ev.target).hasClass("task-gantt-item-sort-pointer" )) {

                this.trigger_up('item_order', {
                    orderedBy: this.parent.state.orderedBy,
                });
            }
        }
    },

    order_action: function(event) {

        var self = this.__parentedParent;
        var parent = this.parent;
        var orderedBy = event.data.orderedBy;


        if (orderedBy.length){

            if (orderedBy[0].asc){
                orderedBy[0].asc = false
            }else{

                orderedBy[0].asc = true
            }

            self.trigger_up('gantt_refresh_after_change' )

        }
    }


});



return {

    OptionsItem : GanttListOptionsItem

};


});