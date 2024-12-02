odoo.define('bi_pos_dynamic_taxes.TaxesTypePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState, onMounted } = owl;
    const { _lt } = require('@web/core/l10n/translation');
    const { Orderline } = require('point_of_sale.models');

    class TaxesTypePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            let order = this.env.pos.get_order();
            this.state = useState({ highlighted_tax: []});
            onMounted(() => this._mounted());
        }
        _mounted(){
            var selected_orderline = this.env.pos.get_order().get_selected_orderline();
            _.each(selected_orderline.get_tax_id_include_base(),function(selected_tax_id_include_base){
                _.each($(".child"), function (tax_data) {
                    if(tax_data.getAttribute("data-id") == selected_tax_id_include_base){
                        $(tax_data).addClass('highlight');
                    }
                });
            });
        }
        async highlight_tax(event) {
            if ($(event.currentTarget).hasClass("highlight")) {
                $(event.currentTarget).removeClass("highlight");
            } else {
                $(event.currentTarget).addClass("highlight");
            }
        }
        async set_tax(){
            var order = this.env.pos.selectedOrder;
            var orderline = order.get_selected_orderline()
            await this.save_tax();
            this.env.posbus.trigger('close-popup', {
                popupId: this.props.id,
                response: { confirmed: false, payload: null },
            });
        }
        save_tax(){
            var self = this;
            var current_order = self.env.pos.get_order();
            var selected_orderline = current_order.get_selected_orderline()
            var data = current_order.export_as_JSON();
            var all_selected_added = []
            var all_selected_added_base = []
            var selected_orderline_taxes_id = selected_orderline.product.taxes_id;
            _.each(selected_orderline_taxes_id,function(selected_ids_backend){
                all_selected_added.push(selected_ids_backend);
                all_selected_added_base.push(selected_ids_backend);
            });
            var highlight_data = []
            _.each($("div.highlight"), function (selected_tax) {
                all_selected_added.push(parseInt(selected_tax.getAttribute("data-value")));
                highlight_data.push(parseInt(selected_tax.getAttribute("data-value")));
            });
            let unique = [];
            for (var i = 0; i < all_selected_added.length; i++) {
                if (unique.indexOf(all_selected_added[i]) === -1) {
                    unique.push(all_selected_added[i]);
                }
            }
            var all_selected_added_config = []
            for(var config_data of  this.env.pos.bi_taxes_data){
                all_selected_added_config.push(config_data.id)
            }
            for(var a of unique){
                if(all_selected_added_base.indexOf(a) !== -1 && all_selected_added_config.indexOf(a) !== -1 && highlight_data.indexOf(a) === -1){
                     for( var i = 0; i < unique.length; i++){
                        if ( unique[i] === a) {
                            unique.splice(i, 1);
                        }
                     }
                }
            }
            var tax = 0;
            var tax_str = '';
            for(var a of this.env.pos.taxes){
                for(var b of unique){
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
            selected_orderline.set_tax_id_include_base(unique);
        }
    }
    TaxesTypePopup.template = 'TaxesTypePopup';
    TaxesTypePopup.defaultProps = {
        confirmText: _lt('Add'),
        cancelText: _lt('Cancel'),
        body: '',
    };

    Registries.Component.add(TaxesTypePopup);
    return TaxesTypePopup;
});