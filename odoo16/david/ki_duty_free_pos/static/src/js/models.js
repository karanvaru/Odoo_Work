/** @odoo-module **/
/*
 * This file is used to add some fields to order class for some reference.
 */
import Registries from 'point_of_sale.Registries';
import {Order} from 'point_of_sale.models'

const BookedOrder = (Order) => class BookedOrder extends Order {
    constructor(obj, options) {
        super(...arguments);
        if (options.json) {
            this.is_booked = true;
            this.to_duty_free = options.json.booked_data || undefined;
	        this.to_invoice     = false;

        }
    }
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.is_booked = json.is_booked;
        this.booked_data = json.booked_data
    }
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.booked_data = this.booked_data;
        json.is_booked = this.is_booked;
        return json;
    }

    set_to_duty_free(to_duty_free) {
        this.assert_editable();
        this.to_duty_free = to_duty_free;
    }
    is_to_duty_free(){
        return this.to_duty_free;
    }


}
Registries.Model.extend(Order, BookedOrder);
