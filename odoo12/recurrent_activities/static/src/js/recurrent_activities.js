odoo.define('recurrent_activities.recurrent_activities', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ActivityMenu = require('mail.systray.ActivityMenu');

    ActivityMenu.include({
        events: _.extend({}, ActivityMenu.prototype.events, {
            "click .recurrent-activities": "_onRecurrentActivities",
        }),
        _onRecurrentActivities: function(event) {
            // The method to open view of recurrent activities
            var self = this;
            this._rpc({
                model: "recurrent.activity.template",
                method: "return_view_action",
                args: [],
                context: self.getSession().user_context,
            }).then(function (action_id) {
                self.do_action(action_id);
            });
        },


    });

    return ActivityMenu

});