odoo.define('ki_accounting_dashboard_extends.AccountingDashboards', function(require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    const AccountingDashboard = require('base_accounting_kit.AccountingDashboard');
    const { loadBundle } = require("@web/core/assets");
    var self = this;
    var currency;
    AccountingDashboard.include({
        contentTemplate: 'Invoicedashboard',
            events: _.extend({}, AccountingDashboard.prototype.events, {
                'click .invoice_dashboard': 'onclick_dashboard',
                'click #invoice_first_quarter': 'onclick_invoice_first_quarter',
                'click #invoice_second_quarter': 'onclick_invoice_second_quarter',
                'click #invoice_third_quarter': 'onclick_invoice_third_quarter',
                'click #invoice_last_quarter': 'onclick_invoice_last_quarter',
                'change #invoice_values': function(e) {
                    e.stopPropagation();
                    var $target = $(e.target);
                    var value = $target.val();

                    if (value == 'first_quarter'){
                        this.onclick_invoice_first_quarter(this.$('#invoice_values').val());
                    }
                    else if (value == 'second_quarter'){
                        this.onclick_invoice_second_quarter(this.$('#invoice_values').val());
                    }
                    else if (value == 'third_quarter'){
                        this.onclick_invoice_third_quarter(this.$('#invoice_values').val());
                    }
                    else if (value == 'last_quarter'){
                        this.onclick_invoice_last_quarter(this.$('#invoice_values').val());
                    }
                },

                'click #total_customer_invoice_paid_q1': 'invoice_q1_paid',
                'click #total_customer_invoice_paid_q2': 'invoice_q2_paid',
                'click #total_customer_invoice_paid_q3': 'invoice_q3_paid',
                'click #total_customer_invoice_paid_q4': 'invoice_q4_paid',
                'click #total_customer_invoice_q1': 'invoice_q1',
                'click #total_customer_invoice_q2': 'invoice_q2',
                'click #total_customer_invoice_q3': 'invoice_q3',
                'click #total_customer_invoice_q4': 'invoice_q4',
                'click #total_supplier_invoice_paid_q1': 'bill_q1_paid',
                'click #total_supplier_invoice_paid_q2': 'bill_q2_paid',
                'click #total_supplier_invoice_paid_q3': 'bill_q3_paid',
                'click #total_supplier_invoice_paid_q4': 'bill_q4_paid',
                'click #total_supplier_invoice_q1': 'bill_q1',
                'click #total_supplier_invoice_q2': 'bill_q2',
                'click #total_supplier_invoice_q3': 'bill_q3',
                'click #total_supplier_invoice_q4': 'bill_q4',
                'click #date_apply': 'date_apply',
				'click .salary-line': 'click_salary_line',
				'click .cue_bridge': 'click_cue_bridge',
				'click .cue_bridge_max': 'click_cue_bridge_max',
				'click .cue_bridge_plus': 'click_cue_bridge_plus',
				'click .total_class': 'total_class_cue_bridge',
				'click .total_class_cue_max': 'total_class_cue_max',
				'click .cue_bridge_plush_total': 'cue_bridge_plush_total',

				
            }),

        renderElement: function(ev) {
            console.log("___________________   firsttt")
            var self = this;
                        var posted = false;

            $.when(this._super())
            .then(function(ev) {

//            var start_date = $('#start_date').val();
//			var end_date = $('#end_date').val();

			        rpc.query({
                    model: "account.move",
                    method: "get_year",
                }).then(function(result) {
//                    $('#start_date').val(result['start_date']);
//                    $('#end_date').val(result['end_date']);
                    $('#start_date').val('2024-04-01')
                    $('#end_date').val('2025-03-31')
                })

//                var start_date = result['start_date'];
//                var end_date =result['end_date'];
//                console.log("____________   start_date",start_date)
//                    console.log("____________   end_date",end_date)
                rpc.query({
                    model: "account.move",
                    method: "get_currency",
                }).then(function(result) {
                    currency = result;
                })
               self.date_apply_custom();
			$('#salary_details_ul').empty()
            rpc.query({
                model: "account.move",
                method: "get_salary_lines",
                args: [start_date , end_date]
            })
            .then(function(result) {
                for (var k = 0; k < result.length; k++) {
                   var  amount = self.format_currency(currency, result[k]['salary']);
					var name = result[k]['name']

					var dept_id = result[k]['dept_id']

                    $('#salary_details_ul').append('<li><div  class="salary-line"  val="' + dept_id + '"id="' + dept_id + '">' + name + '</div><div>' + amount + '</div></li>');

				}
            });

			//CUE BRIDGE
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
	
	
				var das_table = $('#cue_bridge_ul_table')
				das_table.empty()
                var qty_sum = 0
                var amount_sum = 0

                for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="total_class" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')

                	var title_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
               	das_table.append(title_line)
               				    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']

					var id = result[k]['id']
//					 qty_sum += qty;
//					 amount_sum += amount;
//                    qty_sum += result[k]['qty'];
//					amount_sum += result[k]['amount'];
					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}

            });
//                      $('.cue_bridge').on("click", function() {
//                  var start_date = $('#start_date').val();
//			var end_date = $('#end_date').val();
//
//			var id = ev.currentTarget.id
//            rpc.query({
//                model: "account.move",
//                method: "click_cue_bridge",
//                args: [id, start_date, end_date],
//            }).then(function(result) {
//                self.do_action(result);
//            })
//                        });


			//CUE BRIDGE MAX
			$('#cue_bridge_max_ul').empty()
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_max_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
				var das_table = $('#cue_bridge_max_ul_table')
				das_table.empty()
                  var qty_sum = 0
                var amount_sum = 0
                for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="total_class_cue_max" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')

				var title_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
				das_table.append(title_line)
							    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                   var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']
					var id = result[k]['id']

					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge_max"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}
            });


			//CUE BRIDGE PLUS
			$('#cue_bridge_plus_ul').empty()
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_plus_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
				var das_table = $('#cue_bridge_plus_ul_table')
				das_table.empty()

				 var qty_sum = 0
                var amount_sum = 0

 for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="cue_bridge_plush_total" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')


				var title_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer</td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
				das_table.append(title_line)
							    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                   var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']
					var id = result[k]['id']

					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge_plus"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}
            });



