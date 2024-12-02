odoo.define('ki_pos_extend.sale_person_add_button', function(require) {
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const ButtonScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const ajax = require('web.ajax');

    class SalePersonButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        get SalesPersonName() {
            const order = this.env.pos.get_order();

            return "Duty Free Details"
        }
        async onClick() {

            const selectionuser = this.env.pos.getClosePosInfo();
            this.showPopup(
                'SelectionPopupUser',
                {
                }
            )
//            .then(({ confirmed, payload: selectedPaymentMethod }) => {
//                if (confirmed) {
//                    const order = this.env.pos.get_order();
//                    order.ed_no = selectedPaymentMethod;
//                    order.departure_date = selectedPaymentMethod;
//                    order.ship_flight = selectedPaymentMethod;
//                }
//            });
        }
    }
    SalePersonButton.template = 'SalePersonButton';
    ButtonScreen.addControlButton({
        component: SalePersonButton,
        condition: function() {
            return this;
        },
        position: ['before', 'SetPricelistButton'],
    });

    Registries.Component.add(SalePersonButton);
    return SalePersonButton;
});