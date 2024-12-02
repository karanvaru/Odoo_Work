odoo.define('point_of_sale.OrderNoteButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');


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
//                    order.agent_id = selectedPaymentMethod;
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

//    class OrderNoteButton extends PosComponent {
//        setup() {
//            super.setup();
//            useListener('click', this.onClick);
//        }
//
//        async onClick() {
//            const currentPosOrder = this.env.pos.get_order()
//            if (!currentPosOrder) return;
//            const {confirmed, payload: inputNote} = await this.showPopup('CustomTextAreaPopup', {
//                startingValue: currentPosOrder.ed_no,
//                title: this.env._t('ED No'),
//            });
//
//            if (confirmed) {
//                currentPosOrder.addOrderNote(inputNote);
//            }
//        }
//    }
//
//    OrderNoteButton.template = 'OrderNoteButton';
//
//    ProductScreen.addControlButton({
//        component: OrderNoteButton,
//    });
//
//    Registries.Component.add(OrderNoteButton);
//
//    return OrderNoteButton;
//});
