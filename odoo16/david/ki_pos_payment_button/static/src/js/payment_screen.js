odoo.define('ki_pos_payment_button.CustomButtonPaymentScreen', function(require) {
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
           setup() {
               super.setup();
               useListener('click', this.IsPrintDutyFreeButton);
           }
           IsPrintDutyFreeButton() {
            this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice());
            this.render(true);

              // click_invoice
/*              Gui.showPopup("ConfirmPopup", {
                      title: this.env._t('Title'),
                      body: this.env._t('Welcome to OWL(body of popup)'),
                  });
*/          }
      };
   Registries.Component.extend(PaymentScreen, CustomButtonPaymentScreen);
   return CustomButtonPaymentScreen;
});