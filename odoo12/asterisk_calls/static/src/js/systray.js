odoo.define('asterisk_calls.systray', function (require) {
"use strict";

var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var core = require('web.core');
var QWeb = core.qweb;
var ajax = require('web.ajax');

var CallsMenu = Widget.extend({
    name: 'calls_menu',
    template:'asterisk_calls.systray',
    events: {
        'show.bs.dropdown': '_onCallsMenuShow',
    },

    start: function () {
        this._$activitiesPreview = this.$('.o_calls_systray_dropdown');
        this._updateCallsPreview();
        return this._super();
    },

    _getCallsData: function () {
        var self = this;

        return self._rpc({
            model: 'asterisk_calls.channel',
            method: 'search_read',
            args: [[]],
            kwargs: {},
        }).then(function (data) {
            self._channels = data;
        });
    },

    _updateCallsPreview: function () {
        var self = this;
        return self._getCallsData().then(function (){
            self._$activitiesPreview.html(QWeb.render('asterisk_calls.systray_items', {
                widget: self,
                channels: _.values(self._channels) || []
            }));
            self._updateButtonsHandlers();
        });
    },

    _updateButtonsHandlers: function() {
        var self = this;
        // Partner field
        this.$('tbody tr td:nth-child(6)').off().on('click', function(ev){
            var partner = $(ev.target).getAttributes().partner;
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: "res.partner",
                res_id: parseInt(partner),
                views: [[false, 'form']],
                target: 'current',
                context: {},
            });
        });
        // Buttons
        _.each(this.$('.channel_action_button'), function(btn) {
            $(btn).off().on('click', function(ev){
                ev.stopPropagation();                
                var target = $(ev.target);
                var method = (target.parent('button')[0] || target[0]).attributes.name.value;
                var channel = $(ev.target).parents('tr').getAttributes().channel;
                self._make_rpc_request(method, parseInt(channel));
            });
        });
    },

    _make_rpc_request: function(method, channel_id) {
        var self = this;
        return this._rpc({
            model: 'asterisk_calls.channel',
            method: method,
            args: [[channel_id]],
            kwargs: {},
        }).then(function (data) {
            setTimeout(function() {self._updateCallsPreview()}, 500);
        });
    },

    _onCallsActionClick: function (ev) {
        ev.stopPropagation();
        this.$('.dropdown-toggle').dropdown('toggle');
    },

    _onCallsMenuShow: function () {
         this._updateCallsPreview();
    },
});

ajax.rpc('/web/dataset/call_kw/asterisk_common.settings', {
        "model": "asterisk_common.settings",
        "method": "check_widget_enabled",
        "args": [],
        "kwargs": {},
    }).then(function (is_enabled) {
        if (is_enabled) {
            SystrayMenu.Items.push(CallsMenu);
        }
    })

return CallsMenu;

});
