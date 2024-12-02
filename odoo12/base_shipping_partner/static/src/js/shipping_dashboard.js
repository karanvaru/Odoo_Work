odoo.define('base_shipping_partner.base_shipping_partner', function (require) {
    "use strict";

    var core = require('web.core');
    var KanbanRecord = require('web.KanbanRecord');
    var _t = core._t;

    KanbanRecord.include({

        _render: function () {
            var res = this._super.apply(this, arguments);
            return res;
        },

    });

});
