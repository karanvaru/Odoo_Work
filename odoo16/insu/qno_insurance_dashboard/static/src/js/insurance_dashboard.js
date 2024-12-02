odoo.define("qno_insurance_dashboard.insurance_dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var session = require('web.session');
    var stage_domain;
    var InsuranceDashboard = AbstractAction.extend({
        contentTemplate: 'InsuranceDashboard',
         events: {
            "click .vehicle_type": "vehicle_type",
            "click .health_type": "health_type",
            "click .corporate_type": "corporate_type",
            "click .view_policy": "view_policy",
            "click .view_category": "view_category",
            "click .to_invoice_type": "to_invoice_type",
            "click .invoice_type": "invoice_type",
            "click .view_company": "view_company",
            "click .view_detail": "view_detail",
            "click .new_claim": "new_claim",
            "click .in_process_claim": "in_process_claim",
            "click .query_status": "query_status",
            "click .approved_claim": "approved_claim",
            "click .reject_claim": "reject_claim",
            "click .cancel_status": "cancel_status",
         },

         init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['InsurancePolicyData'];
         },

        willStart: function(){
            var self = this;
            return this._super()
                .then(function() {
                var def1 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_all_policy_type_count',
                }).then(function(result) {
                    self.policy_count_count_dict = result
                });
                var def2 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_all_agent',
                }).then(function(result) {
                    self.agent_list = result
                });
                var def3 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_policy_category',
                }).then(function(result) {
                    self.category_list = result
                });
                var def4 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_policy_invoice_status',
                }).then(function(result) {
                    self.invoice_status_data_dct = result
                });
                var def5 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_policy_by_company',
                }).then(function(result) {
                    self.company_list = result
                });
                var def6 = self._rpc({
                    model: 'insurance.policy',
                    method: 'get_policy_expire_30_days',
                }).then(function(result) {
                    self.insurance_list = result
                });
                var def7 = self._rpc({
                    model: 'insurance.claim.details',
                    method: 'get_claim_count',
                }).then(function(result) {
                    self.claimed_list = result
                });
                return $.when(def1,def2,def3,def4,def5,def6,def7);
            });
        },
        start: function() {
            var self = this;
            this.set("title", 'InsuranceDashboard');
            return this._super().then(function() {
                self.render_dashboards();
            });
        },

        new_claim: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("New"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'new']],
                context: {default_state: 'new'},
                target: 'current'
            });
        },
        in_process_claim: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("In Progress"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'in_process']],
                context: {default_state: 'in_process'},
                target: 'current'
            });
        },

             query_status: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Query"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'query']],
                context: {default_state: 'query'},
                target: 'current'
            });
        },
             approved_claim: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Approved"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'approved']],
                context: {default_state: 'approved'},
                target: 'current'
            });
        },
             reject_claim: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Rejected"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'rejected']],
                context: {default_state: 'rejected'},
                target: 'current'
            });
        },
        cancel_status: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Cancelled"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.claim.details',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'cancelled']],
                context: {default_state: 'cancelled'},
                target: 'current'
            });
        },


        vehicle_type: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Vehicle"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.policy',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['policy_type', '=', 'vehicle']],
                context: {default_policy_type: 'vehicle'},
                target: 'current'
            });
        },

        health_type: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Health"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.policy',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['policy_type', '=', 'health']],
                context: {default_policy_type: 'health'},
                target: 'current'
            });
        },

        corporate_type: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("SME"),
                type: 'ir.actions.act_window',
                res_model: 'insurance.policy',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['policy_type', '=', 'corporate']],
                context: {default_policy_type: 'corporate'},
                target: 'current'
            });
        },

         view_policy: function (ev) {
             var self = this;
             var agent = $(ev.target).data().id;
             ev.stopPropagation();
             ev.preventDefault();
             this.do_action({
                 res_model: 'insurance.policy',
                 name: _t('Insurance Policies'),
                 views: [[false, 'list'], [false, 'form']],
                 view_mode: 'tree,form',
                 type: 'ir.actions.act_window',
                 domain: [['agent_id', '=', agent]],
             });
         },

         view_category: function (ev) {
             var self = this;
             var category = $(ev.target).data().id;
             console.log("!!!!!!!!!!!!!!!  category",category)
             ev.stopPropagation();
             ev.preventDefault();
             this.do_action({
                 res_model: 'insurance.policy',
                 name: _t('Insurance Policies'),
                 views: [[false, 'list'], [false, 'form']],
                 view_mode: 'tree,form',
                 type: 'ir.actions.act_window',
                 domain: [['policy_category_id', '=', category]],
             });
         },

         invoice_type: function (ev) {
             var self = this;
             ev.stopPropagation();
             ev.preventDefault();
             this.do_action({
                 name: _t("Commission"),
                 type: 'ir.actions.act_window',
                 res_model: 'insurance.policy',
                 view_mode: 'tree,form',
                 views: [[false, 'list'], [false, 'form']],
                 domain: [['invoice_status', '=', 'invoiced']],
                 context: {default_invoice_status: 'invoiced'},
                 target: 'current'
             });
         },

         to_invoice_type: function (ev) {
             var self = this;
             ev.stopPropagation();
             ev.preventDefault();
             this.do_action({
                 name: _t("To Commission"),
                 type: 'ir.actions.act_window',
                 res_model: 'insurance.policy',
                 view_mode: 'tree,form',
                 views: [[false, 'list'], [false, 'form']],
                 domain: [['invoice_status', '=', 'to_invoice']],
                 context: {default_invoice_status: 'to_invoice'},
                 target: 'current'
             });
         },

        view_company: function (ev) {
            var self = this;
            var company = $(ev.target).data().id;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                res_model: 'insurance.policy',
                name: _t('Insurance Policies'),
                views: [[false, 'list'], [false, 'form']],
                view_mode: 'tree,form',
                type: 'ir.actions.act_window',
                domain: [['insurance_company_id', '=', company]],
            });
        },

        view_detail: function (ev) {
            var self = this;
            var detail = $(ev.target).data().id;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                res_model: 'insurance.policy',
                name: _t('Insurance Policies'),
                res_id: detail,
                views: [[false, 'form']],
                view_mode: 'form',
                view_type: 'form',
                type: 'ir.actions.act_window',
                domain: [['id', '=', detail]],
            });
        },


        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template){
                    self.$('.o_pos_dashboard').append(QWeb.render(template,
                    {
                    widget: self, policy_count_count_dict:self.policy_count_count_dict,
                    widget: self, agent_list:self.agent_list,
                    widget: self, category_list:self.category_list,
                    widget: self, invoice_status_data_dct:self.invoice_status_data_dct,
                    widget: self, company_list:self.company_list,
                    widget: self, insurance_list:self.insurance_list,
                    widget: self, claimed_list:self.claimed_list,

                    }
                ));
            });
        },
    });
    core.action_registry.add('insurance_dashboard_tag', InsuranceDashboard);
    return;
});