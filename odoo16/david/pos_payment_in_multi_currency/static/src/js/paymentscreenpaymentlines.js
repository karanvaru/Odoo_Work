/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_payment_in_multi_currency.pos_payment_in_multi_currency_screenPaymentLines', function (require) {
    "use strict";
    var PaymentScreenPaymentLines = require("point_of_sale.PaymentScreenPaymentLines");
    const Registries = require('point_of_sale.Registries');

    const posPaymentScreenPaymentLines = (PaymentScreenPaymentLines) => class extends PaymentScreenPaymentLines {
        formatLineAmount(paymentline) {
            var self = this;
            var current_order = self.env.pos.get_order();
            if (this.env.pos.config.enable_multi_currency && current_order.use_multi_currency && paymentline.is_multi_currency_payment) {
                var amt = current_order.get_other_currency_amount(paymentline);
                current_order.is_multi_currency_payment = paymentline.is_multi_currency_payment;
                return this.env.pos.format_currency_no_symbol(amt);
            } else {
                return this.env.pos.format_currency_no_symbol(paymentline.get_amount());
            }
        }
    };
    Registries.Component.extend(PaymentScreenPaymentLines, posPaymentScreenPaymentLines);
    return PaymentScreenPaymentLines;
});
