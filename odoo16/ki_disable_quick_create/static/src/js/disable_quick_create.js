odoo.define('ki_disable_quick_create.disable_quick_create', function (require) {
    "use strict";

    var FieldMany2One = require('web.relational_fields').FieldMany2One;

    FieldMany2One = FieldMany2One.include({
        init: function(parent, name, record, options) {
            var self = this;
            this._super(parent, name, record, options)
            this.getSession().user_has_group('ki_disable_quick_create.group_disable_quick_create').then(function(has_group) {
                if (self.field.relation == 'product.product') {
                    self.nodeOptions.no_quick_create = has_group;
                    self.nodeOptions.no_create_edit = has_group;
                }
            });
        },
        _onInputFocusout: function () {
            var self = this;
            var _super = this._super.bind(this);
            this.getSession().user_has_group('ki_disable_quick_create.group_disable_quick_create').then(function(has_group) {
                if (has_group == false) {
                    return _super();
                }
            });
        },
    });
});