/*            rpc.query({
                model: "account.move",
                method: "get_product_counts",
                args: [start_date , end_date]
            })
            .then(function(result) {
	
				var data_line = result
				var das_table = $('#product_lines')
				das_table.empty()

                for (var k = 0; k < data_line.length; k++) {
					if (k == 0){
				    	var title_line = $('<tr style="background-color:#95cce5;font-weight: bold;border:1px solid black;padding-top:0px;padding-bottom:0px;"/>');
					} else {
						var title_line = $('<tr style="border-bottom:1px solid black;padding-top:0px;padding-bottom:0px;"/>');
					}
           			for (var l = 0; l < data_line[k].length; l++) {
						if (k == 0){
							title_line.append('<td style="padding:0.75rem;border:1px solid black;" class="text-center">' + data_line[k][l] + '</td>')
						} else {
							
							if (l == 0){
								title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;border:1px solid black;">' + data_line[k][l] + '</td>')
							} else {
								title_line.append('<td style="border:1px solid black;text-align: right;padding-right:5px;">' + data_line[k][l] + '</td>')
							}

						}
					}
					das_table.append(title_line)
				}
            })




*/
                  rpc.query({

                    model: "account.move",
                    method: "profit_income_this_year",
                    args: [posted],
                }).then(function(result) {
                    var net_profit = true
                    if (result[1] == undefined) {
                        result[1] = 0;
                        if ((result[0]) > (result[1])) {
                            net_profit = result[1] - result[0]
                        }
                    }
                    if (result[0] == undefined) {
                        result[0] = 0;
                    }
                    if ((-result[1]) > (result[0])) {
                        net_profit = -result[1] - result[0]
                    } else if ((result[1]) > (result[0])) {
                        net_profit = -result[1] - result[0]
                    } else {
                        net_profit = -result[1] - result[0]
                    }
                    var profit_this_year = net_profit;
                    if (profit_this_year) {
                    console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        var net_profit_this_year = profit_this_year;
                        net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                        $('#net_profit_current_year').empty();
                        //                                $('#net_profit_this_year').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_year + '</span>')
                        $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title"></div>')
                    } else {
                        var net_profit_this_year = profit_this_year;
                        net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                        $('#net_profit_current_year').empty();
                        //$('#net_profit_this_year').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_year + '</span>')
                        $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title"></div>')
                    }
                })
                rpc.query({
                    model: "account.move",
                    method: "month_income_this_year",
                    args: [posted],
                }).then(function(result) {
                    var incomes_this_year = result[0].debit - result[0].credit;
                    if (incomes_this_year) {
                        incomes_this_year = -incomes_this_year;
                        incomes_this_year = self.format_currency(currency, incomes_this_year);
                        $('#total_incomes_this_year').empty();
                        $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title"></div>')
                    } else {
                        incomes_this_year = -incomes_this_year;
                        incomes_this_year = self.format_currency(currency, incomes_this_year);
                        $('#total_incomes_this_year').empty();
                        $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title"></div>')
                    }
                })
                rpc.query({
                    model: "account.move",
                    method: "month_expense_this_year",
                    args: [posted],
                }).then(function(result) {
                    var expense_this_year = result[0].debit - result[0].credit;
                    if (expense_this_year) {
                        var expenses_this_year_ = expense_this_year;
                        expenses_this_year_ = self.format_currency(currency, expenses_this_year_);
                        $('#total_expense_this_year').empty();
                        $('#total_expense_this_year').append('<span >' + expenses_this_year_ + '</span><div class="title"></div>')
                    } else {
                        var expenses_this_year_ = expense_this_year;
                        expenses_this_year_ = self.format_currency(currency, expenses_this_year_);
                        $('#total_expense_this_year').empty();
                        $('#total_expense_this_year').append('<span >' + expenses_this_year_ + '</span><div class="title"></div>')
                    }
                })


})
		},

		click_salary_line: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "click_salary_lines",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },

		click_cue_bridge: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "click_cue_bridge",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },

		click_cue_bridge_max: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "click_cue_bridge_max",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },

		click_cue_bridge_plus: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "click_cue_bridge_plus",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },

        total_class_cue_bridge: function(ev) {
            console.log("____________________________________________________")
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "click_cue_bridge_total",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },


        total_class_cue_max: function(ev) {
            console.log("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLl")
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "total_click_cue_bridge_max",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },

        cue_bridge_plush_total: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

			var id = ev.currentTarget.id
            rpc.query({
                model: "account.move",
                method: "total_click_cue_bridge_plus",
                args: [id, start_date, end_date],
            }).then(function(result) {
                self.do_action(result);
            })
        },


        profit_income_month: function(ev) {
            var posted = false;
            var self = this;
            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

            rpc.query({
                model: "account.move",
                method: "click_profit_income_month",
                args: [posted, start_date, end_date],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move.line',
                    name: _t('Net Profit or Loss'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        total_income_month: function(ev) {
            var posted = false;
            var self = this;

            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

            rpc.query({
                model: "account.move",
                method: "click_total_income_month",
                args: [posted, start_date, end_date],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move.line',
                    name: _t('Total Income'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        expense_month: function(ev) {
            var posted = false;
            var self = this;

            var start_date = $('#start_date').val();
			var end_date = $('#end_date').val();

            rpc.query({
                model: "account.move",
                method: "click_expense_month",
                args: [posted, start_date, end_date],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move.line',
                    name: _t('Total Expenses'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

         date_apply: function(ev) {
                var self = this;
               self.date_apply_custom();
             },
        date_apply_custom: function(ev) {
			var self = this;
			var startDate = "2024-04-01";
            var endDate   = "2025-03-31";

//            var start_date = $('#start_date').val();
//			var end_date = $('#end_date').val();
//			    var start_date = $('#start_date').val('2024-04-01')
//                var end_date = $('#end_date').val('2025-03-31')
			  console.log("+!!!!!!!!!!!!!!!!!!   222  start_date",start_date)
            console.log("+!!!!!!!!!!!!!!!!!! 22  end_date",end_date)
			if (!start_date){
			    alert('Please Select Start Date')
			    return
			}
			if (!end_date){
			    alert('Please Select End Date')
			    return
			}

                /*$('#toggle-two').bootstrapToggle({
                    on: 'View All Entries',
                    off: 'View Posted Entries'
                });*/
                var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
                rpc.query({
                    model: "account.move",
                    method: "get_currency",
                }).then(function(result) {
                    currency = result;
                })
				console.log("ddddddddddd")
				
				
				$('#salary_details_ul').empty()
                rpc.query({
                    model: "account.move",
                    method: "get_salary_lines",
                    args: [start_date , end_date]
                })
                .then(function(result) {
	                for (var k = 0; k < result.length; k++) {
                       var  amount = self.format_currency(currency, result[k]['salary']);
						var name = result[k]['name']

						var dept_id = result[k]['dept_id']

                        $('#salary_details_ul').append('<li><div  class="salary-line"  val="' + dept_id + '"id="' + dept_id + '">' + name + '</div><div>' + amount + '</div></li>');

					}
                })





			//CUE BRIDGE
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
	
	
				var das_table = $('#cue_bridge_ul_table')
				das_table.empty()

				 var qty_sum = 0
                var amount_sum = 0

                 for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="total_class" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')


				var title_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
				das_table.append(title_line)
							    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                   var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']
					var id = result[k]['id']

					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}
            });


			//CUE BRIDGE MAX
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_max_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
				var das_table = $('#cue_bridge_max_ul_table')
				das_table.empty()
                 var qty_sum = 0
                var amount_sum = 0

            for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="total_class_cue_max" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')


				var title_line = $('<tr  style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
				das_table.append(title_line)
							    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                   var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']
					var id = result[k]['id']

					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge_max"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}
            });


			//CUE BRIDGE PLUS
            rpc.query({
                model: "account.move",
                method: "get_cue_bridge_plus_ul",
                args: [start_date , end_date]
            })
            .then(function(result) {
				var das_table = $('#cue_bridge_plus_ul_table')
				das_table.empty()

				 var qty_sum = 0
                var amount_sum = 0

                for (var k = 0; k < result.length; k++) {
                 qty_sum +=  result[k]['qty'];
		            amount_sum += result[k]['amount'];
                		}
                var title_line_total = $('<tr class="cue_bridge_plush_total" style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#e6889d;font-weight: bold;"/>');
				title_line_total.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:4px;padding-bottom:2px;"> Total </td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">'+ qty_sum+  '</td>')
				title_line_total.append('<td style="text-align:right;padding-right:5px;padding-top:4px;padding-bottom:2px;">' + amount_sum.toFixed(2)+ '</td>')

				var title_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;background-color:#95cce5;font-weight: bold;"/>');
				title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;"> Customer </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Qty </td>')
				title_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;"> Amount </td>')
				das_table.append(title_line)
							    das_table.append(title_line_total)

                for (var k = 0; k < result.length; k++) {
	
	                   var  amount = self.format_currency(currency, result[k]['amount']);
					var name = result[k]['name']
					var qty = result[k]['qty']
					var id = result[k]['id']

					var row_line = $('<tr style="border-bottom:1px solid #F2F2F2;padding-top:0px;padding-bottom:0px;color: #455e7b !important;"' + 'class="cue_bridge_plus"' + 'id=' + id + '/>');
					row_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;padding-top:5px;padding-bottom:5px;">' + name + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + qty + '</td>')
					row_line.append('<td style="text-align:right;padding-right:5px;padding-top:5px;padding-bottom:5px;">' + amount + '</td>')

					das_table.append(row_line)
				}
            });



                var arg = 'this_month';
                rpc.query({
                    model: 'account.move',
                    method: 'get_overdues_this_month_and_year_range',
                    args: [posted, arg, start_date, end_date],
                }).then(function(result) {
                    $('#aged_receivable').empty();
                    var due_count = 0;
                    var amount;
                    $('#aged_receivable').empty();
                    _.forEach(result, function(x) {
                        $('#aged_receivable').show();
                        due_count++;
                        amount = self.format_currency(currency, x.amount);
//						$('#aged_receivable').empty();
                        $('#aged_receivable').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.due_partner + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');
//                        $('#line_' + x.parent).on("click", function() {
//                            self.do_action({
//                                res_model: 'account.move',
//                                name: _t('Invoice'),
//                                views: [
//                                    [false, 'form']
//                                ],
//                                type: 'ir.actions.act_window',
//                                res_id: x.parent,
//                            });
//                        });
                    });
                })



//                 {
//                    console.log("________________________  result ",result)
//                    // Doughnut Chart
//                    $(document).ready(function() {
//                        var options = {
//                            // legend: false,
//                            responsive: true,
//                            legend: {
//                                position: 'bottom'
//                            }
//                        };
//                        if (window.donut != undefined)
//                            window.donut.destroy();
//                        window.donut = new Chart($("#canvas1"), {
//                            type: 'doughnut',
//                            tooltipFillColor: "rgba(51, 51, 51, 0.55)",
//                            data: {
//                                labels: result.due_partner,
//                                datasets: [{
//                                    data: result.due_amount,
//                                    backgroundColor: [
//                                        '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                        '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                        '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                        ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                        '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                        '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                        '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                        '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                        '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                        '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                    ],
//                                    hoverBackgroundColor: [
//                                        '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                        '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                        '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                        ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                        '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                        '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                        '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                        '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                        '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                        '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                    ]
//                                }]
//                            },
//                            options: {
//                                responsive: false
//                            }
//                        });
//                    });
//                })


                rpc.query({
                    model: "account.move",
                    method: "get_total_invoice_current_month",
                    args: [posted, start_date, end_date],
                }).then(function(result) {
                    $('#total_supplier_invoice_paid').hide();
                    $('#total_supplier_invoice').hide();
                    $('#total_customer_invoice_paid').hide();
                    $('#total_customer_invoice').hide();
                    $('#tot_invoice').hide();
                    $('#tot_supplier_inv').hide();

                    $('#total_supplier_invoice_paid_current_month').empty();
                    $('#total_supplier_invoice_current_month').empty();
                    $('#total_customer_invoice_paid_current_month').empty();
                    $('#total_customer_invoice_current_month').empty();
                    $('#tot_invoice_current_month').empty();
                    $('#tot_supplier_inv_current_month').empty();

                    $('#total_supplier_invoice_paid_current_year').hide();
                    $('#total_supplier_invoice_current_year').hide();
                    $('#total_customer_invoice_paid_current_year').hide();
                    $('#total_customer_invoice_current_year').hide();
                    $('#tot_invoice_current_year').hide();
                    $('#tot_supplier_inv_current_year').hide();

                    $('#total_supplier_invoice_paid_current_month').show();
                    $('#total_supplier_invoice_current_month').show();
                    $('#total_customer_invoice_paid_current_month').show();
                    $('#total_customer_invoice_current_month').show();
                    $('#tot_invoice_current_month').show();
                    $('#tot_supplier_inv_current_month').show();

                    var tot_invoice_current_month = result[0][0]
                    var tot_credit_current_month = result[1][0]
                    var tot_supplier_inv_current_month = result[2][0]
                    var tot_supplier_refund_current_month = result[3][0]
                    var tot_customer_invoice_paid_current_month = result[4][0]
                    var tot_supplier_invoice_paid_current_month = result[5][0]
                    var tot_customer_credit_paid_current_month = result[6][0]
                    var tot_supplier_refund_paid_current_month = result[7][0]
                    var customer_invoice_total_current_month = (tot_invoice_current_month - tot_credit_current_month).toFixed(2)
                    var customer_invoice_paid_current_month = (tot_customer_invoice_paid_current_month - tot_customer_credit_paid_current_month).toFixed(2)
                    var invoice_percentage_current_month = ((customer_invoice_total_current_month / customer_invoice_paid_current_month) * 100).toFixed(2)
                    var supplier_invoice_total_current_month = (tot_supplier_inv_current_month - tot_supplier_refund_current_month).toFixed(2)
                    var supplier_invoice_paid_current_month = (tot_supplier_invoice_paid_current_month - tot_supplier_refund_paid_current_month).toFixed(2)
                    var supplier_percentage_current_month = ((supplier_invoice_total_current_month / supplier_invoice_paid_current_month) * 100).toFixed(2)

                    $('#tot_supplier_inv_current_month').attr("value", supplier_invoice_paid_current_month);
                    $('#tot_supplier_inv_current_month').attr("max", supplier_invoice_total_current_month);

                    $('#tot_invoice_current_month').attr("value", customer_invoice_paid_current_month);
                    $('#tot_invoice_current_month').attr("max", customer_invoice_total_current_month);
                    currency = result[8]
                    customer_invoice_paid_current_month = self.format_currency(currency, customer_invoice_paid_current_month);
                    customer_invoice_total_current_month = self.format_currency(currency, customer_invoice_total_current_month);
                    supplier_invoice_paid_current_month = self.format_currency(currency, supplier_invoice_paid_current_month);
                    supplier_invoice_total_current_month = self.format_currency(currency, supplier_invoice_total_current_month);

                    $('#total_customer_invoice_paid_current_month').append('<div class="logo">' + '<span>' + customer_invoice_paid_current_month + '</span><span>Total Paid<span></div>');
                    $('#total_customer_invoice_current_month').append('<div" class="logo">' + '<span>' + customer_invoice_total_current_month + '</span><span>Total Invoice<span></div>');

                    $('#total_supplier_invoice_paid_current_month').append('<div" class="logo">' + '<span>' + supplier_invoice_paid_current_month + '</span><span>Total Paid<span></div>');
                    $('#total_supplier_invoice_current_month').append('<div" class="logo">' + '<span>' + supplier_invoice_total_current_month + '</span><span>Total Invoice<span></div>');
                })
                var arg = 'last_month'
                var self = this;
                rpc.query({
                    model: 'account.move',
                    method: 'get_latebillss',
                    args: [posted, arg, start_date, end_date],
                }).then(function(result) {
                    console.log("________________   reuslrr",result)
                    $('#aged_payable').empty();
                    var due_count = 0;
                    var amount;
                    $('#aged_payable').empty();
                    _.forEach(result, function(x) {
                        $('#aged_payable').show();
                        due_count++;
                        amount = self.format_currency(currency, x.amount);
//						$('#aged_payable').empty();
                        $('#aged_payable').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.bill_partner + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');
                        $('#line_' + x.parent).on("click", function() {
//                            self.do_action({
//                                res_model: 'account.move',
//                                name: _t('Invoice'),
//                                views: [
//                                    [false, 'form']
//                                ],
//                                type: 'ir.actions.act_window',
//                                res_id: x.parent,
//                            });
                        });
                    });
                })

//                {
//                    $(document).ready(function() {
//                        var options = {
//                            // legend: false,
//                            responsive: true,
//                            legend: {
//                                position: 'bottom'
//                            }
//                        };
//                        if (window.donuts != undefined)
//                            window.donuts.destroy();
//                        window.donuts = new Chart($("#horizontalbarChart"), {
//                            type: 'doughnut',
//                            tooltipFillColor: "rgba(51, 51, 51, 0.55)",
//                            data: {
//                                labels: result.bill_partner,
//                                datasets: [{
//                                    data: result.bill_amount,
//                                    backgroundColor: [
//                                        '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                        '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                        '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                        ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                        '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                        '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                        '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                        '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                        '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                        '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                    ],
//                                    hoverBackgroundColor: [
//                                        '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                        '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                        '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                        ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                        '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                        '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                        '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                        '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                        '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                        '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                    ]
//                                }]
//                            },
//                            options: {
//                                responsive: false
//                            }
//                        });
//                    });
//                })
                var f = 'this_month'
                rpc.query({
                    model: "account.move",
                    method: "get_top_10_customers_month",
                    args: [posted, f, start_date, end_date]
                }).then(function(result) {
                    console.log("10_______    ",result)
                    var due_count = 0;
                    var amount;
                    $('#top_10_customers_this_month').empty();
                    _.forEach(result, function(x) {
                        $('#top_10_customers_this_month').show();
                        due_count++;
                        amount = self.format_currency(currency, x.amount);
						$('#top_10_customers_this_month').empty();
                        $('#top_10_customers_this_month').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.customers + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');
                        $('#line_' + x.parent).on("click", function() {
                            self.do_action({
                                res_model: 'res.partner',
                                name: _t('Partner'),
                                views: [
                                    [false, 'form']
                                ],
                                type: 'ir.actions.act_window',
                                res_id: x.parent,
                            });
                        });
                    });
                })
                rpc.query({
                    model: "account.move",
                    method: "bank_balance",
                    args: [posted, start_date, end_date]
                })
                .then(function(result) {
                    var banks = result['banks'];
                    var amount;
                    var balance = result['banking'];
                    var bnk_ids = result['bank_ids'];
                        $('#current_bank_balance').empty()

                    for (var k = 0; k < banks.length; k++) {
                        amount = self.format_currency(currency, balance[k]);
                        //                                $('#charts').append('<li><a ' + banks[k] + '" data-user-id="' + banks[k] + '">' + banks[k] + '</a>'+  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<span>'+ balance[k] +'</span>' + '</li>' );

                        $('#current_bank_balance').append('<li><div val="' + bnk_ids[k] + '"id="b_' + bnk_ids[k] + '">' + banks[k] + '</div><div>' + amount + '</div></li>');
                        //                                $('#current_bank_balance').append('<li>' + banks[k] +'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ balance[k] +  '</li>' );
                        $('#drop_charts_balance').append('<li>' + balance[k] + '</li>');
                        $('#b_' + bnk_ids[k]).on("click", function(ev) {
                            self.do_action({
                                res_model: 'account.account',
                                name: _t('Account'),
                                views: [
                                    [false, 'form']
                                ],
                                type: 'ir.actions.act_window',
                                res_id: parseInt(this.id.replace('b_', '')),
                            });
                        });
                    }
                })

                rpc.query({
                    model: "account.move",
                    method: "month_expense_this_month",
                    args: [posted, start_date, end_date],
                }).then(function(result) {
                    var expense_this_month = result[0].debit - result[0].credit;
                    if (expense_this_month) {
                        var expenses_this_month_ = expense_this_month;
                        expenses_this_month_ = self.format_currency(currency, expenses_this_month_);
                        $('#total_expenses_').empty()
                        $('#total_expenses_').append('<span>' + expenses_this_month_ + '</span><div class="title">This month</div>')
                    } else {
                        var expenses_this_month_ = expense_this_month;
                        expenses_this_month_ = self.format_currency(currency, expenses_this_month_);
                        $('#total_expenses_').empty()
                        $('#total_expenses_').append('<span>' + expenses_this_month_ + '</span><div class="title">This month</div>')
                    }
                })

                rpc.query({
                    model: "account.move",
                    method: "month_income_this_month",
                    args: [posted, start_date, end_date],
                }).then(function(result) {
                    var incomes_ = result[0].debit - result[0].credit;
                    if (incomes_) {
                        incomes_ = -incomes_;
                        incomes_ = self.format_currency(currency, incomes_);
                        $('#total_incomes_').empty()
                        $('#total_incomes_').append('<span>' + incomes_ + '</span><div class="title">This month</div>')
                    } else {
                        incomes_ = -incomes_;
                        incomes_ = self.format_currency(currency, incomes_);
                        $('#total_incomes_').empty()
                        $('#total_incomes_').append('<span>' + incomes_ + '</span><div class="title">This month</div>')
                    }
                })

                rpc.query({
                    model: "account.move",
                    method: "profit_income_this_month",
                    args: [posted, start_date, end_date],
                }).then(function(result) {
                    var net_profit = true
                    if (result[1] == undefined) {
                        result[1] = 0;
                        if ((result[0]) > (result[1])) {
                            net_profit = result[1] - result[0]
                        }
                    }
                    if (result[0] == undefined) {
                        result[0] = 0;
                    }
                    if ((-result[1]) > (result[0])) {
                        net_profit = -result[1] - result[0]
                    } else if ((result[1]) > (result[0])) {
                        net_profit = -result[1] - result[0]
                    } else {
                        net_profit = -result[1] - result[0]
                    }
                    var profit_this_months = net_profit;
                    if (profit_this_months) {
                        var net_profit_this_months = profit_this_months;
                        net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                        $('#net_profit_current_months').empty();
                        //$('#net_profit_current_months').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_months + '</span>')
                        $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                    } else {
                        var net_profit_this_months = profit_this_months;
                        net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                        $('#net_profit_current_months').empty();
                        //$('#net_profit_current_months').append('<div class="title">Net Profit/Loss &nbsp;&nbsp;&nbsp;</div><span>' + net_profit_this_months + '</span>')
                        $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                    }
                })
	
/*	            rpc.query({
	                model: "account.move",
	                method: "get_product_counts",
	                args: [start_date , end_date]
	            })
	            .then(function(result) {
		
					var data_line = result
					var das_table = $('#product_lines')
					das_table.empty()
	
	                for (var k = 0; k < data_line.length; k++) {
						if (k == 0){
					    	var title_line = $('<tr style="background-color:#95cce5;font-weight: bold;border:1px solid black;padding-top:0px;padding-bottom:0px;"/>');
						} else {
							var title_line = $('<tr style="border-bottom:1px solid black;padding-top:0px;padding-bottom:0px;"/>');
						}
	           			for (var l = 0; l < data_line[k].length; l++) {
							if (k == 0){
								title_line.append('<td style="padding:0.75rem;border:1px solid black;" class="text-center">' + data_line[k][l] + '</td>')
							} else {
								
								if (l == 0){
									title_line.append('<td style="padding-left:0.75rem;padding-right:0.75rem;border:1px solid black;">' + data_line[k][l] + '</td>')
								} else {
									title_line.append('<td style="border:1px solid black;text-align: right;padding-right:5px;">' + data_line[k][l] + '</td>')
								}
	
							}
						}
						das_table.append(title_line)
					}
	            })
*/


        },

        bill_q1: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q1",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q2: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q2",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q3: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q3",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },
        bill_q4: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q4",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q1_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q1_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q2_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q2_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q3_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q3_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        bill_q4_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_bill_q4_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q1: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q1",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q2: function(ev) {
            var posted = false;
            if ($('#toggle-two')[0].checked == true) {
                posted = "posted"
            }
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q2",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q3: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q3",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q4: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q4",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Invoice'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q1_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q1_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q2_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q2_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q3_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q3_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        invoice_q4_paid: function(ev) {
            var posted = false;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            var self = this;
            rpc.query({
                model: "account.move",
                method: "click_invoice_q4_paid",
                args: [posted],
            }).then(function(result) {
                self.do_action({
                    res_model: 'account.move',
                    name: _t('Paid'),
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    type: 'ir.actions.act_window',
                    domain: [
                        ['id', 'in', result]
                    ],
                });
            })
        },

        onclick_toggle_two: function(ev) {
//            this.onclick_aged_payable(this.$('#aged_receivable_values').val());
//            this.onclick_aged_payable(this.$('#aged_payable_value').val());
            this.onclick_invoice_first_quarter(ev);
            this.onclick_invoice_second_quarter(ev);
            this.onclick_invoice_third_quarter(ev);
            this.onclick_invoice_last_quarter(ev);
        },
        onclick_aged_payable: function(f) {
            var self = this
            var arg = f;
            var selected = $('.btn.btn-tool.expense');
            var data = $(selected[0]).data();
            var posted = false;
            rpc.query({
                model: 'account.move',
                method: 'get_overdues_this_month_and_year',
                args: [posted, f],
            }).then(function(result) {
                    $('#aged_receivable').empty();
                    var due_count = 0;
                    var amount;
                    $('#aged_receivable').empty();
                    _.forEach(result, function(x) {
                        $('#aged_receivable').show();
                        due_count++;
                        amount = self.format_currency(currency, x.amount);
//						$('#aged_receivable').empty();
                        $('#aged_receivable').append('<li><div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + x.due_partner + '</div>' + '<div id="line_' + x.parent + '" data-user-id="' + x.parent + '">' + amount + '</div>' + '</li>');
//                        $('#line_' + x.parent).on("click", function() {
//                            self.do_action({
//                                res_model: 'account.move',
//                                name: _t('Invoice'),
//                                views: [
//                                    [false, 'form']
//                                ],
//                                type: 'ir.actions.act_window',
//                                res_id: x.parent,
//                            });
//                        });
                    });
                })



//             {
//                // Doughnut Chart
//                $(document).ready(function() {
//                    var options = {
//                        // legend: false,
//                        responsive: false
//                    };
//                    if (window.donut != undefined)
//                        window.donut.destroy();
//                    window.donut = new Chart($("#canvas1"), {
//                        type: 'doughnut',
//                        tooltipFillColor: "rgba(51, 51, 51, 0.55)",
//                        data: {
//                            labels: result.due_partner,
//                            datasets: [{
//                                data: result.due_amount,
//                                backgroundColor: [
//                                    '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                    '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                    '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                    ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                    '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                    '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                    '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                    '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                    '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                    '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                ],
//                                hoverBackgroundColor: [
//                                    '#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf',
//                                    '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
//                                    '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
//                                    ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
//                                    '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
//                                    '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
//                                    '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
//                                    '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
//                                    '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
//                                    '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
//                                ]
//                            }]
//                        },
//                        options: {
//                            responsive: false
//                        }
//                    });
//                });
//                // Doughnut Chart
//            })
        },


        onclick_invoice_first_quarter: function(ev) {
            var selected = $('.btn.btn-tool.selected');
			console.log("selected___________1251____",selected)
            var data = $(selected[0]).data();
            var posted = false;
            var self = this;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            rpc.query({
                model: "account.move",
                method: "get_currency",
            }).then(function(result) {
                currency = result;
            })
            rpc.query({
                model: "account.move",
                method: "get_total_invoice_q1",
                args: [posted],
            }).then(function(result) {
                $('#total_supplier_invoice_paid').hide();
                $('#total_supplier_invoice').hide();
                $('#total_customer_invoice_paid').hide();
                $('#total_customer_invoice').hide();
                $('#tot_invoice').hide();
                $('#tot_supplier_inv').hide();

                $('#total_supplier_invoice_paid_current_month').hide();
                $('#total_supplier_invoice_current_month').hide();
                $('#total_customer_invoice_paid_current_month').hide();
                $('#total_customer_invoice_current_month').hide();
                $('#tot_invoice_current_month').hide();
                $('#tot_supplier_inv_current_month').hide();

                $('#total_supplier_invoice_paid_current_year').hide();
                $('#total_supplier_invoice_current_year').hide();
                $('#total_customer_invoice_paid_current_year').hide();
                $('#total_customer_invoice_current_year').hide();
                $('#tot_invoice_current_year').hide();
                $('#tot_supplier_inv_current_year').hide();

                $('#total_supplier_invoice_paid_q2').hide();
                $('#total_supplier_invoice_q2').hide();
                $('#total_customer_invoice_paid_q2').hide();
                $('#total_customer_invoice_q2').hide();
                $('#tot_invoice_q2').hide();
                $('#tot_supplier_inv_q2').hide();

                $('#total_supplier_invoice_paid_q3').hide();
                $('#total_supplier_invoice_q3').hide();
                $('#total_customer_invoice_paid_q3').hide();
                $('#total_customer_invoice_q3').hide();
                $('#tot_invoice_q3').hide();
                $('#tot_supplier_inv_q3').hide();

                $('#total_supplier_invoice_paid_q4').hide();
                $('#total_supplier_invoice_q4').hide();
                $('#total_customer_invoice_paid_q4').hide();
                $('#total_customer_invoice_q4').hide();
                $('#tot_invoice_q4').hide();
                $('#tot_supplier_inv_q4').hide();

                $('#total_supplier_invoice_paid_q1').empty();
                $('#total_supplier_invoice_q1').empty();
                $('#total_customer_invoice_paid_q1').empty();
                $('#total_customer_invoice_q1').empty();
                $('#tot_invoice_q1').empty();
                $('#tot_supplier_inv_q1').empty();

                $('#total_supplier_invoice_paid_q1').show();
                $('#total_supplier_invoice_q1').show();
                $('#total_customer_invoice_paid_q1').show();
                $('#total_customer_invoice_q1').show();
                $('#tot_supplier_inv_q1').show();
                $('#tot_invoice_q1').show();

                var tot_invoice_q1 = result[0][0]
                var tot_credit_q1 = result[1][0]
                var tot_supplier_inv_q1 = result[2][0]
                var tot_supplier_refund_q1 = result[3][0]
                var tot_customer_invoice_paid_q1 = result[4][0]
                var tot_supplier_invoice_paid_q1 = result[5][0]
                var tot_customer_credit_paid_q1 = result[6][0]
                var tot_supplier_refund_paid_q1 = result[7][0]

                var customer_invoice_total_q1 = (tot_invoice_q1 - tot_credit_q1).toFixed(2)
                var customer_invoice_paid_q1  = (tot_customer_invoice_paid_q1 - tot_customer_credit_paid_q1).toFixed(2)
                var invoice_percentage_q1  = ((customer_invoice_total_q1 / customer_invoice_paid_q1) * 100).toFixed(2)
                var supplier_invoice_total_q1  = (tot_supplier_inv_q1 - tot_supplier_refund_q1).toFixed(2)
                var supplier_invoice_paid_q1  = (tot_supplier_invoice_paid_q1 - tot_supplier_refund_paid_q1).toFixed(2)
                var supplier_percentage_q1  = ((supplier_invoice_total_q1 / supplier_invoice_paid_q1) * 100).toFixed(2)

                $('#tot_supplier_inv_q1').attr("value", supplier_invoice_paid_q1);
                $('#tot_supplier_inv_q1').attr("max", supplier_invoice_total_q1);

                $('#tot_invoice_q1').attr("value", customer_invoice_paid_q1);
                $('#tot_invoice_q1').attr("max", customer_invoice_total_q1);

                customer_invoice_paid_q1 = self.format_currency(currency, customer_invoice_paid_q1);
                customer_invoice_total_q1 = self.format_currency(currency, customer_invoice_total_q1);
                supplier_invoice_paid_q1 = self.format_currency(currency, supplier_invoice_paid_q1);
                supplier_invoice_total_q1 = self.format_currency(currency, supplier_invoice_total_q1);

                $('#total_customer_invoice_paid_q1').append('<div class="logo">' + '<span>' + customer_invoice_paid_q1 + '</span><span>Total Paid<span></div>');
                $('#total_customer_invoice_q1').append('<div" class="logo">' + '<span>' + customer_invoice_total_q1 + '</span><span>Total Invoice <span></div>');

                $('#total_supplier_invoice_paid_q1').append('<div" class="logo">' + '<span>' + supplier_invoice_paid_q1 + '</span><span>Total Paid<span></div>');
                $('#total_supplier_invoice_q1').append('<div" class="logo">' + '<span>' + supplier_invoice_total_q1 + '</span><span>Total Invoice<span></div>');

            })
        },

        onclick_invoice_second_quarter: function(ev) {
            var selected = $('.btn.btn-tool.selected');
			console.log("selected___________ 1363 ____",selected)

            var data = $(selected[0]).data();
            var posted = false;
            var self = this;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            rpc.query({
                model: "account.move",
                method: "get_currency",
            }).then(function(result) {
                currency = result;
            })
            rpc.query({
                model: "account.move",
                method: "get_total_invoice_q2",
                args: [posted],
            }).then(function(result) {
                $('#total_supplier_invoice_paid').hide();
                $('#total_supplier_invoice').hide();
                $('#total_customer_invoice_paid').hide();
                $('#total_customer_invoice').hide();
                $('#tot_invoice').hide();
                $('#tot_supplier_inv').hide();

                $('#total_supplier_invoice_paid_current_month').hide();
                $('#total_supplier_invoice_current_month').hide();
                $('#total_customer_invoice_paid_current_month').hide();
                $('#total_customer_invoice_current_month').hide();
                $('#tot_invoice_current_month').hide();
                $('#tot_supplier_inv_current_month').hide();

                $('#total_supplier_invoice_paid_current_year').hide();
                $('#total_supplier_invoice_current_year').hide();
                $('#total_customer_invoice_paid_current_year').hide();
                $('#total_customer_invoice_current_year').hide();
                $('#tot_invoice_current_year').hide();
                $('#tot_supplier_inv_current_year').hide();

                $('#total_supplier_invoice_paid_q1').hide();
                $('#total_supplier_invoice_q1').hide();
                $('#total_customer_invoice_paid_q1').hide();
                $('#total_customer_invoice_q1').hide();
                $('#tot_invoice_q1').hide();
                $('#tot_supplier_inv_q1').hide();

                $('#total_supplier_invoice_paid_q3').hide();
                $('#total_supplier_invoice_q3').hide();
                $('#total_customer_invoice_paid_q3').hide();
                $('#total_customer_invoice_q3').hide();
                $('#tot_invoice_q3').hide();
                $('#tot_supplier_inv_q3').hide();

                $('#total_supplier_invoice_paid_q4').hide();
                $('#total_supplier_invoice_q4').hide();
                $('#total_customer_invoice_paid_q4').hide();
                $('#total_customer_invoice_q4').hide();
                $('#tot_invoice_q4').hide();
                $('#tot_supplier_inv_q4').hide();

                $('#total_supplier_invoice_paid_q2').empty();
                $('#total_supplier_invoice_q2').empty();
                $('#total_customer_invoice_paid_q2').empty();
                $('#total_customer_invoice_q2').empty();
                $('#tot_invoice_q2').empty();
                $('#tot_supplier_inv_q2').empty();

                $('#total_supplier_invoice_paid_q2').show();
                $('#total_supplier_invoice_q2').show();
                $('#total_customer_invoice_paid_q2').show();
                $('#total_customer_invoice_q2').show();
                $('#tot_supplier_inv_q2').show();
                $('#tot_invoice_q2').show();

                var tot_invoice_q2 = result[0][0]
                var tot_credit_q2 = result[1][0]
                var tot_supplier_inv_q2 = result[2][0]
                var tot_supplier_refund_q2 = result[3][0]
                var tot_customer_invoice_paid_q2 = result[4][0]
                var tot_supplier_invoice_paid_q2 = result[5][0]
                var tot_customer_credit_paid_q2 = result[6][0]
                var tot_supplier_refund_paid_q2 = result[7][0]

                var customer_invoice_total_q2 = (tot_invoice_q2 - tot_credit_q2).toFixed(2)
                var customer_invoice_paid_q2  = (tot_customer_invoice_paid_q2 - tot_customer_credit_paid_q2).toFixed(2)
                var invoice_percentage_q2  = ((customer_invoice_total_q2 / customer_invoice_paid_q2) * 100).toFixed(2)
                var supplier_invoice_total_q2  = (tot_supplier_inv_q2 - tot_supplier_refund_q2).toFixed(2)
                var supplier_invoice_paid_q2  = (tot_supplier_invoice_paid_q2 - tot_supplier_refund_paid_q2).toFixed(2)
                var supplier_percentage_q2 = ((supplier_invoice_total_q2 / supplier_invoice_paid_q2) * 100).toFixed(2)

                $('#tot_supplier_inv_q2').attr("value", supplier_invoice_paid_q2);
                $('#tot_supplier_inv_q2').attr("max", supplier_invoice_total_q2);

                $('#tot_invoice_q2').attr("value", customer_invoice_paid_q2);
                $('#tot_invoice_q2').attr("max", customer_invoice_total_q2);

                customer_invoice_paid_q2 = self.format_currency(currency, customer_invoice_paid_q2);
                customer_invoice_total_q2 = self.format_currency(currency, customer_invoice_total_q2);
                supplier_invoice_paid_q2 = self.format_currency(currency, supplier_invoice_paid_q2);
                supplier_invoice_total_q2 = self.format_currency(currency, supplier_invoice_total_q2);

                $('#total_customer_invoice_paid_q2').append('<div class="logo">' + '<span>' + customer_invoice_paid_q2 + '</span><span>Total Paid<span></div>');
                $('#total_customer_invoice_q2').append('<div" class="logo">' + '<span>' + customer_invoice_total_q2 + '</span><span>Total Invoice <span></div>');

                $('#total_supplier_invoice_paid_q2').append('<div" class="logo">' + '<span>' + supplier_invoice_paid_q2 + '</span><span>Total Paid<span></div>');
                $('#total_supplier_invoice_q2').append('<div" class="logo">' + '<span>' + supplier_invoice_total_q2 + '</span><span>Total Invoice<span></div>');
            })
        },

        onclick_invoice_third_quarter: function(ev) {
            var selected = $('.btn.btn-tool.selected');
			console.log("selected___________1475____",selected)

            var data = $(selected[0]).data();
            var posted = false;
            var self = this;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}

            rpc.query({
                model: "account.move",
                method: "get_currency",
            }).then(function(result) {
                currency = result;
            })
            rpc.query({
                model: "account.move",
                method: "get_total_invoice_q3",
                args: [posted],
            }).then(function(result) {
                $('#total_supplier_invoice_paid').hide();
                $('#total_supplier_invoice').hide();
                $('#total_customer_invoice_paid').hide();
                $('#total_customer_invoice').hide();
                $('#tot_invoice').hide();
                $('#tot_supplier_inv').hide();

                $('#total_supplier_invoice_paid_current_month').hide();
                $('#total_supplier_invoice_current_month').hide();
                $('#total_customer_invoice_paid_current_month').hide();
                $('#total_customer_invoice_current_month').hide();
                $('#tot_invoice_current_month').hide();
                $('#tot_supplier_inv_current_month').hide();

                $('#total_supplier_invoice_paid_current_year').hide();
                $('#total_supplier_invoice_current_year').hide();
                $('#total_customer_invoice_paid_current_year').hide();
                $('#total_customer_invoice_current_year').hide();
                $('#tot_invoice_current_year').hide();
                $('#tot_supplier_inv_current_year').hide();

                $('#total_supplier_invoice_paid_q1').hide();
                $('#total_supplier_invoice_q1').hide();
                $('#total_customer_invoice_paid_q1').hide();
                $('#total_customer_invoice_q1').hide();
                $('#tot_invoice_q1').hide();
                $('#tot_supplier_inv_q1').hide();

                $('#total_supplier_invoice_paid_q2').hide();
                $('#total_supplier_invoice_q2').hide();
                $('#total_customer_invoice_paid_q2').hide();
                $('#total_customer_invoice_q2').hide();
                $('#tot_invoice_q2').hide();
                $('#tot_supplier_inv_q2').hide();

                $('#total_supplier_invoice_paid_q4').hide();
                $('#total_supplier_invoice_q4').hide();
                $('#total_customer_invoice_paid_q4').hide();
                $('#total_customer_invoice_q4').hide();
                $('#tot_invoice_q4').hide();
                $('#tot_supplier_inv_q4').hide();

                $('#total_supplier_invoice_paid_q3').empty();
                $('#total_supplier_invoice_q3').empty();
                $('#total_customer_invoice_paid_q3').empty();
                $('#total_customer_invoice_q3').empty();
                $('#tot_invoice_q3').empty();
                $('#tot_supplier_inv_q3').empty();

                $('#total_supplier_invoice_paid_q3').show();
                $('#total_supplier_invoice_q3').show();
                $('#total_customer_invoice_paid_q3').show();
                $('#total_customer_invoice_q3').show();
                $('#tot_supplier_inv_q3').show();
                $('#tot_invoice_q3').show();

                var tot_invoice_q3 = result[0][0]
                var tot_credit_q3 = result[1][0]
                var tot_supplier_inv_q3 = result[2][0]
                var tot_supplier_refund_q3 = result[3][0]
                var tot_customer_invoice_paid_q3 = result[4][0]
                var tot_supplier_invoice_paid_q3 = result[5][0]
                var tot_customer_credit_paid_q3 = result[6][0]
                var tot_supplier_refund_paid_q3 = result[7][0]

                var customer_invoice_total_q3 = (tot_invoice_q3 - tot_credit_q3).toFixed(2)
                var customer_invoice_paid_q3  = (tot_customer_invoice_paid_q3 - tot_customer_credit_paid_q3).toFixed(2)
                var invoice_percentage_q3  = ((customer_invoice_total_q3 / customer_invoice_paid_q3) * 100).toFixed(2)
                var supplier_invoice_total_q3  = (tot_supplier_inv_q3 - tot_supplier_refund_q3).toFixed(2)
                var supplier_invoice_paid_q3  = (tot_supplier_invoice_paid_q3 - tot_supplier_refund_paid_q3).toFixed(2)
                var supplier_percentage_q3 = ((supplier_invoice_total_q3 / supplier_invoice_paid_q3) * 100).toFixed(2)

                $('#tot_supplier_inv_q3').attr("value", supplier_invoice_paid_q3);
                $('#tot_supplier_inv_q3').attr("max", supplier_invoice_total_q3);

                $('#tot_invoice_q3').attr("value", customer_invoice_paid_q3);
                $('#tot_invoice_q3').attr("max", customer_invoice_total_q3);

                customer_invoice_paid_q3 = self.format_currency(currency, customer_invoice_paid_q3);
                customer_invoice_total_q3 = self.format_currency(currency, customer_invoice_total_q3);
                supplier_invoice_paid_q3 = self.format_currency(currency, supplier_invoice_paid_q3);
                supplier_invoice_total_q3 = self.format_currency(currency, supplier_invoice_total_q3);

                $('#total_customer_invoice_paid_q3').append('<div class="logo">' + '<span>' + customer_invoice_paid_q3 + '</span><span>Total Paid<span></div>');
                $('#total_customer_invoice_q3').append('<div" class="logo">' + '<span>' + customer_invoice_total_q3 + '</span><span>Total Invoice <span></div>');

                $('#total_supplier_invoice_paid_q3').append('<div" class="logo">' + '<span>' + supplier_invoice_paid_q3 + '</span><span>Total Paid<span></div>');
                $('#total_supplier_invoice_q3').append('<div" class="logo">' + '<span>' + supplier_invoice_total_q3 + '</span><span>Total Invoice<span></div>');
            })
        },

        onclick_invoice_last_quarter: function(ev) {
            var selected = $('.btn.btn-tool.selected');
			console.log("selected___________1588____",selected)

            var data = $(selected[0]).data();
            var posted = false;
            var self = this;
                //if ($('#toggle-two')[0].checked == true) {
                    posted = "posted"
                //}
            rpc.query({
                model: "account.move",
                method: "get_currency",
            }).then(function(result) {
                currency = result;
            })
            rpc.query({
                model: "account.move",
                method: "get_total_invoice_q4",
                args: [posted],
            }).then(function(result) {
                $('#total_supplier_invoice_paid').hide();
                $('#total_supplier_invoice').hide();
                $('#total_customer_invoice_paid').hide();
                $('#total_customer_invoice').hide();
                $('#tot_invoice').hide();
                $('#tot_supplier_inv').hide();

                $('#total_supplier_invoice_paid_current_month').hide();
                $('#total_supplier_invoice_current_month').hide();
                $('#total_customer_invoice_paid_current_month').hide();
                $('#total_customer_invoice_current_month').hide();
                $('#tot_invoice_current_month').hide();
                $('#tot_supplier_inv_current_month').hide();

                $('#total_supplier_invoice_paid_current_year').hide();
                $('#total_supplier_invoice_current_year').hide();
                $('#total_customer_invoice_paid_current_year').hide();
                $('#total_customer_invoice_current_year').hide();
                $('#tot_invoice_current_year').hide();
                $('#tot_supplier_inv_current_year').hide();

                $('#total_supplier_invoice_paid_q1').hide();
                $('#total_supplier_invoice_q1').hide();
                $('#total_customer_invoice_paid_q1').hide();
                $('#total_customer_invoice_q1').hide();
                $('#tot_invoice_q1').hide();
                $('#tot_supplier_inv_q1').hide();

                $('#total_supplier_invoice_paid_q2').hide();
                $('#total_supplier_invoice_q2').hide();
                $('#total_customer_invoice_paid_q2').hide();
                $('#total_customer_invoice_q2').hide();
                $('#tot_invoice_q2').hide();
                $('#tot_supplier_inv_q2').hide();

                $('#total_supplier_invoice_paid_q3').hide();
                $('#total_supplier_invoice_q3').hide();
                $('#total_customer_invoice_paid_q3').hide();
                $('#total_customer_invoice_q3').hide();
                $('#tot_invoice_q3').hide();
                $('#tot_supplier_inv_q3').hide();

                $('#total_supplier_invoice_paid_q4').empty();
                $('#total_supplier_invoice_q4').empty();
                $('#total_customer_invoice_paid_q4').empty();
                $('#total_customer_invoice_q4').empty();
                $('#tot_invoice_q4').empty();
                $('#tot_supplier_inv_q4').empty();

                $('#total_supplier_invoice_paid_q4').show();
                $('#total_supplier_invoice_q4').show();
                $('#total_customer_invoice_paid_q4').show();
                $('#total_customer_invoice_q4').show();
                $('#tot_supplier_inv_q4').show();
                $('#tot_invoice_q4').show();

                var tot_invoice_q4 = result[0][0]
                var tot_credit_q4 = result[1][0]
                var tot_supplier_inv_q4 = result[2][0]
                var tot_supplier_refund_q4 = result[3][0]
                var tot_customer_invoice_paid_q4 = result[4][0]
                var tot_supplier_invoice_paid_q4 = result[5][0]
                var tot_customer_credit_paid_q4 = result[6][0]
                var tot_supplier_refund_paid_q4 = result[7][0]

                var customer_invoice_total_q4 = (tot_invoice_q4 - tot_credit_q4).toFixed(2)
                var customer_invoice_paid_q4  = (tot_customer_invoice_paid_q4 - tot_customer_credit_paid_q4).toFixed(2)
                var invoice_percentage_q4  = ((customer_invoice_total_q4 / customer_invoice_paid_q4) * 100).toFixed(2)
                var supplier_invoice_total_q4  = (tot_supplier_inv_q4 - tot_supplier_refund_q4).toFixed(2)
                var supplier_invoice_paid_q4  = (tot_supplier_invoice_paid_q4 - tot_supplier_refund_paid_q4).toFixed(2)
                var supplier_percentage_q4 = ((supplier_invoice_total_q4 / supplier_invoice_paid_q4) * 100).toFixed(2)

                $('#tot_supplier_inv_q4').attr("value", supplier_invoice_paid_q4);
                $('#tot_supplier_inv_q4').attr("max", supplier_invoice_total_q4);

                $('#tot_invoice_q4').attr("value", customer_invoice_paid_q4);
                $('#tot_invoice_q4').attr("max", customer_invoice_total_q4);

                customer_invoice_paid_q4 = self.format_currency(currency, customer_invoice_paid_q4);
                customer_invoice_total_q4 = self.format_currency(currency, customer_invoice_total_q4);
                supplier_invoice_paid_q4 = self.format_currency(currency, supplier_invoice_paid_q4);
                supplier_invoice_total_q4 = self.format_currency(currency, supplier_invoice_total_q4);

                $('#total_customer_invoice_paid_q4').append('<div class="logo">' + '<span>' + customer_invoice_paid_q4 + '</span><span>Total Paid<span></div>');
                $('#total_customer_invoice_q4').append('<div" class="logo">' + '<span>' + customer_invoice_total_q4 + '</span><span>Total Invoice <span></div>');

                $('#total_supplier_invoice_paid_q4').append('<div" class="logo">' + '<span>' + supplier_invoice_paid_q4 + '</span><span>Total Paid<span></div>');
                $('#total_supplier_invoice_q4').append('<div" class="logo">' + '<span>' + supplier_invoice_total_q4 + '</span><span>Total Invoice<span></div>');
            })
        },


    });

return AccountingDashboard;

});