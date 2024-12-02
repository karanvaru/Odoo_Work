/** @odoo-module **/

import { DomainSelectorBits, DomainSelectorBits2 } from "@advanced_web_domain_widget/core/domain_selector/domain_selector";
import { DomainSelectorDialogBits, DomainSelectorDialogBits2 } from "@advanced_web_domain_widget/core/domain_selector_dialog/domain_selector_dialog";
import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useBus, useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { Domain } from "@web/core/domain";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";

function calculateDate(domain) {
  if (Array.isArray(domain)) {
    const field_name = domain[0];
    const operator = domain[1];
    const val = domain[2];

    const current_date = new Date();
    current_date.setHours(0, 0, 0, 0);

    if (operator !== "date_filter") {
        return [domain];
    }

    if (val === "today") {
        const start_of_today = new Date(current_date);
        const end_of_today = new Date(current_date);
        end_of_today.setDate(end_of_today.getDate() + 1);

        return ["&", [field_name, ">=", start_of_today], [field_name, "<", end_of_today]];
    }

    if (val === "this_week") {
        const start_of_week = new Date(current_date);
        start_of_week.setDate(current_date.getDate() - current_date.getDay());
        const end_of_week = new Date(start_of_week);
        end_of_week.setDate(end_of_week.getDate() + 7);

        return ["&", [field_name, ">=", start_of_week], [field_name, "<", end_of_week]];
    }

    if (val === "this_month") {
        const start_of_month = new Date(current_date);
        start_of_month.setDate(1);
        const end_of_month = new Date(current_date);
        end_of_month.setMonth(end_of_month.getMonth() + 1, 0);

        return ["&", [field_name, ">=", start_of_month], [field_name, "<=", end_of_month]];
    }

    if (val === "this_quarter") {
        const start_of_quarter = new Date(current_date);
        start_of_quarter.setMonth(Math.floor(start_of_quarter.getMonth() / 3) * 3, 1);
        const end_of_quarter = new Date(start_of_quarter);
        end_of_quarter.setMonth(end_of_quarter.getMonth() + 3, 0);

        return ["&", [field_name, ">=", start_of_quarter], [field_name, "<", end_of_quarter]];
    }

    if (val === "this_year") {
        const start_of_year = new Date(current_date);
        start_of_year.setMonth(0, 1);
        const end_of_year = new Date(start_of_year);
        end_of_year.setFullYear(end_of_year.getFullYear() + 1, 0, 0);

        return ["&", [field_name, ">=", start_of_year], [field_name, "<", end_of_year]];
    }

    if (val === "last_day") {
        const start_of_yesterday = new Date(current_date);
        start_of_yesterday.setDate(start_of_yesterday.getDate() - 1);

        return ["&", [field_name, ">=", start_of_yesterday], [field_name, "<", current_date]];
    }

    if (val === "last_week") {
        const end_of_last_week = new Date(current_date);
        end_of_last_week.setDate(end_of_last_week.getDate() - end_of_last_week.getDay());
        const start_of_last_week = new Date(end_of_last_week);
        start_of_last_week.setDate(start_of_last_week.getDate() - 6);

        return ["&", [field_name, ">=", start_of_last_week], [field_name, "<", end_of_last_week]];
    }

    if (val === "last_month") {
        const start_of_last_month = new Date(current_date);
        start_of_last_month.setMonth(start_of_last_month.getMonth() - 1, 1);
        const end_of_last_month = new Date(start_of_last_month);
        end_of_last_month.setMonth(end_of_last_month.getMonth() + 1, 0);

        return ["&", [field_name, ">=", start_of_last_month], [field_name, "<", end_of_last_month]];
    }

    if (val === "last_quarter") {
        const start_of_this_quarter = new Date(current_date);
        start_of_this_quarter.setMonth(Math.floor(start_of_this_quarter.getMonth() / 3) * 3, 1);
        const end_of_last_quarter = new Date(start_of_this_quarter);
        end_of_last_quarter.setMonth(end_of_last_quarter.getMonth() - 1, 0);
        const start_of_last_quarter = new Date(end_of_last_quarter);
        start_of_last_quarter.setMonth(start_of_last_quarter.getMonth() - 3, 1);

        return ["&", [field_name, ">=", start_of_last_quarter], [field_name, "<", end_of_last_quarter]];
    }

    if (val === "last_year") {
        const end_of_last_year = new Date(current_date);
        end_of_last_year.setFullYear(end_of_last_year.getFullYear() - 1, 0, 0);
        const start_of_last_year = new Date(end_of_last_year);
        start_of_last_year.setFullYear(start_of_last_year.getFullYear() - 1, 0, 1);

        return ["&", [field_name, ">=", start_of_last_year], [field_name, "<", end_of_last_year]];
    }

    if (val === "last_7_days") {
        const start_of_last_7_days = new Date(current_date);
        start_of_last_7_days.setDate(start_of_last_7_days.getDate() - 7);

        return [[field_name, ">=", start_of_last_7_days]];
    }

    if (val === "last_30_days") {
        const start_of_last_30_days = new Date(current_date);
        start_of_last_30_days.setDate(start_of_last_30_days.getDate() - 30);

        return [[field_name, ">=", start_of_last_30_days]];
    }

    if (val === "last_90_days") {
        const start_of_last_90_days = new Date(current_date);
        start_of_last_90_days.setDate(start_of_last_90_days.getDate() - 90);

        return [[field_name, ">=", start_of_last_90_days]];
    }

    if (val === "last_365_days") {
        const start_of_last_365_days = new Date(current_date);
        start_of_last_365_days.setDate(start_of_last_365_days.getDate() - 365);

        return [[field_name, ">=", start_of_last_365_days]];
    }

    if (val === "next_day") {
        const start_of_next_day = new Date(current_date);
        start_of_next_day.setDate(start_of_next_day.getDate() + 1);
        const end_of_next_day = new Date(start_of_next_day);
        end_of_next_day.setDate(end_of_next_day.getDate() + 1);

        return ["&", [field_name, ">=", start_of_next_day], [field_name, "<", end_of_next_day]];
    }

    if (val === "next_week") {
        const start_of_next_week = new Date(current_date);
        start_of_next_week.setDate(current_date.getDate() + (7 - current_date.getDay()));
        const end_of_next_week = new Date(start_of_next_week);
        end_of_next_week.setDate(end_of_next_week.getDate() + 7);

        return ["&", [field_name, ">=", start_of_next_week], [field_name, "<", end_of_next_week]];
    }

    if (val === "next_month") {
      const start_of_next_month = new Date(current_date);
            start_of_next_month.setMonth(current_date.getMonth() + 1, 1);
            const end_of_next_month = new Date(start_of_next_month);
            end_of_next_month.setMonth(end_of_next_month.getMonth() + 1, 1);

            return ["&", [field_name, ">=", start_of_next_month], [field_name, "<", end_of_next_month]];
        }

        if (val === "next_quarter") {
            const start_of_this_quarter = new Date(current_date);
            start_of_this_quarter.setMonth(Math.floor(start_of_this_quarter.getMonth() / 3) * 3, 1);
            const end_of_next_quarter = new Date(start_of_this_quarter);
            end_of_next_quarter.setMonth(end_of_next_quarter.getMonth() + 3, 0);
            const start_of_next_quarter = new Date(end_of_next_quarter);
            start_of_next_quarter.setMonth(start_of_next_quarter.getMonth() + 1, 1);

            return ["&", [field_name, ">=", start_of_next_quarter], [field_name, "<", end_of_next_quarter]];
        }

        if (val === "next_year") {
            const start_of_next_year = new Date(current_date);
            start_of_next_year.setFullYear(current_date.getFullYear() + 1, 0, 1);
            const end_of_next_year = new Date(start_of_next_year);
            end_of_next_year.setFullYear(end_of_next_year.getFullYear() + 1, 0, 0);

            return ["&", [field_name, ">=", start_of_next_year], [field_name, "<", end_of_next_year]];
        }
    }
    return [domain];
}

