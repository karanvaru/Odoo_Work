odoo.define("ki_dashboard_crm.crm_dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var stage_domain;
    var rpc = require('web.rpc');
    var CrmDashBoard = AbstractAction.extend({
        contentTemplate: 'CrmDashBoard',
         events: {
            "click .crm_new_stage": "crm_new_stage",
            "click .crm_qualified_stage": "crm_qualified_stage",
            "click .crm_proposition_stage": "crm_proposition_stage",
            "click .crm_won_stage": "crm_won_stage",
            "click #top_10_crm_record": "top_10_crm_between_date",
            'click #top_crm_team_on_graph': 'top_crm_team_on_graph',
            'click #customer_on_graph_crm': 'customer_on_graph_crm',
        },
        top_crm_team_on_graph: function(ev) {
            var time_interval = $('#top_crm_team_on_graph').val();
            this.crm_team_graph(time_interval);
        },

        customer_on_graph_crm: function(ev) {
            var time_interval = $('#customer_on_graph_crm').val();
            this.crm_customer_graph(time_interval);
        },

        renderElement: function(ev) {

            var self = this;
            $.when(this._super())
                .then(function(ev) {
                 rpc.query({
                    model: "purchase.order",
                    method: "get_year_finience",
                }).then(function(result) {
                    $('#customer_from_date').val(result['start_date']);
                    $('#customer_to_date').val(result['end_date']);
//                    $('#start_date_class').val('2024-04-01')
//                    $('#end_date_class').val('2025-03-31')
                })


                    self.render_graphs();
            })
        },

        render_graphs: function(){
            var self = this;
            self.crm_team_graph();
            self.crm_customer_graph();
        },
        crm_team_graph: function(time_interval) {
            var self = this;
            this._rpc({
                model: 'crm.lead',
                method: 'crm_team_graph',
                kwargs: [{
                    'time_interval':time_interval,
                }],
            }).then(function(result){

              $('#operation_crm_team_graph_id').empty();
                    var due_count = 0;
                    var amount;
                    $('#operation_crm_team_graph_id').empty();
                    _.forEach(result, function(x) {

                        $('#operation_crm_team_graph_id').show();
                        due_count++;
                        $('#operation_crm_team_graph_id').append('<li><div>' + x.name + '</div>' + '<div data-user-id="' + x.name + '">' + x.value + '</div>' + '</li>');

                    });
                })
        },

        crm_customer_graph: function(time_interval) {
            var self = this;
            this._rpc({
                model: 'crm.lead',
                method: 'crm_customer_graph',
                kwargs: [{
                    'time_interval':time_interval,
                }],
            })
            .then(function(result){
              $('#operation_customer_on_graph_crm_id').empty();
                    var due_count = 0;
                    var amount;
                    $('#operation_customer_on_graph_crm_id').empty();
                    _.forEach(result, function(x) {
                        $('#operation_customer_on_graph_crm_id').show();
                        due_count++;
                        $('#operation_customer_on_graph_crm_id').append('<li><div>' + x.name + '</div>' + '<div data-user-id="' + x.name + '">' + x.value + '</div>' + '</li>');

                    });
                })
        },

        crm_new_stage: function (ev) {
            var self = this;
            var stage = $(ev.currentTarget).attr('data-id');
            var count =  this.$(ev.currentTarget);
            var customer_from_date = $('#customer_from_date').val();
            var customer_to_date = $('#customer_to_date').val();
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t(stage),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['stage_id.name', '=', stage],['create_date', '>=', customer_from_date],['create_date', '>=', customer_from_date]],
                context: {default_stage_id: stage},
                target: 'current'
            });
        },
        top_10_crm_between_date: function (ev) {
            var self = this;
            var customer_from_date = $('#customer_from_date').val();
            var customer_to_date = $('#customer_to_date').val();
            var def1 = self._rpc({
                model: 'crm.lead',
                method: 'top_10_crm_filter',
                kwargs: [{
                    'customer_from_date':customer_from_date,
                    'customer_to_date':customer_to_date
                }],
                }).then(function(result) {
                    $('#top_10_crm_filter_customer').empty();
                    $('#top_10_crm_team').empty();
                    $('#crm_top_10_sale_team_by_amount').empty();
                    $('#top_10_crm_sales_team_vals').empty();
                    $('.top_list_class').empty();
                    $('.top_10_crm_customer_vals').empty();
                    $('#operation_crm_team_graph_id').empty();
                    $('#operation_customer_on_graph_crm_id').empty();
                    $('#state_display').empty();
                    for (var c in result[0]) {
                        $('#top_10_crm_filter_customer').show();
                        for (var x in result[0][c]) {
                            $('#top_10_crm_filter_customer').append(
                            '<div class="row top_10_filter" style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4 top_10_details" style="text-align:right;"><span>' + result[3] +' '+ result[0][c][x] + '</span>' +'</div></div>');
                        }
                    };
                    for (var c in result[1]) {
                        $('#top_10_crm_team').show();
                        for (var x in result[1][c]) {

                            $('#top_10_crm_team').append(
                            '<div class="row top_10_filter"  style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4 top_10_details" style="text-align:right;"><span>' + result[1][c][x]  + '</span>' +'</div></div>');
                        }
                    };
                    for (var c in result[2]) {
                        $('#crm_top_10_sale_team_by_amount').show();
                        for (var x in result[2][c]) {
                            $('#crm_top_10_sale_team_by_amount').append(
                            '<div class="row top_10_filter"  style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4  top_10_details" style="text-align:right;"><span>'+ result[3] +''+ result[2][c][x] + '</span>' +'</div></div>');
                        }
                    };

                    for (var x in result[4]) {
                        $('#operation_crm_team_graph_id').show();
                        $('#operation_crm_team_graph_id').append('<li><div><span>' + result[4][x]['name'] + '</span></div>' + '<div data-user-id="' +result[4][x]['name']+ '">' + result[4][x]['value'] + '</div>' + '</li>');
                    };

                    for (var x in result[5]) {
                        $('#operation_customer_on_graph_crm_id').show();
                        $('#operation_customer_on_graph_crm_id').append('<li><div><span>' + result[5][x]['name'] + '</span></div>' + '<div data-user-id="' +result[5][x]['name']+ '">' + result[5][x]['value'] + '</div>' + '</li>');
                    };

                    for (var x in result[6]) {
                      $('#state_display').show();
                        var data = $('#state_display').append(
                         '<div class="col-md crm_new_stage" data-id= '+ x + '>' +
                        '<div class="tile wide invoice box-1"><div class="headers"><div class="main-title"><span>'+ x + '</span></div>' +
                        '<div id="monthly_invoice"><div class="left"><span>Count</span><div class="count"> <span>' + result[6][x][1] +
                         '</span> </div> </div> <div class="right crm_new_stage" id="crm_new_stage_id"  data-id='
                         + x + ' style="text-align:center"> <span>Amount</span>  <div class="count"> <span>' + result[6][x][0] +
                          '</span></div></div> </div></div></div></div>'
                    );
                    }


                });
            },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['CrmLeadBarGraph'];
        },

        willStart: function(){
            var self = this;
            return this._super()
            .then(function() {
                var def1 = self._rpc({
                    model: 'crm.lead',
                    method: 'get_crm_state',
                }).then(function(result) {
                    self.stage_dict = result
                });
                var def2 = self._rpc({
                    model: 'crm.lead',
                    method: 'crm_top_10_customer',
                }).then(function(result) {
                    self.top_10_crm_customer = result
                });
                var def3 = self._rpc({
                        model: 'crm.lead',
                        method: 'top_10_sales_team',
                }).then(function(result) {
                    self.top_10_sales_team = result
                });
                var def4 = self._rpc({
                        model: 'crm.lead',
                        method: 'top_10_sales_team_by_amount',
                })
                .then(function(result) {
                    self.top_10_team_by_amount = result[0]
                    self.currency = result[1]
                });
                return $.when(def1,def2,def3,def4);
            });
        },
        start: function() {
            var self = this;
            this.set("title", 'CrmDashBoard');
            return this._super().then(function() {
                self.render_dashboards();
            });
        },
        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template){
                self.$('.o_pos_dashboard').append(QWeb.render(template,
                    {
                        widget: self,stage_dict:self.stage_dict,
                        widget: self, top_10_crm_customer:self.top_10_crm_customer,
                        widget: self, top_10_sales_team:self.top_10_sales_team,
                        widget: self, top_10_team_by_amount:self.top_10_team_by_amount,
                        widget: self, currency:self.currency,
                    }
                ));
            });
        },
  });
    core.action_registry.add('crm_dashboard_tag', CrmDashBoard);
    return;
});
