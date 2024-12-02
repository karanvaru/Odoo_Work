/** @odoo-module **/

import { registry } from "@web/core/registry";

import { Component } from "@odoo/owl";

const dsf = registry.category("domain_selector/fields_bits");
const dso = registry.category("domain_selector/operator_bits");

export class DomainSelectorSelectionFieldBits extends Component {
    onChange(ev) {
        this.props.update({ value: ev.target.value });
    }
}
Object.assign(DomainSelectorSelectionFieldBits, {
    template: "advanced_web_domain_widget.DomainSelectorSelectionFieldBits",

    onDidTypeChange(field) {
        return { value: field.selection[0][0] };
    },
    getOperators() {
        return ["=", "!=", "set", "not set"].map((key) => dso.get(key));
    },
});

dsf.add("selection", DomainSelectorSelectionFieldBits);
