odoo.define('ki_duty_free_pos.PaymentScreenStatus', function (require) {
  "use strict";

  var PaymentScreenStatus = require("point_of_sale.PaymentScreenStatus");

  var field_utils = require('web.field_utils');
  const Registries = require('point_of_sale.Registries');

  var utils = require('web.utils');
  var round_di = utils.round_decimals;
  const posPaymentScreenStatusUSD = (PaymentScreenStatus) => class extends PaymentScreenStatus {

        get USDText() {
			var order_amt = this.props.order.get_total_with_tax()
			var currency_id = this.env.pos.currency.id
			if (this.env.pos.config.usd_currency_id){
		        var currency_id = this.env.pos.config.usd_currency_id[0];
			}
            var amt = this.env.pos.currency_by_id[currency_id].rate * order_amt
            var order_amt = field_utils.format.float(round_di(amt, 2), { digits: [69, 2] });
//       		return this.formating(order_amt, currency_id)
       		return order_amt

        }
}
  Registries.Component.extend(PaymentScreenStatus, posPaymentScreenStatusUSD);
  return PaymentScreenStatus;
});

