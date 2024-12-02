odoo.define('bi_pos_dynamic_taxes.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');


    const PosProductScreen = ProductScreen =>
        class extends ProductScreen {
            setup() {
                super.setup();
            }
            _setValue(val) {
                if (this.currentOrder.get_selected_orderline()) {
                    if (this.env.pos.numpadMode === 'quantity') {
                        const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                        if (this.env.pos.config.modify_taxes_line) {
                            var selectedLine = this.currentOrder.get_selected_orderline()
                            if(selectedLine){
                                var tax = 0;
                                var tax_str = '';
                                for(var a of this.env.pos.taxes){
                                    for(var b of selectedLine.tax_id_include_base){
                                        if(b == a.id){
                                            tax_str = tax_str + a.name + '  , ';
                                            let percentage_tax = selectedLine.price * a.amount /100;
                                            let percentage_tax_qty = percentage_tax * selectedLine.quantity;
                                            tax = tax + percentage_tax_qty;
                                        }
                                    }
                                }
                                selectedLine.set_all_tax(tax);
                                selectedLine.set_tax_string(tax_str);
                            }
                        }
                        if (!result) NumberBuffer.reset();
                    } else if (this.env.pos.numpadMode === 'discount') {
                        this.currentOrder.get_selected_orderline().set_discount(val);
                    } else if (this.env.pos.numpadMode === 'price') {
                        var selected_orderline = this.currentOrder.get_selected_orderline();
                        selected_orderline.price_manually_set = true;
                        selected_orderline.set_unit_price(val);
                        if (this.env.pos.config.modify_taxes_line) {
                            if(selected_orderline){
                                var tax = 0;
                                var tax_str = '';
                                for(var a of this.env.pos.taxes){
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
                }
            }
        };
    Registries.Component.extend(ProductScreen, PosProductScreen);
    return ProductScreen;
});