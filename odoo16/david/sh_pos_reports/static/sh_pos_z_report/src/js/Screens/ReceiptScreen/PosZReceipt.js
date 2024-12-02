odoo.define("sh_pos_z_report.PosZReceipt", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    var field_utils = require('web.field_utils');

  class PosZReceipt extends PosComponent {
        setup() {
            super.setup();
        }
        getDate(date) {
            return field_utils.format.datetime(moment(new Date()), {}, {timezone: false});
        }
    }
    PosZReceipt.template = "PosZReceipt";
    Registries.Component.add(PosZReceipt);

    return PosZReceipt
});
