odoo.define('ki_export_import_access.export_import_option', function (require) {
"use strict";

var rpc = require('web.rpc');
const ActionMenus = require('web.ActionMenus');
var AbstractController = require('web.AbstractController');
const ImportMenu = require('base_import.ImportMenu');
const Registry = require('web.Registry');
var group = 'ki_export_import_access.group_hide_export_import'
rpc.query({
    "model": "res.users",
    "method": "has_group",
    "args": [group],
    "kwargs": {}
    }, {async: false}).then(function(output) {
    	ActionMenus.prototype._remove_import = function(actionItems) {
    		for (var i = 0; i < actionItems.length; i++) {
    			if (actionItems[i].description == 'Export') {
    				delete actionItems[i]
    			}
			}
    		return actionItems.flat()
    	}
    	if (output == false) {
    		ImportMenu.template = "new_import_menu_template";
    		ActionMenus.template = "new_action_menu_template"
    	}
    	else if (output == true) {
    		ImportMenu.template = "base_import.ImportMenu";
    		ActionMenus.template = "web.ActionMenus"
    	}
        AbstractController.include({
	        is_action_enabled: function (action) {
	            if (action == 'export_xlsx') {
	                if (output == false) {
	                    return false
	                }
	            }
	            return this._super(action)
	        },
	    });
    });
});
