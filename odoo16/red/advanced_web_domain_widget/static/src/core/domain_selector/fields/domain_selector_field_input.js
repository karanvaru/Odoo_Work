/** @odoo-module **/

import { registry } from "@web/core/registry";

import { Component } from "@odoo/owl";
const parsers = registry.category("parsers");

export class DomainSelectorFieldInputBits extends Component {
    parseValue(value) {
        const parser = parsers.get(this.props.field.type, (value) => value);
        try {
            return parser(value);
        } catch (_) {
            return value;
        }
    }

    onChange(ev) {
        this.props.update({ value: this.parseValue(ev.target.value) });
    }
}
DomainSelectorFieldInputBits.template = "advanced_web_domain_widget.DomainSelectorFieldInputBits";