export class DomainFieldBits extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            recordCount: null,
            isValid: true,
        });
        this.addDialog = useOwnedDialogs();

        this.displayedDomain = null;
        this.isDebugEdited = false;

        onWillStart(() => {
            this.displayedDomain = this.props.value;
            this.loadCount(this.props);
        });
        onWillUpdateProps((nextProps) => {
            this.isDebugEdited = this.isDebugEdited && this.props.readonly === nextProps.readonly;
            if (!this.isDebugEdited) {
                this.displayedDomain = nextProps.value;
                this.loadCount(nextProps);
            }
        });

        useBus(this.env.bus, "RELATIONAL_MODEL:NEED_LOCAL_CHANGES", async (ev) => {
            if (this.isDebugEdited) {
                const prom = this.loadCount(this.props);
                ev.detail.proms.push(prom);
                await prom;
                if (!this.state.isValid) {
                    this.props.record.setInvalidField(this.props.name);
                }
            }
        });
    }

    getContext(p) {
        return p.record.getFieldContext(p.name);
    }
    getResModel(p) {
        let resModel = p.resModel;
        if (p.record.fieldNames.includes(resModel)) {
            resModel = p.record.data[resModel];
        }
        return resModel;
    }

    onButtonClick() {
        const domain = this.getDomain(this.props.value).toList(this.getContext(this.props)) || [];
        const newDomain = [];
            domain.forEach((ele) => {
                if(ele.includes("date_filter") && !isNaN(new Date(ele[2]))) {
                    ele[2] = "today";
                }
                if(ele.includes("date_filter")) {
                    calculateDate(ele).forEach(el => newDomain.push(el));
                } else {
                    newDomain.push(ele);
                }
            });
        this.addDialog(SelectCreateDialog, {
            title: this.env._t("Selected records"),
            noCreate: true,
            multiSelect: false,
            resModel: this.getResModel(this.props),
            domain: newDomain,
            context: this.getContext(this.props) || {},
        }, {
            // The counter is reloaded "on close" because some modal allows to modify data that can impact the counter
            onClose: () => this.loadCount(this.props)
        });
    }
    get isValidDomain() {
        try {
            this.getDomain(this.props.value).toList();
            return true;
        } catch (_e) {
            // WOWL TODO: rethrow error when not the expected type
            return false;
        }
    }

    getDomain(value) {
        return new Domain(value || "[]");
    }
    async loadCount(props) {
        if (!this.getResModel(props)) {
            Object.assign(this.state, { recordCount: 0, isValid: true });
        }

        let recordCount;
        try {
            const domain = this.getDomain(props.value).toList(this.getContext(props));
            const newDomain = [];
            domain.forEach((ele) => {
                if(ele.includes("date_filter") && !isNaN(new Date(ele[2]))) {
                    ele[2] = "today";
                }
                if(ele.includes("date_filter")) {
                    calculateDate(ele).forEach(el => newDomain.push(el));
                } else {
                    newDomain.push(ele);
                }
            });
            recordCount = await this.orm.silent.call(
                this.getResModel(props),
                "get_widget_count",
                [newDomain],
                { context: this.getContext(props) }
            );
        } catch (_e) {
            // WOWL TODO: rethrow error when not the expected type
            Object.assign(this.state, { recordCount: 0, isValid: false });
            return;
        }
        Object.assign(this.state, { recordCount, isValid: true });
    }

    update(domain, isDebugEdited) {
        this.isDebugEdited = isDebugEdited;
        return this.props.update(domain);
    }

    onEditDialogBtnClick() {
        this.addDialog(DomainSelectorDialogBits, {
            resModel: this.getResModel(this.props),
            initialValue: this.props.value || "[]",
            readonly: this.props.readonly,
            isDebugMode: !!this.env.debug,
            onSelected: this.props.update,
        });
    }  
}

