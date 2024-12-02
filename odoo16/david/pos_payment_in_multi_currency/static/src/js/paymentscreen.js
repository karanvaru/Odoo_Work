/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_payment_in_multi_currency.pos_payment_in_multi_currency_screen', function (require) {
  "use strict";
  var PaymentScreen = require("point_of_sale.PaymentScreen");
  const NumberBuffer = require('point_of_sale.NumberBuffer');
  const Registries = require('point_of_sale.Registries');

  const posPaymentScreen = (PaymentScreen) => class extends PaymentScreen {

    _updateSelectedPaymentline() {
      if (this.paymentLines.every((line) => line.paid)) {
        this.currentOrder.add_paymentline(this.env.pos.payment_methods[0]);
      }
      if (!this.selectedPaymentLine) return; // do nothing if no selected payment line
      // disable changing amount on paymentlines with running or done payments on a payment terminal
      if (
        this.payment_interface &&
        !['pending', 'retry'].includes(this.selectedPaymentLine.get_payment_status())
      ) {
        return;
      }
      if (NumberBuffer.get() === null) {
        this.deletePaymentLine({ detail: { cid: this.selectedPaymentLine.cid } });
      } else {
        if (this.selectedPaymentLine.is_multi_currency_payment) {
          var amt = (NumberBuffer.getFloat() * this.env.pos.currency.rate) / this.selectedPaymentLine.other_currency_rate;
          this.selectedPaymentLine.otc_amount = amt;
          this.selectedPaymentLine.set_amount(amt);
        } else {
          this.selectedPaymentLine.set_amount(NumberBuffer.getFloat());
        }
      }
    }

    clickmulticurrency() {
      var self = this;
      var order = self.env.pos.get_order();
      if (order && order.use_multi_currency) {
        order.use_multi_currency = false
        $('.wk-multi-currency').removeClass('highlight');
        if (order && order.get_paymentlines() && order.get_paymentlines().length) {
          _.each(order.get_paymentlines(), function (paymentline) {
            paymentline.other_currency_id = false
            paymentline.other_currency_rate = 0
            paymentline.other_currency_amount = 0
            paymentline.is_multi_currency_payment = false
            if (self.env.pos.config.currency_id && self.env.pos.config.currency_id[0]) {
              paymentline.currency_id = self.env.pos.config.currency_id[0]
            }
          })
          self.trigger('change');
        }
      } else {
        order.use_multi_currency = true
        $('.wk-multi-currency').addClass('highlight');
      }
      order.export_as_JSON();
      order.save_to_db()
    }

    async addNewPaymentLine({ detail: paymentMethod }) {
      var self = this;
      var current_order = self.env.pos.get_order();
      if (this.currentOrder.electronic_payment_in_progress()) {
        this.showPopup('ErrorPopup', {
          title: this.env._t('Error'),
          body: this.env._t('There is already an electronic payment in progress.'),
        });
        return false;
      } else {
        var currency_id = self.env.pos.config.currency_id[0];
        if (this.env.pos.config.enable_multi_currency && current_order.use_multi_currency) {
          var popup = await this.showPopup('MultiCurrencyPopup', { 'payment_id': paymentMethod })
          if (popup.confirmed) {
            currency_id = popup.payload
          }
        }
        var paymentline = this.currentOrder.add_paymentline(paymentMethod);
        if (current_order.selected_paymentline) {
          current_order.selected_paymentline.currency_id = parseInt(currency_id);
          var currency_data = self.env.pos.currency_by_id[currency_id];
          current_order.selected_paymentline.other_currency_id = parseInt(currency_id);
          if(currency_data)
            current_order.selected_paymentline.other_currency_rate = currency_data.rate
          current_order.selected_paymentline.is_multi_currency_payment = true
          current_order.selected_paymentline.otc_amount = current_order.selected_paymentline.get_amount()
        }
        NumberBuffer.reset();
        this.payment_interface = paymentMethod.payment_terminal;
        if (this.payment_interface) {
          this.currentOrder.selected_paymentline.set_payment_status('pending');
        }
        return true;
      }
    }
  };
  Registries.Component.extend(PaymentScreen, posPaymentScreen);
  return PaymentScreen;
});
