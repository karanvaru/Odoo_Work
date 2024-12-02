/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { DomainSelectorBits, DomainSelectorBits2 } from "../domain_selector/domain_selector";
import { _lt } from "@web/core/l10n/translation";

import { Component, useState } from "@odoo/owl";

export class DomainSelectorDialogBits extends Component {
    setup() {
        this.state = useState({
            value: this.props.initialValue,
        });
    }

    get dialogTitle() {
        return _lt("Domain");
    }

    get domainSelectorProps() {
        return {
            className: this.props.className,
            resModel: this.props.resModel,
            readonly: this.props.readonly,
            isDebugMode: this.props.isDebugMode,
            defaultLeafValue: this.props.defaultLeafValue,
            value: this.state.value,
            update: (value) => {
                this.state.value = value;
            },
        };
    }

    async onSave() {
        await this.props.onSelected(this.state.value);
        this.props.close();
    }
    onDiscard() {
        this.props.close();
    }
}
DomainSelectorDialogBits.template = "advanced_web_domain_widget.DomainSelectorDialogBits";
DomainSelectorDialogBits.components = {
    Dialog,
    DomainSelectorBits,
};
DomainSelectorDialogBits.props = {
    close: Function,
    className: { type: String, optional: true },
    resModel: String,
    readonly: { type: Boolean, optional: true },
    isDebugMode: { type: Boolean, optional: true },
    defaultLeafValue: { type: Array, optional: true },
    initialValue: { type: String, optional: true },
    onSelected: { type: Function, optional: true },
};
DomainSelectorDialogBits.defaultProps = {
    initialValue: "",
    onSelected: () => {},
    readonly: true,
    isDebugMode: false,
};


export class DomainSelectorDialogBits2 extends DomainSelectorDialogBits {}

DomainSelectorDialogBits2.components = {
    ...DomainSelectorDialogBits2.components,
    DomainSelectorBits: DomainSelectorBits2
}