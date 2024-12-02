///** @odoo-module **/

import Registries from 'point_of_sale.Registries';
import TicketScreen from 'point_of_sale.TicketScreen';
import {useListener} from "@web/core/utils/hooks";

class BookOrderPopup extends TicketScreen {
    setup() {
        super.setup();
        useListener('button-confirm', this._Confirm);
    }
    back() {
        this.showScreen('ProductScreen');
    }
    _Confirm(ev) {
        var self = this
        var data = ev.detail
        this.env.pos.add_new_order();
        this.env.pos.selectedOrder.booked_data = data
        this.showScreen('ProductScreen');
    }
}
BookOrderPopup.template = 'BookOrderPopup';
Registries.Component.add(BookOrderPopup);
