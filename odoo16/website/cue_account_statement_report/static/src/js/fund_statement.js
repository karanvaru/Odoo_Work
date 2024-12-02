odoo.define('cue_account_statement_report.fund_statement', function(require) {
	'use strict';
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var field_utils = require('web.field_utils');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var utils = require('web.utils');
	var QWeb = core.qweb;
	var _t = core._t;
	var datepicker = require('web.datepicker');
	var time = require('web.time');
	var framework = require('web.framework');
    var filter_data_selected = {};
	window.click_num = 0;
	var fundstatement = AbstractAction.extend({
		template: 'FundStatementTemp',
			events: {
			    'click .fl-line': 'show_drop_down',
			    'click .flh-line': 'show_capital_down',
			    'click #fs_apply_filter': 'apply_filter',
			    'click #fund_xlsx': 'print_xlsx',
			    'mousedown div.input-group.date[data-target-input="nearest"]': '_onCalendarIconClick',
		    },

		init: function(parent, action) {
			this._super(parent, action);
			this.wizard_id = action.context.wizard | null;
		},

		start: function() {
			var self = this;
			self.initial_render = true;
			rpc.query({
				model: 'fund.statement',
				method: 'create',
				args: [{}]
			}).then(function(t_res) {
				self.wizard_id = t_res;
				self.apply_filter();
			})
		},
	    _onCalendarIconClick: function(ev) {
			var $calendarInputGroup = $(ev.currentTarget);
			var calendarOptions = {
				minDate: moment({
					y: 1000
				}),
				maxDate: moment().add(200, 'y'),
				calendarWeeks: true,
				defaultDate: moment().format(),
				sideBySide: true,
				buttons: {
					showClear: true,
					showClose: true,
					showToday: true,
				},
				icons: {
					date: 'fa fa-calendar',
				},
				locale: moment.locale(),
				format: time.getLangDateFormat(),
				widgetParent: 'body',
				allowInputToggle: true,
			};
			$calendarInputGroup.datetimepicker(calendarOptions);
		},

        print_xlsx: function() {
	        var self = this;
			var action_title = self._title
			self._rpc({
			    model: 'fund.statement',
				method: 'view_report',
				kwargs: [{
                    'wizard_id':self.wizard_id,
                    'data_dct' : filter_data_selected
                }],
			    }).then(function(data) {
				    var action = {
					'data': {
						'model': 'fund.statement',
						'output_format': 'xlsx',
						'report_data': JSON.stringify(data['header']),
						'report_month': JSON.stringify(data['month_list']),
						'report_name': action_title,
						'dfr_data': JSON.stringify(data),
					},
				};
				self.downloadXlsx(action)
			});
		},
		downloadXlsx: function(action) {
			framework.blockUI();
			session.get_file({
				url: '/fund_statement_dynamic_xlsx_reports',
				data: action.data,
				complete: framework.unblockUI,
				error: (error) => this.call('crash_manager', 'rpc_error', error),
			});
		},

        apply_filter: function(event) {
            var self = this;
            if (this.$el.find('.datetimepicker-input[name="date_from"]').val()) {
                filter_data_selected.date_from = moment(this.$el.find('.datetimepicker-input[name="date_from"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }
            if (this.$el.find('.datetimepicker-input[name="date_to"]').val()) {
                filter_data_selected.date_to = moment(this.$el.find('.datetimepicker-input[name="date_to"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
            }
            self.$(".categ").empty();
            try {
                var self = this;
                self._rpc({
                    model: 'fund.statement',
                    method: 'view_report',
                    kwargs: [{
                        'wizard_id':this.wizard_id,
                        'data_dct' : filter_data_selected
                    }],
                }).then(function(data) {
                    var child = [];
                    self.$('.table_view_tb').html(QWeb.render('FSTable', {
                        month_data: data['month_list'],
                        symbol: data['symbol'],
                        account_data: data['header'],
                    }));
                    self.$('.filter_view_tb').html(QWeb.render('FSFilterView', {
                    }));
                });

            } catch (el) {
                window.location.href
            }
        },

        show_capital_down: function(event) {
            event.preventDefault();
            var self = this;
            var inner_data = $(event.currentTarget).data('inner-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length ==1) {
                self._rpc({
                    model: 'fund.statement',
                    method: 'get_working_capital_data_new',
                    kwargs: [{
                    'wizard_id':this.wizard_id,
                    'data_dct' : filter_data_selected
                }],
                }).then(function(data) {
                    for (var inner in data['data']){
                        if (inner_data == data['data'][inner]['id']) {
                            var td_data_inner = $(event.currentTarget).next('tr').find('td').remove();
                            $(event.currentTarget).next('tr').after(
                                QWeb.render('SubInnerSectionFS', {
                                    inner_details: data['data'][inner],

                                })
                            )
                        }
                    }
                });
            }
        },

        show_drop_down: function(event) {
            event.preventDefault();
            var self = this;
            var header_id = $(event.currentTarget).data('header-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            var header_list = ['Net Income','EBIT','Interest Payments','Tax Payments','Cash Flow from Financing Activity','Cash In Hand at the beginning','Minimum Capital Required | Net Cash Flow','Cumulative Net Cashflow']
            if (td.length == 1) {
                self._rpc({
                    model: 'fund.statement',
                    method: 'view_report',
                    kwargs: [{
                    'wizard_id':this.wizard_id,
                    'data_dct' : filter_data_selected
                }],
                }).then(function(data) {
                    for (var header in data['header']){
                    if (header_id == header) {
                        if (header_list.includes(header_id)) {
                            return
                        }
                        var td_data = $(event.currentTarget).next('tr').find('td').remove();
                            $(event.currentTarget).next('tr').after(
                                QWeb.render('SubSectionFS', {
                                    account_data: data['header'][header],
                                    symbol: data['symbol'],
                                    id: data,
                                    header_name : header
                                })
                            )
                        }
                    }
                });
            }
        },
	});
	core.action_registry.add("f_s", fundstatement);
	return fundstatement;
});