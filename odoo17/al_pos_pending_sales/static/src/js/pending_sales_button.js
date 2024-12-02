/**@odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PendingSalesButton extends Component {
    static template = "point_of_sale.PendingSalesButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        if (this.isTicketScreenShown) {
            this.pos.closeScreen();
        }
        else {
            if (this._shouldLoadOrders()) {
                try {
                    this.pos.setLoadingOrderState(true);
                    const message = await this.pos._syncAllOrdersFromServer();
                    if (message) {
                        this.notification.add(message, 5000);
                    }
                } finally {
                    this.pos.setLoadingOrderState(false);
                    this.pos.showScreen("TicketScreen");
                }
            }
            else {
                this.pos.showScreen("TicketScreen");
            }
        }
    }
    _shouldLoadOrders() {
        return this.pos.config.trusted_config_ids.length > 0;
    }
}

ProductScreen.addControlButton({
    component: PendingSalesButton,
    position: ["after", "TableGuestsButton"],
});