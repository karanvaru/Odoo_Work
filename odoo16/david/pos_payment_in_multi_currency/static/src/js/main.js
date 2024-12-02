/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_payment_in_multi_currency.pos_payment_in_multi_currency', function (require) {
    "use strict";
    var { PosGlobalState, Order, Payment } = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var field_utils = require('web.field_utils');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const PosCurrencyGlobalState = (PosGlobalState) => class PosCurrencyGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            var self = this;
            rpc.query({
                model: 'res.currency',
                method: 'get_currency',
                args: [1]
            }).then(function (currencies) {
                self.currencies = false
                if (self.config.enable_multi_currency && self.config.multi_currency_ids) {
                    self.currencies = []
                    self.currency_by_id = {}
                    _.each(currencies, function (currencie) {
                        if (self.config.multi_currency_ids.includes(currencie.id)) {
                            if (self.config.currency_id[0] != currencie.id) {
                                self.currencies.push(currencie)
                                self.currency_by_id[currencie.id] = currencie
                            }
                        }
                        if (self.config.currency_id[0] == currencie.id) {
                            self.currencies.push(currencie)
                            self.currency_by_id[currencie.id] = currencie
                        }
                        if (currencie.rate == 1) {
                            self.base_currency = currencie
                        }
                    });
                }
            });
        }
        async getClosePosInfo() {
            const closingData = await this.env.services.rpc({
                model: 'pos.session',
                method: 'get_closing_control_data',
                args: [[this.pos_session.id]]
            });
            const ordersDetails = closingData.orders_details;
            const paymentsAmount = closingData.payments_amount;
            const payLaterAmount = closingData.pay_later_amount;
            const openingNotes = closingData.opening_notes;
            const defaultCashDetails = closingData.default_cash_details;
            const otherPaymentMethods = closingData.other_payment_methods;
            const isManager = closingData.is_manager;
            const amountAuthorizedDiff = closingData.amount_authorized_diff;
            const cashControl = this.config.cash_control;
            const currency_amount = closingData.currency_amount;
            // component state and refs definition
            const state = { notes: '', acceptClosing: false, payments: {} };
            if (cashControl) {
                state.payments[defaultCashDetails.id] = { counted: 0, difference: -defaultCashDetails.amount, number: 0 };
            }
            if (otherPaymentMethods.length > 0) {
                otherPaymentMethods.forEach(pm => {
                    if (pm.type === 'bank') {
                        state.payments[pm.id] = { counted: this.round_decimals_currency(pm.amount), difference: 0, number: pm.number }
                    }
                })
            }
            return {
                ordersDetails, paymentsAmount, payLaterAmount, openingNotes, defaultCashDetails, otherPaymentMethods,
                isManager, amountAuthorizedDiff, state, cashControl, currency_amount
            }
        }
    }
    Registries.Model.extend(PosGlobalState, PosCurrencyGlobalState);

    const PosOrder = (Order) => class PosOrder extends Order {
        constructor(obj, option) {
            super(...arguments);
            var self = this;
            self.use_multi_currency = self.use_multi_currency || false;
            self.multi_payment_lines = self.multi_payment_lines || {};
            self.is_multi_currency_payment = self.is_multi_currency_payment || false;
            if(option.json){
                self.use_multi_currency = option.json.is_multi_currency_payment || false;
                self.multi_payment_lines = option.json.multi_payment_lines || [];
                self.is_multi_currency_payment = option.json.is_multi_currency_payment || false;
                self.reprint = true
            }
        }
        init_from_JSON(json) {
            var self = this;
            super.init_from_JSON(...arguments);
            this.use_multi_currency = json.use_multi_currency || false;
            this.multi_payment_lines = json.multi_payment_lines || {};
            this.is_multi_currency_payment = json.is_multi_currency_payment || false;
            this.reprint = json.reprint || false;
        }
        export_as_JSON() {
            var self = this;
            var loaded = super.export_as_JSON();
            if (self.use_multi_currency){
                loaded.use_multi_currency = self.use_multi_currency;
                loaded.multi_payment_lines = self.multi_payment_lines;
                loaded.is_multi_currency_payment = self.is_multi_currency_payment;
                loaded.reprint = self.reprint;
            }
            return loaded
        }
        export_for_printing(){
            var self = this;
            var receipt = super.export_for_printing();
            receipt.multi_payment_lines = self.get_paymentlines();
            receipt.is_multi_currency_payment = self.is_multi_currency_payment;
            if(self.reprint){
                receipt.is_multi_currency_payment = self.is_multi_currency_payment;
                receipt.multi_payment_lines = self.multi_payment_lines;
                receipt.multi_payment_lines.forEach(function(line){
                    if(line.is_change){
                        receipt.is_other_currency_change = true
                        receipt.change_other_currency_id = line.other_currency_id
                        receipt.change_other_currency_amount = line.other_currency_amount
                    }
                })
            } else {
                if (self.is_multi_currency_payment && self.has_single_multi_currency_payment){
                    receipt.is_other_currency_change = true
                    var currency =  self.pos.currency_by_id[self.change_single_other_currency_id]
                    var amt = (receipt.change * currency.rate) / self.pos.currency.rate;
                    receipt.change_other_currency_id = currency.id
                    receipt.change_other_currency_amount = amt
                }
            }
            return receipt;
        }
        get_other_currency_amount(line) {
            var self = this;
            if (line && line.currency_id) {
                var amt = (self.pos.currency_by_id[line.currency_id].rate * line.otc_amount) / self.pos.currency.rate
                line.other_currency_amount = (self.pos.currency_by_id[line.currency_id].rate * line.get_amount()) / self.pos.currency.rate;
                var res = field_utils.format.float(round_di(amt, 4), { digits: [69, 4] });
                return res;
            } else {
                line.other_currency_amount = 0.0;
                return 0.0;
            }
        }
        get_change_mc(change, paymentline) {
            if (this.use_multi_currency && paymentline && paymentline.other_currency_id) {
                var amt = (this.pos.currency_by_id[paymentline.currency_id].rate * change) / this.pos.currency.rate
                amt = parseFloat(round_di(amt, 4));
                return amt
            } else {
                return Math.max(0, change);
            }
        }
        get_change(paymentline) {
            var self = this;
            if(this.paymentlines.length == 1){
                var lines  = this.paymentlines;
                for (var i = 0; i < lines.length; i++) {
                    if(lines[i].is_multi_currency_payment && lines[i].other_currency_id){
                        self.has_single_multi_currency_payment = true
                        self.change_single_other_currency_id = lines[i].other_currency_id
                    }
                }
            }
            return super.get_change(paymentline)
        }
    }
    Registries.Model.extend(Order, PosOrder);

    const PosPayment = (Payment) => class PosPayment extends Payment {
        constructor(obj, option) {
            super(...arguments);
            var self = this;
            self.other_currency_id = false
            self.other_currency_rate = false
            self.other_currency_amount = 0.0
            self.otc_amount = 0.0
            self.currency_id = self.currency_id || false;
            self.other_currency_id = self.currency_id || false;
            self.other_currency_rate = self.other_currency_rate || false;
            self.other_currency_amount = self.other_currency_amount || 0.0;
            self.is_multi_currency_payment = self.is_multi_currency_payment || false;
            self.otc_amount = self.otc_amount || 0;
        }
        init_from_JSON(json) {
            var self = this;
            super.init_from_JSON(...arguments);
            self.currency_id = json.currency_id || false;
            self.other_currency_id = self.currency_id || false;
            self.other_currency_rate = json.other_currency_rate || false;
            self.other_currency_amount = self.other_currency_amount || 0.0;
            self.is_multi_currency_payment = json.is_multi_currency_payment || false;
            self.otc_amount = json.otc_amount || 0.0;
        }
        export_as_JSON() {
            var self = this;
            var loaded = super.export_as_JSON();
            if (self.currency_id) {
                loaded.currency_id = self.currency_id;
            }
            if (self.other_currency_id) {
                loaded.other_currency_id = self.currency_id;
            }
            if (self.other_currency_rate) {
                loaded.other_currency_rate = self.other_currency_rate;
            }
            if (self.other_currency_amount) {
                loaded.other_currency_amount = self.other_currency_amount;
            }
            if (self.is_multi_currency_payment) {
                loaded.is_multi_currency_payment = self.is_multi_currency_payment
            }
            if (self.otc_amount) {
                loaded.otc_amount = self.otc_amount
            }
            return loaded;
        }
    }
    Registries.Model.extend(Payment, PosPayment);
});
