/** @odoo-module **/

import { Component, toRaw } from "@odoo/owl";

export class DomainSelectorControlPanelBits extends Component {
    deleteNode() {
        this.props.node.delete();
    }

    insertNode(newNodeType) {
        toRaw(this.props.node).insert(newNodeType); // FIXME WOWL reactivity
    }

    onEnterDeleteNodeBtn() {
        this.props.onHoverDeleteNodeBtn(true);
    }
    onLeaveDeleteNodeBtn() {
        this.props.onHoverDeleteNodeBtn(false);
    }
    onEnterInsertLeafNodeBtn() {
        this.props.onHoverInsertLeafNodeBtn(true);
    }
    onLeaveInsertLeafNodeBtn() {
        this.props.onHoverInsertLeafNodeBtn(false);
    }
    onEnterInsertBranchNodeBtn() {
        this.props.onHoverInsertBranchNodeBtn(true);
    }
    onLeaveInsertBranchNodeBtn() {
        this.props.onHoverInsertBranchNodeBtn(false);
    }
}
DomainSelectorControlPanelBits.template = "advanced_web_domain_widget.DomainSelectorControlPanelBits";
DomainSelectorControlPanelBits.props = {
    node: Object,
    onHoverDeleteNodeBtn: Function,
    onHoverInsertLeafNodeBtn: Function,
    onHoverInsertBranchNodeBtn: Function,
};
