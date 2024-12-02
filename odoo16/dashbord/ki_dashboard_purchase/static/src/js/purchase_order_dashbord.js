odoo.define("ki_dashboard.purchase_dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var stage_domain;
    var PurchaseDashboard = AbstractAction.extend({
        contentTemplate: 'PurchaseDashboard',
         events: {
            "click .inbox_draft": "draft_inbox",
            "click .inbox_done": "done_inbox",
            "click .inbox_sale": "sale_inbox",
            "click .inbox_sent": "sent_inbox",
            "click #top_10_between_date_purchase": "top_10_between_date",
            'click #top_purchase_product_value': 'top_purchase_product_value',
            'click #customer_on_graph_purchase': 'customer_on_graph_purchase',
        },


         top_purchase_product_value: function(ev) {
            var time_interval = $('#top_purchase_product_value').val();
            this.purchase_product_graph(time_interval);
         },

           customer_on_graph_purchase: function(ev) {
            var time_interval = $('#customer_on_graph_purchase').val();
            this.customer_graph_purchase(time_interval);
         },

        renderElement: function(ev) {
        var self = this;
        $.when(this._super())
            .then(function(ev) {
                self.render_graphs();
            })
        },

        render_graphs: function(){
            var self = this;
            self.purchase_product_graph();
            self.customer_graph_purchase();
        },
        purchase_product_graph: function(time_interval) {
            var self = this;
            this._rpc({
                model: 'purchase.order',
                method: 'purchase_product_graph',
                kwargs: [{
                    'time_interval':time_interval,
            }],
            })
            .then(function(result) {
                var ctx = self.$("#operation_product_purchase");
                if(window.PurchaseProduct != undefined){
                    window.PurchaseProduct.destroy();
                }
                window.PurchaseProduct = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: result[0],
                        datasets :result[1],
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                id: 'y-axis-0',
                                ticks: {
                                    beginAtZero:true,
                                }
                            }],
                        },
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                });
            });
        },

        customer_graph_purchase: function(time_interval) {
            var self = this;
            this._rpc({
                model: 'purchase.order',
                method: 'customer_on_graph_purchase',
                    kwargs: [{
                    'time_interval':time_interval,
            }],
            })
            .then(function(result) {
                var ctx = self.$("#operation_customer_on_graph_purchase");
                if(window.SaleCustomer != undefined){
                    window.SaleCustomer.destroy();
                }
                window.SaleCustomer = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: result[0],
                        datasets :result[1],
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                id: 'y-axis-0',
                                ticks: {
                                    beginAtZero:true,
                                }
                            }],
                        },
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                });
            });
         },
         draft_inbox: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Draft"),
                type: 'ir.actions.act_window',
                res_model: 'purchase.order',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'draft']],
                context: {default_state: 'draft'},
                target: 'current'
            });
        },
        done_inbox: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Done"),
                type: 'ir.actions.act_window',
                res_model: 'purchase.order',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'done']],
                context: {default_state: 'done'},
                target: 'current'
            });
        },
        sale_inbox: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Purchase"),
                type: 'ir.actions.act_window',
                res_model: 'purchase.order',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'purchase']],
                context: {default_state: 'purchase'},
                target: 'current'
            });
        },
        sent_inbox: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Sent"),
                type: 'ir.actions.act_window',
                res_model: 'purchase.order',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'sent']],
                context: {default_state: 'sent'},
                target: 'current'
            });
        },

        top_10_between_date: function (ev) {
            var self = this;
            var customer_from_date = $('#customer_from_date').val();
            var customer_to_date = $('#customer_to_date').val();
             var def1 = self._rpc({
                model: 'purchase.order',
                method: 'top_10_by_filter',
                kwargs: [{
                    'customer_from_date':customer_from_date,
                    'customer_to_date':customer_to_date
                }],
                }).then(function(result) {
                     $('#top_10_vendor_this_month').empty();
                    $('#purchase_top_10_product').empty();
                    $('#purchase_top_10_product_by_qty').empty();
                    $('.top_10_purchase_product_by_qty_vals').empty();
                    $('.top_10_purchase_product_val').empty();
                    $('.top_10_purchase_customer_name').empty();
                    for (var c in result[0]) {
                        $('#top_10_vendor_this_month').show();
                        for (var x in result[0][c]) {
                            $('#top_10_vendor_this_month').append(
                            '<div class="row top_10_row" style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4 top_10_details" style="text-align:right;"><span>' + result[3] + ' ' + result[0][c][x]  +'</span>' +'</div></div>');
                        }
                    };
                    for (var c in result[1]) {
                        $('#purchase_top_10_product').show();
                        for (var x in result[1][c]) {
                            $('#purchase_top_10_product').append(
                            '<div class="row top_10_row" style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4 top_10_details" style="text-align:right;"><span>' + result[3] + ' ' + result[1][c][x]  + '</span>' +'</div></div>');
                        }
                    };


                       for (var c in result[2]) {
                        $('#purchase_top_10_product_by_qty').show();
                        for (var x in result[2][c]) {
                            $('#purchase_top_10_product_by_qty').append(
                            '<div class="row top_10_row" style="margin-bottom:0px;"><div class="col-8 top_10_details"><span>' +x + '</div>'
                            + '</span>' +'<div class="col-4 top_10_details" style="text-align:right;"><span>' + result[2][c][x] + '  Units' + '</span>' +'</div></div>');
                        }
                    };

                });
        },

         init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['ProductPurchaseBarGraph'];
        },



        willStart: function(){
            var self = this;
            return this._super()
            .then(function() {
                var def1 = self._rpc({
                        model: 'purchase.order',
                        method: 'get_all_state_count',
                }).then(function(result) {
                    self.state_count_dict = result
                });
             var def2 = self._rpc({
                        model: 'purchase.order',
                        method: 'top_10_customer',
                }).then(function(result) {
                    self.top_10 = result
                });
                var def3 = self._rpc({
                        model: 'purchase.order',
                        method: 'top_10_product',
                }).then(function(result) {
                    self.top_10_entities = result
                });
                var def4 = self._rpc({
                        model: 'purchase.order',
                        method: 'top_10_product_by_qty',
                })
                .then(function(result) {
                    self.top_10_product_qty = result
                });
                return $.when(def1,def2,def3,def4);
            });
        },
          start: function() {
            var self = this;
            this.set("title", 'PurchaseDashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_graphs();
            });
        },
         render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template){
                    self.$('.o_pos_dashboard').append(QWeb.render(template,
                    {
                    widget: self, state_count_dict:self.state_count_dict,
                    widget: self, top_10_product_qty:self.top_10_product_qty,
                    widget: self, top_10:self.top_10,
                    widget: self, top_10_entities:self.top_10_entities,
                    }
                ));
            });
        },

  });
    core.action_registry.add('purchase_dashboard_tag', PurchaseDashboard);
    return;
});