/** @odoo-module **/

import { DatePicker, DateTimePicker } from "@web/core/datepicker/datepicker";
import { DateSelectionBits } from "@advanced_web_domain_widget/js/dateSelectionBits/dateSelectionBits";
import {
  deserializeDate,
  deserializeDateTime,
  serializeDate,
  serializeDateTime,
} from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";

import { Component } from "@odoo/owl";

const dsf = registry.category("domain_selector/fields_bits");
const dso = registry.category("domain_selector/operator_bits");

export class DomainSelectorDateTimeFieldBits extends Component {
  get component() {
    if (this.props.operator.value == "date_filter") {
      return DateSelectionBits;
    }
    const { DatePicker, DateTimePicker } = this.constructor.components;
    return this.props.field.type === "date" ? DatePicker : DateTimePicker;
  }
  get deserializedValue() {
    if (this.props.operator.value == "date_filter") {
      return this.props.value || "";
    }
    const deserialize =
      this.props.field.type === "date" ? deserializeDate : deserializeDateTime;
    return this.props.value
      ? deserialize(this.props.value)
      : luxon.DateTime.local();
  }
  onChange(value) {
    if (typeof value == "string") {
      this.props.update({ value: value });
      return;
    }
    if (!this.deserializedValue.isValid && !value) {
      return;
    }
    const serialize =
      this.props.field.type === "date" ? serializeDate : serializeDateTime;
    this.props.update({ value: serialize(value || luxon.DateTime.local()) });
  }
}
Object.assign(DomainSelectorDateTimeFieldBits, {
  template: "advanced_web_domain_widget.DomainSelectorDateTimeFieldBits",
  components: {
    DatePicker,
    DateTimePicker,
    DateSelectionBits,
  },

  onDidTypeChange(field) {
    const serialize = field.type === "date" ? serializeDate : serializeDateTime;
    return { value: serialize(luxon.DateTime.local()) };
  },
  getOperators() {
    return [
      "=",
      "!=",
      ">",
      "<",
      ">=",
      "<=",
      "set",
      "not set",
      "date_filter",
    ].map((key) => dso.get(key));
  },
});

dsf.add("date", DomainSelectorDateTimeFieldBits);
dsf.add("datetime", DomainSelectorDateTimeFieldBits);
