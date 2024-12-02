odoo.define('bi_pos_dynamic_taxes.point_of_sale', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var field_utils = require('web.field_utils');

    const PosDynamicTaxesPosGlobalState = (PosGlobalState) => class PosDynamicTaxesPosGlobalState extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.taxes = loadedData['account.tax'];
            this.bi_taxes_data = [];
            for(var taxes of this.taxes){
                for(var bi_taxes of this.config.taxes_ids){
                    if(taxes.id == bi_taxes){
                        this.bi_taxes_data.push(taxes);
                    }
                }
            }
            await this.loadTaxesTypeId();
        }
        loadTaxesTypeId(){
            this.bi_taxes_by_id = {};
            for(let type of this.bi_taxes_data){
                this.bi_taxes_by_id[type.id] = type;
            }
        }
    }
    Registries.Model.extend(PosGlobalState, PosDynamicTaxesPosGlobalState);

    const PosTaxOrderline = (Orderline) => class PosTaxOrderline extends Orderline {
        constructor(obj, options) {
            super(...arguments);
            this.all_tax = this.all_tax || 0.0;
            this.tax_string = this.tax_string || '';
            this.tax_id_include_base = this.tax_id_include_base || [];
        }
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.all_tax = json.all_tax || 0.0;
            this.tax_string = json.tax_ids_after_fiscal_position || "";
            this.tax_id_include_base = json.tax_id_include_base || this.tax_ids;
        }
       
        set_all_tax(all_tax) {
            this.all_tax = all_tax;
        }
        get_all_tax() {
            return this.all_tax;
        }
        set_tax_string(tax_string) {
            this.tax_string = tax_string;
        }
        get_tax_string() {
            return this.tax_string;
        }
        set_tax_id_include_base(tax_id_include_base) {
            this.tax_id_include_base = tax_id_include_base;
        }
        get_tax_id_include_base() {
            return this.tax_id_include_base;
        }
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.all_tax = this.all_tax;
            json.tax_string = this.tax_string;
            json.tax_id_include_base = this.tax_id_include_base;
            return json;
        }
        export_for_printing() {
            const json = super.export_for_printing(...arguments);
            json.all_tax = this.get_all_tax();
            json.tax_string = this.get_tax_string();
            json.tax_id_include_base = this.get_tax_id_include_base();
            return json;
        }
        get_all_prices(qty = this.get_quantity()){
            var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
            var taxtotal = 0;
            var product =  this.get_product();
            if (this.pos.config.modify_taxes_line) {
                var taxes_ids = this.tax_id_include_base || [];
            } else {
                var taxes_ids = this.tax_ids || product.taxes_id;
            }
            taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
            var taxdetail = {};
            var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

            var all_taxes = this.compute_all(product_taxes, price_unit, qty, this.pos.currency.rounding);
            var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), qty, this.pos.currency.rounding);
            
            _(all_taxes.taxes).each(function(tax) {
                taxtotal += tax.amount;
                taxdetail[tax.id] = {
                    amount: tax.amount,
                    base: tax.base,
                };
            });
            return {
                "priceWithTax": all_taxes.total_included,
                "priceWithoutTax": all_taxes.total_excluded,
                "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        }
    }
    Registries.Model.extend(Orderline, PosTaxOrderline);

    const biDynamicTaxOrder = (Order) => class biDynamicTaxOrder extends Order {
        add_product(product, options){
            if(this.pos.doNotAllowRefundAndSales() && this.orderlines[0] && this.orderlines[0].refunded_orderline_id) {
                Gui.showPopup('ErrorPopup', {
                    title: _t('Refund and Sales not allowed'),
                    body: _t('It is not allowed to mix refunds and sales')
                });
                return;
            }
            if(this._printed){
                this.pos.removeOrder(this);
                return this.pos.add_new_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var line = Orderline.create({}, {pos: this.pos, order: this, product: product});
            this.fix_tax_included_price(line);

            this.set_orderline_options(line, options);
            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline){
                to_merge_orderline.merge(line);
                this.select_orderline(to_merge_orderline);
                if (this.pos.config.modify_taxes_line) {
                    var selected_orderline = to_merge_orderline;
                    if(selected_orderline){
                        var tax = 0;
                        var tax_str = '';
                        for(var a of this.pos.taxes){
                            for(var b of selected_orderline.get_tax_id_include_base()){
                                if(b == a.id){
                                    tax_str = tax_str + a.name + '  , ';
                                    let percentage_tax = selected_orderline.price * a.amount /100;
                                    let percentage_tax_qty = percentage_tax * selected_orderline.quantity;
                                    tax = tax + percentage_tax_qty;
                                }
                            }
                        }
                        selected_orderline.set_all_tax(tax);
                        selected_orderline.set_tax_string(tax_str);
                    }
                }
            } else {
                this.add_orderline(line);
                this.select_orderline(this.get_last_orderline());
                if (this.pos.config.modify_taxes_line) {
                    var all_selected_added = []
                    var selected_orderline = line;
                    var selected_orderline_taxes_id = line.product.taxes_id;
                    _.each(selected_orderline_taxes_id,function(selected_ids_backend){
                        all_selected_added.push(selected_ids_backend);
                    });
                    _.each(selected_orderline.tax_id_include_base,function(selected_ids){
                        all_selected_added.push(selected_ids);
                    });
                    let unique = [];
                    for (var i = 0; i < all_selected_added.length; i++) {
                        if (unique.indexOf(all_selected_added[i]) === -1) {
                            unique.push(all_selected_added[i]);
                        }
                    }
                    selected_orderline.set_tax_id_include_base(unique);
                    if(selected_orderline){
                        var tax = 0;
                        var tax_str = '';
                        for(var a of this.pos.taxes){
                            for(var b of selected_orderline.tax_id_include_base){
                                if(b == a.id){
                                    tax_str = tax_str + a.name + '  , ';
                                    let percentage_tax = selected_orderline.price * a.amount /100;
                                    let percentage_tax_qty = percentage_tax * selected_orderline.quantity;
                                    tax = tax + percentage_tax_qty;
                                }
                            }
                        }
                        selected_orderline.set_all_tax(tax);
                        selected_orderline.set_tax_string(tax_str);
                    }
                }
            }
            if (options.draftPackLotLines) {
                this.selected_orderline.setPackLotLines(options.draftPackLotLines);
            }
        }
    }
    Registries.Model.extend(Order, biDynamicTaxOrder);
});