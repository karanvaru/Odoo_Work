odoo.define('rdp_it_inherit_ev12_custom.BasicView', function (require) {
"use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            var model = self.controllerParams.modelName
            if (model === 'product.template' || model === 'product.product') {
                session.user_has_group('base.group_system').then(function(has_group) {
                    if(!has_group) {
                        self.controllerParams.activeActions['delete'] = 'False' in viewInfo.fields;
                    }
                });
            }
        },
    });
});