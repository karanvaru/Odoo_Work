odoo.define('asterisk_calls_crm.systray', function (require) {
"use strict";

var CallsMenu = require('asterisk_calls.systray');

var CrmCallsMenu = CallsMenu.include({

    start: function () {
        this._updateButtonsHandlers();
        return this._super();
    },

    _updateButtonsHandlers: function() {
        this._super();
        var self = this;
        // Lead field
        this.$('tbody tr td:nth-child(7)').off().on('click', function(ev){
            var lead = $(ev.target).getAttributes().lead;
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: "crm.lead",
                res_id: parseInt(lead),
                views: [[false, 'form']],
                target: 'current',
                context: {},
            });
        });
    },

});

return CrmCallsMenu;

});
