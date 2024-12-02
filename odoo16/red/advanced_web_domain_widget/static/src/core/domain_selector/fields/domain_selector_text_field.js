/** @odoo-module **/

import { registry } from "@web/core/registry";
import { DomainSelectorFieldInputBits } from "./domain_selector_field_input";
import { DomainSelectorFieldInputWithTagsBits } from "./domain_selector_field_input_with_tags";

import { Component } from "@odoo/owl";

const dsf = registry.category("domain_selector/fields_bits");
const dso = registry.category("domain_selector/operator_bits");

export class DomainSelectorTextFieldBits extends Component {}
Object.assign(DomainSelectorTextFieldBits, {
    template: "advanced_web_domain_widget.DomainSelectorTextFieldBits",
    components: {
        DomainSelectorFieldInputBits,
        DomainSelectorFieldInputWithTagsBits,
    },

    onDidTypeChange() {
        return { value: "" };
    },
    getOperators() {
        return ["=", "!=", "ilike", "not ilike", "set", "not set", "in", "not in"].map((key) =>
            dso.get(key)
        );
    },
});

dsf.add("char", DomainSelectorTextFieldBits);
dsf.add("html", DomainSelectorTextFieldBits);
dsf.add("text", DomainSelectorTextFieldBits);
