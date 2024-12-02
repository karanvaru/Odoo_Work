/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_payment_in_multi_currency.pos_payment_in_multi_currency_screen_status', function (require) {
  "use strict";
  var PaymentScreenStatus = require("point_of_sale.PaymentScreenStatus");
  var field_utils = require('web.field_utils');
  const Registries = require('point_of_sale.Registries');
  var utils = require('web.utils');
  var round_di = utils.round_decimals;

  const posPaymentScreenStatus = (PaymentScreenStatus) => class extends PaymentScreenStatus {
    formating(amount, currency_id) {
      if (currency_id) {
        var currency = this.env.pos.currency_by_id[currency_id];
      }
      else {
        var currency = this.env.pos.currency;
      }
      if (currency.position === 'after') {
        return amount + ' ' + (currency.symbol || '');
      } else {
        return (currency.symbol || '') + ' ' + amount;
      }
    }
    format_currency_n_symbol(amount, precisson) {
      if (typeof amount === 'number') {
        var decimals = 2;
        amount = round_di(amount, decimals).toFixed(decimals);
        amount = field_utils.format.float(round_di(amount, decimals), {
          digits: [69, decimals],
        });
      }
      return amount;

    }
    get changeTextmc() {
      if (this.env.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var amt = this.format_currency_n_symbol(this.props.order.get_change_mc(this.props.order.get_change(), this.props.order.selected_paymentline), 0.0001);
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        return this.formating(amt, currency_id)
      } else {
        return this.env.pos.format_currency(this.props.order.get_change());
      }
    }
    get totalDueTextmc() {
      if (this.env.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        var due = this.props.order.get_change_mc(this.props.order.get_total_with_tax() + this.props.order.get_rounding_applied(), this.props.order.selected_paymentline)
        var amt = this.format_currency_n_symbol(
          due > 0 ? due : 0, 0.0001);
        return this.formating(amt, currency_id)
      } else {
        return this.env.pos.format_currency(
          this.props.order.get_total_with_tax() + this.props.order.get_rounding_applied()
        );
      }
    }
    get remainingTextmc() {
      if (this.env.pos.config.enable_multi_currency && this.props.order.use_multi_currency) {
        var currency_id = this.props.order.selected_paymentline.other_currency_id;
        var rem = this.props.order.get_change_mc(this.props.order.get_due(), this.props.order.selected_paymentline)
        var amt = this.format_currency_n_symbol(
          rem > 0 ? rem : 0, 0.0001)
        return this.formating(amt, currency_id)
      } else {
        return this.env.pos.format_currency(
          this.props.order.get_due() > 0 ? this.props.order.get_due() : 0
        );
      }
    }
    get convamount() {
      return this.env.pos.format_currency_no_symbol(this.props.order.selected_paymentline.get_amount());
    }
  };
  Registries.Component.extend(PaymentScreenStatus, posPaymentScreenStatus);

  return PaymentScreenStatus;
});
