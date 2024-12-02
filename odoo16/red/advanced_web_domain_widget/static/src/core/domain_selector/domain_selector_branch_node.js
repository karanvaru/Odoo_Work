/** @odoo-module **/

import { DomainSelectorBranchOperatorBits } from "./domain_selector_branch_operator";
import { DomainSelectorControlPanelBits } from "./domain_selector_control_panel";
import { DomainSelectorLeafNodeBits, DomainSelectorLeafNodeBits2 } from "./domain_selector_leaf_node";

import { Component, useRef } from "@odoo/owl";

export class DomainSelectorBranchNodeBits extends Component {
    setup() {
        this.root = useRef("root");
    }
    onHoverDeleteNodeBtn(hovering) {
        this.root.el.classList.toggle("o_hover_btns", hovering);
    }
    onHoverInsertLeafNodeBtn(hovering) {
        this.root.el.classList.toggle("o_hover_add_node", hovering);
    }
    onHoverInsertBranchNodeBtn(hovering) {
        this.root.el.classList.toggle("o_hover_add_node", hovering);
        this.root.el.classList.toggle("o_hover_add_inset_node", hovering);
    }
}
DomainSelectorBranchNodeBits.template = "advanced_web_domain_widget.DomainSelectorBranchNodeBits";
DomainSelectorBranchNodeBits.components = {
    DomainSelectorBranchNodeBits,
    DomainSelectorBranchOperatorBits,
    DomainSelectorControlPanelBits,
    DomainSelectorLeafNodeBits,
};

export class DomainSelectorBranchNodeBits2 extends DomainSelectorBranchNodeBits {}

DomainSelectorBranchNodeBits2.components = {
    ...DomainSelectorBranchNodeBits.components,
    DomainSelectorLeafNodeBits: DomainSelectorLeafNodeBits2
}