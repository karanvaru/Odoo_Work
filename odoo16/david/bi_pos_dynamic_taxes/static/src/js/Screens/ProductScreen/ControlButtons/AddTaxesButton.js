odoo.define('bi_pos_dynamic_taxes.AddTaxesButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useState } = owl;
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class AddTaxesButton extends PosComponent {
        setup() {
           super.setup();
           useListener('click', this.onClick);
        }
        async onClick() {
            if(this.env.pos.get_order().get_orderlines().length > 0){
                const { confirmed , payload } = await this.showPopup('TaxesTypePopup', {
                                                    title: this.env._t('Select Taxes Need To Apply')});
            } else {
                 alert("Please Select The Product First ");
            }
        }
    }
    AddTaxesButton.template = 'AddTaxesButton';
    ProductScreen.addControlButton({
    component: AddTaxesButton,
    condition: function() {
            if(this.env.pos.config.modify_taxes_line){
                return true;
            } else {
                return false;
            }
        },
    });
    Registries.Component.add(AddTaxesButton);
    return AddTaxesButton;
});