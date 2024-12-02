/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_loyalty_management.pos_multi_currency_PopupWidget', function (require) {
  'use strict';
  const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
  const Registries = require('point_of_sale.Registries');
  var utils = require('web.utils');
  var round_di = utils.round_decimals;
  var field_utils = require('web.field_utils');
  var HeaderButton = require('point_of_sale.HeaderButton');

  var PosResHeaderButton = HeaderButton => class extends HeaderButton {}
  Registries.Component.extend(HeaderButton, PosResHeaderButton);

  class MultiCurrencyPopup extends AbstractAwaitablePopup {
    amountCheck() {
      var currency_id = $('.wk-selected-currency').val()
      if (currency_id) {
        var currency = this.env.pos.currency_by_id[currency_id]
        if (currency) {
          $(".wk-exchange-rate").html(currency.rate)
          var rate = (currency.rate * 1) / this.env.pos.currency_by_id[this.env.pos.config.currency_id[0]].rate
          rate = field_utils.format.float(round_di(rate, 5), { digits: [69, 5] })
          $(".wk-currency-amount").html(rate)
          $(".wk-currency-name").html(currency.name + "(" + currency.symbol + ")")
        }
      }
    }
    setup() {
      super.setup();
      var self = this;
      $(document).ready(function () {
        self.amountCheck();
        $(".wk-selected-currency").change(function () {
          self.amountCheck();
        })
      })
    }
    getPayload() {
      return $('.wk-selected-currency').val();
    }
  };
  MultiCurrencyPopup.template = 'MultiCurrencyPopup';
  MultiCurrencyPopup.defaultProps = { title: 'Select the Product', body: '', list: [] };
  Registries.Component.add(MultiCurrencyPopup);
  return MultiCurrencyPopup;
});
