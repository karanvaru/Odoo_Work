odoo.define('printnode_base.ReportActionManager', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var crash_manager = require('web.crash_manager');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');

    var _t = core._t;

    ActionManager.include({

        _printOrDownload: function (url, download_only){
            var self = this;
            var type = url.split('/')[2];
            if (type === "pdf" || type === "text") {
                type = 'qweb-' + type;
            }
            var def_obj = $.Deferred();
            if (!download_only && session.printnode_enabled) {
                framework.blockUI();
                ajax.post('/report/check', {
                    data: JSON.stringify([url, type])
                }).then(
                    function(res) {
                        def_obj.resolve((res === 'true'));
                    },
                    function() {
                        def_obj.resolve(false);
                    }
                );
            } else {
                def_obj.resolve(false);
            }
            return $.when(def_obj).then(function (res) {
                if (res) {
                    return ajax.post('/report/print', {
                        data: JSON.stringify([url, type])
                    }).then(
                        function(print_result) {
                            framework.unblockUI();
                            try { // Case of a serialized Odoo Exception: It is Json Parsable
                                print_result = JSON.parse(print_result);
                                if (print_result.notify) {
                                    self.do_notify(
                                            print_result.title,
                                            print_result.message,
                                            false
                                        );
                                }
                            } catch (e) { // Arbitrary uncaught python side exception
                                var err
                                var doc = new DOMParser().parseFromString(print_result, 'text/html');
                                var nodes = doc.body.children.length === 0 ? doc.body.childNodes : doc.body.children;
                                try { // Case of a serialized Odoo Exception: It is Json Parsable
                                    var node = nodes[1] || nodes[0];
                                    err = JSON.parse(node.textContent);
                                } catch (e) { // Arbitrary uncaught python side exception
                                    err = {
                                        message: nodes.length > 1 ? nodes[1].textContent : '',
                                        data: {
                                            name: 'Server Error',
                                            title: nodes.length > 0 ? nodes[0].textContent : '',
                                        }
                                    };
                                }
                                crash_manager.rpc_error.apply(crash_manager, err);
                            }
                        },
                        function() {
                            framework.unblockUI();
                            self.do_notify(
                                _t('Printing error!'),
                                _t('Something went wrong. Report is not printed'),
                                false
                            );
                        }
                    );
                } else {
                    framework.unblockUI();
                    return self._downloadReport(url);
                }
            });
        },

        _triggerDownload: function (action, options, type){
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            if (type === "pdf" || type === "text" || (type === "py3o" && action["py3o_filetype"] === "pdf")) {
                return this._printOrDownload(reportUrls[type], options.download ? true : false).then(function () {
                    if (action.close_on_report_download) {
                        var closeAction = { type: 'ir.actions.act_window_close' };
                        return self.doAction(closeAction, _.pick(options, 'on_close'));
                    } else {
                        return options.on_close();
                    }
                });
            }
            return this._super.apply(this, arguments);
        },

    });
});
