odoo.define('activities_todo.act_systray', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ActivityMenu = require('mail.systray.ActivityMenu');

    ActivityMenu.include({
        events: _.extend({}, ActivityMenu.prototype.events, {
            "click .activity_todo": "_onStartActivities",
        }),
        _onStartActivities: function(event) {
            // The method to open activities to-do interface
            var self = this;
            this._rpc({
                model: "mail.activity.todo",
                method: "start_todo",
                args: [],
                context: {},
            }).then(function (action_id) {
                self.do_action(action_id);
            });
        },


    });

    return ActivityMenu

});