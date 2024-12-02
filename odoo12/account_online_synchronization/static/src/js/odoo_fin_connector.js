odoo.define('account_online_synchronization.odoo_fin_connector', function(require) {
"use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');

    function OdooFinConnector (parent, action) {
        var id = action.id;
        var mode = action.params.mode || 'link';
        // Ensure that the proxyMode is valid
        var modeRegexp = /^[a-z0-9-_]+$/i;
        if (!modeRegexp.test(action.params.proxyMode)) { return; }
        var url = 'https://' + action.params.proxyMode + '.odoofin.com/proxy/v1/odoofin_link';
        
        ajax.loadJS(url)
        .then(function () {
            // Create and open the iframe
            var params = {
                data: action.params, 
                proxyMode: action.params.proxyMode, 
                onEvent: function(event, data){
                    switch(event) {
                        case 'close':
                            return;
                        case 'reload':
                            return parent.do_action({type: 'ir.actions.client', tag: 'reload'});
                        case 'notification':
                            parent.do_notify(data.title, data.message);
                            break;
                        case 'exchange_token':
                            parent._rpc({
                                model: 'account.online.link',
                                method: 'exchange_token',
                                args: [[id], data]
                            })
                            break;
                        case 'success':
                            mode = data.mode || mode;
                            return parent._rpc({
                                model: 'account.online.link',
                                method: 'success',
                                args: [[id], mode, data]
                            })
                            .then(function(action) {
                                parent.do_action(action)
                            });
                        default:
                            return;
                    }
                },
                onAddBank: function() {
                    // If the user doesn't find his bank.
                    return parent._rpc({
                        model: 'account.online.link',
                        method: 'create_new_bank_account_action',
                    })
                    .then(function(action) {
                        return parent.do_action(action, {replace_last_action: true});
                    });
                }
            }
            OdooFin.create(params);
            OdooFin.open();
            // This is needed in case iframe is opened from a modal, close the modal when opening the iframe
            if (parent.currentDialogController) {
                parent._closeDialog();
            }
        });
        return;
    }
    core.action_registry.add('odoo_fin_connector', OdooFinConnector);
});
