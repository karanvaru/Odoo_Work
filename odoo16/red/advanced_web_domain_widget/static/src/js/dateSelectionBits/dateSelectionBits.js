/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class DateSelectionBits extends Component {
    setup() {
        if(!isNaN(new Date(this.props.date))) {
            this.props.onDateTimeChanged("today");
            this.props.value = "today";
        }
    }
    onchange(ev) {
        this.props.onDateTimeChanged(ev.target.value);
    }
}

DateSelectionBits.template = "advanced_web_domain_widget.DateSelectionBits";