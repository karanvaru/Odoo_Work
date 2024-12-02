odoo.define('web_gantt_native.ItemInfo', function (require) {
"use strict";


var core = require('web.core');

var dialogs = require('web.view_dialogs');

var Widget = require('web.Widget');
var Model = require('web.AbstractModel');

var framework = require('web.framework');

var _lt = core._lt;
var _t = core._t;



var GanttListInfo = Widget.extend({
    template: "GanttList.action",

    init: function(parent, options) {

        this._super(parent);
        this.parent = parent;
        this.items_sorted = options.items_sorted;
        this.export_wizard = options.export_wizard;
        this.main_group_id_name = options.main_group_id_name;
        this.action_menu = options.action_menu;
        this.tree_view = options.tree_view;
        this.$zTree = parent.widget_ztree.$zTree;


    },

    start: function() {

        var self = this;
        var $zTree = this.$zTree;

        var nodes = $zTree.getNodes();

         _.each(nodes, function (node) {

             var childNodes = $zTree.transformToArray(node);

             _.each(childNodes, function (child) {

                var id = child["id"];



                var item_info = $('<div class="item-info"/>');

                if (id !== undefined) {
                    item_info.prop('id', "item-info-" + id);
                    item_info.prop('data-id', id);
                    item_info.prop('allowRowHover', true);
                }

                var duration = child['duration'];
                var duration_units = undefined;
                var subtask_count = child['subtask_count'];


                if (duration){

                    var duration_scale = child['duration_scale'];

                    if (duration_scale) {

                        duration_units =  duration_scale.split(",");

                    }
                    // Array of strings to define which units are used to display the duration (if needed).
                    // Can be one, or a combination of any, of the following:
                    // ['y', 'mo', 'w', 'd', 'h', 'm', 's', 'ms']
                    //
                    // humanizeDuration(3600000, { units: ['h'] })       // '1 hour'
                    // humanizeDuration(3600000, { units: ['m'] })       // '60 minutes'
                    // humanizeDuration(3600000, { units: ['d', 'h'] })  // '1 hour'

                    var duration_humanize = humanizeDuration(duration*1000, { round: true });

                    if (duration_units){
                        duration_humanize = humanizeDuration(duration*1000,{ units: duration_units, round: true });
                    }


                    if (child['isParent']){
                        item_info.append('<div class="task-gantt-item-info task-gantt-items-subtask" style="float: right;">'+duration_humanize+'</div>');
                    }
                    else{
                        item_info.append('<div class="task-gantt-item-info" style="float: right;">'+duration_humanize+'</div>');
                    }

                }


                // if (child["is_group"]) {
                //     item_info.addClass("task-gantt-items-group");
                //     item_info.css({'background-color':   "beige"});
                // }

                var fold = child["fold"];
                if (self.tree_view) {
                    if (fold) {
                        item_info.css({'display': 'none'});
                    }
                }

                self.$el.append(item_info);



             });


         });



    },


});

return GanttListInfo;

});





// odoo.define('web_gantt_native.ItemInfo', function (require) {
// "use strict";
//
//
// var core = require('web.core');
//
// var dialogs = require('web.view_dialogs');
//
// var Widget = require('web.Widget');
// var Model = require('web.AbstractModel');
//
// var framework = require('web.framework');
//
// var _lt = core._lt;
// var _t = core._t;
//
//
//
// var GanttListInfo = Widget.extend({
//     template: "GanttList.info",
//
//     init: function(parent, record, options) {
//
//         this._super(parent);
//         this.record = record;
//         this.items_sorted = options.items_sorted;
//         this.export_wizard = options.export_wizard;
//         this.main_group_id_name = options.main_group_id_name;
//         this.action_menu = options.action_menu;
//         this.tree_view = options.tree_view;
//
//
//     },
//
//     start: function() {
//
//         var self = this;
//
//         var id = self.record["id"];
//
//         if (id !== undefined) {
//             self.$el.prop('id', "item-info-" + id);
//             self.$el.prop('data-id', id);
//             self.$el.prop('allowRowHover', true);
//         }
//
//         var duration = self.record['duration'];
//         var duration_units = undefined;
//         var subtask_count = self.record['subtask_count'];
//
//         if (duration){
//
//             var duration_scale = self.record['duration_scale'];
//
//             if (duration_scale) {
//
//                 duration_units =  duration_scale.split(",");
//
//             }
//             // Array of strings to define which units are used to display the duration (if needed).
//             // Can be one, or a combination of any, of the following:
//             // ['y', 'mo', 'w', 'd', 'h', 'm', 's', 'ms']
//             //
//             // humanizeDuration(3600000, { units: ['h'] })       // '1 hour'
//             // humanizeDuration(3600000, { units: ['m'] })       // '60 minutes'
//             // humanizeDuration(3600000, { units: ['d', 'h'] })  // '1 hour'
//
//             var duration_humanize = humanizeDuration(duration*1000, { round: true });
//
//             if (duration_units){
//                 duration_humanize = humanizeDuration(duration*1000,{ units: duration_units, round: true });
//             }
//
//
//             if (subtask_count){
//                 this.$el.append('<div class="task-gantt-item-info task-gantt-items-subtask" style="float: right;">'+duration_humanize+'</div>');
//             }
//             else{
//                 this.$el.append('<div class="task-gantt-item-info" style="float: right;">'+duration_humanize+'</div>');
//             }
//
//         }
//
//
//         if (self.record["is_group"]) {
//             this.$el.addClass("task-gantt-items-group");
//             this.$el.css({'background-color':   "beige"});
//         }
//
//         var fold = self.record['fold'];
//
//         if (self.tree_view) {
//             if (fold) {
//                 this.$el.css({'display': 'none'});
//             }
//         }
//
//
//
//
//
//     },
//
//
//
//
// });
//
// return GanttListInfo;
//
// });