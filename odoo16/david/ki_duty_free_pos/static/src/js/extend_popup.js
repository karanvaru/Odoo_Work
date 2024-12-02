odoo.define('ki_duty_free_pos.extend_popup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const rpc = require('web.rpc');

    const { useState } = owl;

    class SelectionPopupUser extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.order = this.env.pos.get_order()
            const partner = this.env.pos.get_order().get_partner();
			this.props.ed_no = partner.customer_passport_number

        }
        async onConfirm() {
        var ed_no = $("#ed_no").val();
        var ship_flight = $("#ship_flight").val();
        var departure_date = $("#departure_date").val();
//        var third_schedule = $("#third_schedule").val();
        var staying_at = $("#staying_at").val();
        var data = {
            'ed_no':ed_no,
            'ship_flight':ship_flight,
            'departure_date':departure_date,
//            'third_schedule':third_schedule,
            'staying_at':staying_at,
        }

        this.env.pos.selectedOrder.booked_data = data
        this.cancel();
        }
    }
    SelectionPopupUser.template = 'SelectionPopupUser';
    SelectionPopupUser.defaultProps = {
        cancelText: _lt('Cancel'),
        body: '',
        list: [],
        confirmKey: false,
    };
    Registries.Component.add(SelectionPopupUser);
    return SelectionPopupUser;
});
