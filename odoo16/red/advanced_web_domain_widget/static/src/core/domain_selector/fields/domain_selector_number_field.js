/** @odoo-module **/

import { registry } from "@web/core/registry";
import { DomainSelectorFieldInputBits } from "./domain_selector_field_input";

import { Component } from "@odoo/owl";

const dsf = registry.category("domain_selector/fields_bits");
const dso = registry.category("domain_selector/operator_bits");

export class DomainSelectorNumberFieldBits extends Component {}
Object.assign(DomainSelectorNumberFieldBits, {
    template: "advanced_web_domain_widget.DomainSelectorNumberFieldBits",
    components: {
        DomainSelectorFieldInputBits,
    },

    onDidTypeChange() {
        return { value: 0 };
    },
    getOperators() {
        return [
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "ilike",
            "not ilike",
            "set",
            "not set",
        ].map((key) => dso.get(key));
    },
});

dsf.add("integer", DomainSelectorNumberFieldBits);
dsf.add("float", DomainSelectorNumberFieldBits);
dsf.add("monetary", DomainSelectorNumberFieldBits);