DomainFieldBits.template = "advanced_web_domain_widget.DomainFieldBits";
DomainFieldBits.components = {
    DomainSelectorBits,
};
DomainFieldBits.props = {
    ...standardFieldProps,
    editInDialog: { type: Boolean, optional: true },
    resModel: { type: String, optional: true },
};
DomainFieldBits.defaultProps = {
    editInDialog: false,
};

DomainFieldBits.displayName = _lt("Bits");
DomainFieldBits.supportedTypes = ["char"];

DomainFieldBits.isEmpty = () => false;
DomainFieldBits.extractProps = ({ attrs }) => {
    return {
        editInDialog: attrs.options.in_dialog,
        resModel: attrs.options.model,
    };
};

registry.category("fields").add("terabits_domain", DomainFieldBits);


class DomainFieldBits2 extends DomainFieldBits {
    onEditDialogBtnClick() {
        this.addDialog(DomainSelectorDialogBits2, {
            resModel: this.getResModel(this.props),
            initialValue: this.props.value || "[]",
            readonly: this.props.readonly,
            isDebugMode: !!this.env.debug,
            onSelected: this.props.update,
        });
    } 
}

DomainFieldBits2.components = {
    ...DomainFieldBits.components,
    DomainSelectorBits: DomainSelectorBits2
}

DomainFieldBits2.template = "advanced_web_domain_widget.DomainFieldBits2"

registry.category("fields").add("terabits_field_domain", DomainFieldBits2);
