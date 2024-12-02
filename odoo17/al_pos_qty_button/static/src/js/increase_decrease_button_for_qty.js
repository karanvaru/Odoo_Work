/** @odoo-module */
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";


patch(Orderline.prototype, {
    onClickIncreaseQty() {
        const order = this.env.services.pos.get_order();
        const selectedLine = order.get_selected_orderline();
        const currentQuantity = selectedLine.get_quantity();
        selectedLine.set_quantity(currentQuantity + 1);
    },
    onClickDecreaseQty() {
        const order = this.env.services.pos.get_order();
        const selectedLine = order.get_selected_orderline();
        const currentQuantity = selectedLine.get_quantity();
        const new_qty = currentQuantity-1
        selectedLine.set_quantity(new_qty);
            if (new_qty == 0) {
                order._unlinkOrderline(selectedLine);
        }
    },
});
