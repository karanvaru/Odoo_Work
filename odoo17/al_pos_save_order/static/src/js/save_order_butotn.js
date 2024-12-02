/**@odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class SaveOrderButton extends Component {
    static template = "point_of_sale.SaveOrderButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        if (this['pos'].selectedOrder.orderlines.length > 0) {
            this.pos.add_new_order();
            this.pos.showScreen("ProductScreen");
        } else {
            this.popup.add(ErrorPopup, {
                title: _t('Add Product'),
                body: _t('Add Product Before Save Order'),
            });
        }
    }
}

ProductScreen.addControlButton({
    component: SaveOrderButton,
    position: ["after", "TableGuestsButton"],
});