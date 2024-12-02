/** @odoo-module */
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";


const itemRemoveOrder = {
    setup() {
        super.setup();
        this.numberBuffer = useService("number_buffer");
    },
    ClearButtonFun() {
        this.numberBuffer.sendKey("Backspace");
        this.numberBuffer.sendKey("Backspace");
    }
};

patch(Orderline.prototype, itemRemoveOrder);