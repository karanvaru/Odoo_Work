/** @odoo-module **/
import { sortBy } from "@web/core/utils/arrays";
import { fuzzyLookup } from "@web/core/utils/search";
import { useModelRecord } from "./model_record_hook";
import { useUniquePopover } from "./unique_popover_hook";
import core from 'web.core';
var _t = core._t;

import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";

export class ModelRecordSelectorBits extends Component {
    setup() {
        this.modelRecord = useModelRecord();
        this.chain = [];
        this.searchValue = ""
        this.tags = [];
        this.props.value = this.props.node.operands[1]; 
        if(this.props.fieldInfo.relation){
            this.modelName = this.props.fieldInfo.relation;
            this.fieldName = this.props.fieldInfo.name;
        } else {
            this.modelName = this.props.modelName;
            this.fieldName = this.props.fieldInfo.name;
        }
        onWillStart(async () => {
            this.chain = await this.loadChain(this.modelName, this.fieldName);
        });
        onWillUpdateProps(async (nextProps) => {
            this.chain = await this.loadChain(this.modelName, this.fieldName);
        });
    }
    async loadChain(resModel, fieldName) {
        let recordsInfo = {};
        let currentNode = {};
        let exist_values = [];
        const values = this.props.node.operands[1];
        var self =  this;
        if (resModel) {
            recordsInfo = await this.modelRecord.loadModelRecords(resModel);
            if (resModel == 'res.users') {
                recordsInfo.unshift({ 'id': 0, 'display_name': 'Logged In User' })
            } else if(resModel == 'res.company'){
                recordsInfo.unshift({ 'id': 0, 'display_name': 'Environment Company' })
            }
            if(values.length){
                self.tags = []
                _.each(recordsInfo, function(record){
                    if(_.contains(values, record.id)){
                        self.tags.push(record)
                    }
                });
                recordsInfo = _.filter(recordsInfo, function (val) {
                    return !_.contains(values, val.id);
                });
            }
            if (this.searchValue) {
                recordsInfo = fuzzyLookup(this.searchValue, recordsInfo, (key)=> key.display_name)
            }
            currentNode = { resModel: resModel, Selectedfield: fieldName, records: recordsInfo };
        }
        exist_values;
        const chain = [currentNode];
        return chain;
    }
    onSelection(ev) {
        $(ev.currentTarget).parent().find('.o_record_selector_popover').toggleClass('d-none');
    }
    closeRecs(ev) {
        $(ev.currentTarget).parents('.o_record_selector_popover').toggleClass('d-none');
    }
    removeTag(ev) {
        const operands = this.props.node.operands[1]
        if(ev.currentTarget.dataset.id && operands.length && typeof(operands) == 'object'){
            let TagId = Number(ev.currentTarget.dataset.id);
            this.tags = this.tags.filter((tag)=>{
                return tag[0] != TagId;
            });
            let TagIndex = operands.indexOf(TagId)
            operands.splice(TagIndex,1)
            this.props.node.update({ value: operands });
            if(!operands.length){
                this.tags = [];
            }
            this.render();
        }
    }
    async onSearch(ev) {
        this.searchValue = ev.target.value;
        this.chain = await this.loadChain(this.modelName, this.fieldName);
        if(this.chain[0].records){
            let recordKeys = this.chain[0].records;
            if (this.searchValue) {
                recordKeys = fuzzyLookup(this.searchValue, this.chain[0].records, (key)=> key.display_name)
            }
            this.chain[0].records = recordKeys;
            this.render();
        }
    }
    sortedKeys(obj) {
        const keys = Object.keys(obj);
        return sortBy(keys, (key) => obj[key].string);
    }
    onSelectRecord(ev) {
        this.props.value = this.props.node.operands[1]
        let targetElem = $(ev.currentTarget);
        let recID = Number(ev.currentTarget.dataset.id)
        let recNAME = targetElem.html();
        if (!_.contains(this.props.value, recID)) {
            this.props.value.push(recID);
            this.props.node.update({ value: this.props.value });
        }
        $(ev.currentTarget).parents('.o_record_selector_popover').toggleClass('d-none');
    }
}

Object.assign(ModelRecordSelectorBits, {
    template: "advanced_web_domain_widget._ModelRecordSelectorBits",
    props: {
        fieldName: String,
        modelName: String,
        node: Object,
        fieldInfo: {},
        value: { type: Array, optional: true },
        showSearchInput: { type: Boolean, optional: true },
    },
    defaultProps: {
        value: [],
        showSearchInput: true,
        update: () => { },
    },
});
