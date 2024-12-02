odoo.define('printnode_base.Sidebar', function (require) {
"use strict";

var core = require('web.core');
var Sidebar = require('web.Sidebar');
var Context = require('web.Context');
var pyUtils = require('web.py_utils');
var session = require('web.session');

var _t = core._t;

Sidebar.include({

    init: function (parent, options) {
        this._super.apply(this, arguments);
        if (session.printnode_enabled) {
            var ind = _.findIndex(this.sections, {name: 'print'});
            ind = ind >= 0 ? ind + 1 : 0;
            this.sections.splice(ind, 0, {
                name: 'download',
                label: _t('Download')
            });
            this.items['download'] = this.items['print'];
        }
    },

    _onDownloadItemActionClicked: function (item) {
        var self = this;
        this.trigger_up('sidebar_data_asked', {
            callback: function (env) {
                self.env = env;
                var activeIdsContext = {
                    active_id: env.activeIds[0],
                    active_ids: env.activeIds,
                    active_model: env.model,
                };
                if (env.domain) {
                    activeIdsContext.active_domain = env.domain;
                }

                var context = pyUtils.eval('context', new Context(env.context, activeIdsContext));
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: item.action.id,
                        context: context,
                    },
                }).then(function (result) {
                    result.context = new Context(
                        result.context || {}, activeIdsContext)
                            .set_eval_context(context);
                    result.flags = result.flags || {};
                    result.flags.new_window = true;
                    self.do_action(result, {
                        on_close: function () {
                            self.trigger_up('reload');
                        },
                        download: true
                    });
                });
            }
        });
    },

    _onDropdownClicked: function (event) {
        var section = $(event.currentTarget).data('section');
        var index = $(event.currentTarget).data('index');
        var item = this.items[section][index];
        if (section == 'download') {
            if (item.callback) {
                item.callback.apply(this, [item]);
            } else if (item.action) {
                this._onDownloadItemActionClicked(item);
            } else if (item.url) {
                return true;
            }
        } else {
            return this._super.apply(this, arguments);
        }
        event.preventDefault();
    },

});

return Sidebar;

});
