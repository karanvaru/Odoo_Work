/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ModelRecordSelectorBits } from "@advanced_web_domain_widget/core/model_record_selector/model_record_selector";
import { DomainSelectorFieldInputBits } from "./domain_selector_field_input";

import { Component } from "@odoo/owl";

const dso = registry.category("domain_selector/operator_bits");

export class DomainSelectorRelationFieldBits extends Component {
    setup(){
        this.modelName = this.props.field.relation;
        this.fieldName =  this.props.field.name;
        // this.props.update({modelName:this.props.field.relation,fieldName:this.props.field.name})
    }
}
Object.assign(DomainSelectorRelationFieldBits, {
    template: "advanced_web_domain_widget.DomainSelectorRelationFieldBits",
    components: {
        DomainSelectorFieldInputBits
    },

    onDidTypeChange(fieldsInfo) {
        if(fieldsInfo){
            return { value: "0" };
        }else{
            return { value: "0" };
        }    
    },
    onChange(ev) {
        this.props.update({ value: this.parseValue(ev.target.value) });
    },
    getOperators() {
        return ["=", "!=", "ilike", "not ilike", "set", "not set","in","not in"].map((key) => dso.get(key));
    }
});

registry
    .category("domain_selector/fields_bits")
    .add("one2many", DomainSelectorRelationFieldBits)
    .add("many2one", DomainSelectorRelationFieldBits)
    .add("many2many", DomainSelectorRelationFieldBits);
