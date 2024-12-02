/** @odoo-modules */

import {Order, Orderline, PosGlobalState} from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';


const OrderInherit = (Order) => class OrderInherit extends Order {


    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.ed_no = this.ed_no
//        json.ship_flight = this.ship_flight
        return json;
    }

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.ed_no = json.ed_no;
//        this.ship_flight = json.ship_flight;
    }

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.ed_no = this.ed_no;
//        result.ship_flight = this.ship_flight;
        return result;
    }

    addOrderNote(ed_no,ship_flight) {
        this.ed_no = ed_no;
//        this.ship_flight = ship_flight;
    }
}

Registries.Model.extend(Order, OrderInherit);