odoo.define("sh_pos_cash_in_out.screen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ReceiptScreen = require("point_of_sale.ReceiptScreen");

    const SHReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            orderDone() {
                this.env.pos.is_z_report_receipt = false;
                super.orderDone()
            }
        };
    Registries.Component.extend(ReceiptScreen, SHReceiptScreen);

});
