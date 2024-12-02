odoo.define('ki_duty_free_pos.CustomButtonPaymentScreen', function(require) {
'use strict';

const { Gui } = require('point_of_sale.Gui');
const PosComponent = require('point_of_sale.PosComponent');
const { identifyError } = require('point_of_sale.utils');
const ProductScreen = require('point_of_sale.ProductScreen');
const { useListener } = require("@web/core/utils/hooks");
const Registries = require('point_of_sale.Registries');
const PaymentScreen = require('point_of_sale.PaymentScreen');
const Chrome = require('point_of_sale.Chrome');
const CustomButtonPaymentScreen = (PaymentScreen) =>
    class extends PaymentScreen {
        async validateOrder(isForceValidate) {
            if (this.currentOrder.is_to_duty_free() === true) {
                let syncResult
                var self = this;
                syncResult = await this.env.pos.push_single_order(this.currentOrder);


                if (syncResult.length) {
                    await this.env.legacyActionManager.do_action('ki_duty_free_pos.pos_duty_free_pdf_report', {
                        additional_context: {
                            active_ids: [syncResult[0].id],
                        },
                    });
                }
            }
        return super.validateOrder(...arguments);
        }

        toggleIsTopos() {
	            this.currentOrder.set_to_duty_free(!this.currentOrder.is_to_duty_free());
            this.render(true);
        }

        get currentOrder() {
           return this.env.pos.get_order();
        }
    };
    Registries.Component.extend(PaymentScreen, CustomButtonPaymentScreen);
    return PaymentScreen;
});
