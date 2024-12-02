odoo.define("reddot_dashboard_crm.dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var stage_domain;
        var session = require('web.session');

    var rpc = require('web.rpc');
    var DashBoardCrm = AbstractAction.extend({
        contentTemplate: 'DashBoardCrm',
         events: {
             "click .all_leads": "open_all_lead",
             "click .all_revenue": "open_all_lead",
             "click .my_leads": "open_my_lead",

         },

         init: function(parent, context) {
             this._super(parent, context);
             this.dashboards_templates = ['CRMDashboard'];
         },


        willStart: function(){
            var self = this;
            return this._super()
            .then(function() {
                var leads =  self.lead_data_count();
            });
        },


          open_all_lead: function(ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            rpc.query({
                model: "crm.lead",
                method: "click_open_all_lead",
                kwargs: {  },
            }).then(function(result) {
                self.do_action(result);
            })
        },



        open_my_lead: function (ev) {
        var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            rpc.query({
                model: "crm.lead",
                method: "click_open_my_lead",
                kwargs: {  },
            }).then(function(result) {
                self.do_action(result);
            })
        },


//            open_my_lead: function (ev) {
//            var self = this;
//            var login_user = session.uid
//            var isAdmin = session.user_context.allowed_groups.indexOf('base.group_system') !== -1;
//            ev.stopPropagation();
//            ev.preventDefault();
//            var domain = []
//                var indexOf;
//             if (!isAdmin) {
//               domain += ['user_id', '=', login_user]
//             }
//             console.log("_____________________  domnaaa",domain)
//                  this.do_action({
//                name: _t("My Lead"),
//                type: 'ir.actions.act_window',
//                res_model: 'crm.lead',
//                view_mode: 'tree,form',
//                views: [[false, 'list'], [false, 'form']],
//                domain: [domain],
//                target: 'current'
//            });
//
//
//
//        },


        lead_data_count: function() {
            var self = this;
            var fields;
            var def1 = self._rpc({
               model: 'crm.lead',
               method: 'get_lead_count',
               args: []
            }).then(function(result) {
                $('#total_lead_count').empty()
                $('#total_lead_revenue').empty()
                $('#my_lead_count').empty()
                $('#my_lead_revenue').empty()
                self.$('#total_lead_count').append('<span>'+ result.all_leads +'</span>');
                self.$('#total_lead_revenue').append('<span>'+ result.revenue_sum +'</span>');
                self.$('#my_lead_count').append('<span>'+ result.my_leads +'</span>');
                self.$('#my_lead_revenue').append('<span>'+ result.my_revenue_sum +'</span>');
            });
            return def1
        },

//        lead_by_status_chart: function() {
//            var self = this;
//            rpc.query({
//                model: 'crm.lead',
//                method: 'status_wise_leads',
//                kwargs: { },
//            }).then(function (result) {
//                var ctx = self.$el.find('#lead_by_status')[0].getContext('2d');
//                new Chart(ctx, {
//                    type: 'doughnut',
//                    data: {
//                        labels: result['status_type_label'],
//                        datasets: [{
//                            data: result['status_type_value'],
//                            backgroundColor: result['backgroundColor']
//                        }]
//                    },
//                    options: {
//                        title: {
//                            display: true,
//                            text: 'Status Wise Lead'
//                        },
//                    }
//                });
//            });
//        },



        start: function() {
            var self = this;
            self.render_dashboards();
            self.renderChart();
            this.set("title", 'DashBoardCrm');
            return this._super().then(function() {
            });
        },
        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template){
                self.$('.o_crm_dashboard').append(QWeb.render(template,
                    {
                    }
                ));
            });
        },


        renderChart: function () {
            var self = this;
//             self.lead_by_status_chart();

            },
        });
    core.action_registry.add('crm_dashboard_tag', DashBoardCrm);
    return;
});