/** @odoo-module **/
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

import { Component } from "@odoo/owl";

export class DomainSelectorBranchOperatorBits extends Component {
    onOperatorSelected(operator) {
        this.props.node.update(operator);
    }
}
DomainSelectorBranchOperatorBits.components = {
    Dropdown,
    DropdownItem,
};
DomainSelectorBranchOperatorBits.template = "advanced_web_domain_widget.DomainSelectorBranchOperatorBits";
DomainSelectorBranchOperatorBits.props = {
    node: Object,
    readonly: Boolean,
    showCaret: {
        type: Boolean,
        optional: true,
    },
};
