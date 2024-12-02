odoo.define("reddot_dashboard_hr.dashboard", function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var stage_domain;
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var DashBoardHr = AbstractAction.extend({
        contentTemplate: 'DashBoardHr',
        events: {
            "click .open_contract": "open_contract",
            "click .expired_contract": "expired_contract",
            "click .upcoming_contract": "upcoming_contract",
            'click #custom_date_onclick': 'custom_date_onclick',
            'click .open_headCount': 'click_open_headCount',
            'click .open_hires': 'click_open_hires',
            'click .open_terminations': 'click_open_terminations',
            'change .date_filter_values': 'date_filter_values',
            'change .company_filter_values': 'company_filter_values',
            'change .department_filter_values': 'department_filter_values',
            'change .gender_filter_values': 'gender_filter_values',
            'change .job_filter_values': 'job_filter_values',
        },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['HrDashboard'];
        },

        willStart: function(){
            var self = this;
            return this._super()
            .then(function() {
                var def1 =  self.gender_count();
                var years =  self.get_financial_year();
                var company =  self.get_company_data();
                var department =  self.department_data();
                var job_data =  self.get_job_filter_values();
                var employee =  self.employee_count();
                var contract =  self.contract_count();

            });
        },
        final_method : function(start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            self.gender_count(start_date,end_date,company,department,gender,position);
            self.employee_count(start_date,end_date,company,department,gender,position);
            self.contract_count(start_date,end_date,company,department,gender,position);
            self.headcount_by_contract_type(start_date,end_date,company,department,gender,position);
            self.headcount_by_job_position(start_date,end_date,company,department,gender,position);
            self.headcount_by_department(start_date,end_date,company,department,gender,position);
            self.headcount_by_age_range(start_date,end_date,company,department,gender,position);
            self.employee_type_position(start_date,end_date,company,department,gender,position);
            self.headcount_by_office(start_date,end_date,company,department,gender,position);
        },

        date_filter_values: function (ev) {
            var year = $('#date_filter_values_id').val();
            var company=null
            var company = $('#filter_company_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            $('#date_filter_data').empty()
            $('#date_filter_data').show()
            $('.filter').show()
            $('#date_filter_data').append('<span>'+ year +'</span>');
            var self = this;
            var start_date, end_date;
            if (year === 'custom') {
                $('#openpopup').modal('show');
            }
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null  &&  year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
                self.final_method(start_date, end_date,company,department,gender,position)
            } else {
                console.error('Invalid year:', year);
            }
        },

        company_filter_values : function (ev) {
            var self = this;
            var start_date, end_date;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            $('#company_filter_data').empty()
            $('#company_filter_data').show()
            $('.filter').show()
            $('#company_filter_data').append('<span>'+ company +'</span>');
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null  &&  year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            self.final_method(start_date, end_date,company,department,gender,position)
        },

        department_filter_values: function (ev) {
            var self = this;
            var start_date, end_date;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            $('#department_filter_data').empty()
            $('.filter').show()
            $('#department_filter_data').show()
            $('#department_filter_data').append('<span>'+ department +'</span>');
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null  &&  year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            self.final_method(start_date, end_date,company,department,gender,position)
        },

        gender_filter_values: function (ev) {
            var self = this;
            var start_date, end_date;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            $('#gender_filter_data').empty()
            $('.filter').show()
            $('#gender_filter_data').show()
            $('#gender_filter_data').append('<span>'+ gender +'</span>');
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null  && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }

            self.final_method(start_date, end_date,company,department,gender,position)
        },

        job_filter_values: function (ev) {
            var self = this;
            var start_date, end_date;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            $('#job_position_filter_data').empty()
            $('#job_position_filter_data').show()
            $('.filter').show()
            $('#job_position_filter_data').append('<span>'+ position +'</span>');
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            self.final_method(start_date, end_date,company,department,gender,position)
        },


        custom_date_onclick: function (ev) {
            var self = this;
            var start_date = self.$('#start_date').val();
            var end_date = self.$('#end_date').val();
            self.final_method(start_date, end_date)
        },

        get_company_data: function() {
            var self = this;
            var def1 = self._rpc({
               model: 'hr.employee',
               method: 'get_company_data',
               args: []
            }).then(function(result) {
                for (var c in result) {
                    self.$('.company_filter_values').append('<option data-value=' + c + '>' + result[c] + '</option>');
                };
            });
            return def1
        },

        department_data: function() {
            var self = this;
            var def1 = self._rpc({
               model: 'hr.employee',
               method: 'get_department_data',
               args: []
            }).then(function(result) {
                for (var c in result) {
                    self.$('.department_filter_values').append('<option data-value=' + result[c] + '>' + result[c] + '</option>');
                };
            });
            return def1
        },

        get_job_filter_values: function() {
            var self = this;
            var def1 = self._rpc({
               model: 'hr.employee',
               method: 'get_job_position_data',
               args: []
            }).then(function(result) {
                for (var c in result) {
                    self.$('.job_filter_values').append('<option data-value=' + result[c] + '>' + result[c] + '</option>');
                };
            });
            return def1
        },

        get_financial_year: function(start_date=null,end_date=null) {
            var self = this;
            var def1 = self._rpc({
                model: 'hr.employee',
                method: 'get_last_three_financial_years',
                args: [1,start_date,end_date]
            }).then(function(result) {
                for (var c in result) {
                    self.$('.date_filter_values').append('<option class="class_year" data-value=' + result[c] + '>' + result[c] + '</option>');
                };
                self.$('.date_filter_values').append('<option class="class_year" value="custom">Custom</option>');
            });
            return def1
        },

        open_contract: function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var id = ev.currentTarget.id
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            rpc.query({
                model: "hr.employee",
                method: "click_open_contract",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        expired_contract:  function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            rpc.query({
                model: "hr.employee",
                method: "click_expired_contract",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        upcoming_contract:function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            rpc.query({
                model: "hr.employee",
                method: "click_upcoming_contract",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        click_open_headCount: function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            rpc.query({
                model: "hr.employee",
                method: "click_headCount",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        click_open_hires: function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
			rpc.query({
                model: "hr.employee",
                method: "click_hires",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        click_open_terminations: function(ev) {
            var posted = false;
            var self = this;
            var company = $('#filter_company_id').val();
            var year = $('#date_filter_values_id').val();
            var department = $('#department_filter_values_id').val();
            var gender = $('#gender_filter_values_id').val();
            var position = $('#job_filter_values_id').val();
            var start_date = null
            var end_date = null
            if (year = 'custom') {
                var start_date = self.$('#start_date').val();
                var end_date = self.$('#end_date').val();
            }
            if (year != null && year != 'custom') {
                var start_date = new Date(year, 0, 1).toISOString().split('T')[0];
                var end_date = new Date(year, 11, 31).toISOString().split('T')[0];
            }
            rpc.query({
                model: "hr.employee",
                method: "click_terminations",
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                self.do_action(result);
            })
        },

        gender_count: function(start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            var def1 = self._rpc({
                model: 'hr.employee',
                method: 'get_gender_count',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                $('#male_count').empty()
                $('#female_count').empty()
                self.$('#male_count').append('<span>'+ result.male +'</span>');
                self.$('#female_count').append('<span>'+ result.female +'</span>');
            });
            return def1
        },

        employee_count: function(start_date=null,end_date=null ,company=null,department=null,gender=null,position=null) {
            var self = this;
            var fields;
            var def1 = self._rpc({
                model: 'hr.employee',
                method: 'get_employee_count',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                $('#all_employee_count').empty()
                $('#hired_employee_count').empty()
                $('#terminate_employee_count').empty()
                self.$('#all_employee_count').append('<span>'+ result.all_employee +'</span>');
                self.$('#hired_employee_count').append('<span>'+ result.hired_employee +'</span>');
                self.$('#terminate_employee_count').append('<span>'+ result.terminate_employee +'</span>');
            });
            return def1
        },

        contract_count: function(start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            var fields;
            var def1 = self._rpc({
                model: 'hr.employee',
                method: 'get_contract_count',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function(result) {
                $('#open_contact_count').empty()
                $('#expired_contact_count').empty()
                $('#upcoming_contact_count').empty()
                self.$('#open_contact_count').append('<span>'+ result.open_contract +'</span>');
                self.$('#expired_contact_count').append('<span>'+ result.close_contract +'</span>');
                self.$('#upcoming_contact_count').append('<span>'+ result.upcoming_contract +'</span>');
            });
            return def1
        },

        start: function() {
            var self = this;
            self.render_dashboards();
            self.renderChart();
            this.set("title", 'DashBoardHr');
            return this._super().then(function() {
            });
        },
        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template){
                self.$('.o_hr_dashboard').append(QWeb.render(template,
                    {
                    }
                ));
            });
        },

        employee_type_position: function(start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            rpc.query({
                model: 'hr.employee',
                method: 'open_position_employee_type',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (result) {
                var ctx = self.$el.find('#open_possition_chart')[0].getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: result['employee_type_label'],
                        datasets: [{
                            data: result['employee_type_value'],
                            backgroundColor: result['backgroundColor']
                        }]
                    },
                    options: {
                        title: {
                            display: true,
                            text: 'Open Positions By Employee Type'
                        },
                    }
                });
            });
        },

        headcount_by_office:  function(start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'get_headcount_by_office_pie_chart',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (data) {
                var ctx = self.$el.find('#HeadcountByOfficePieChart')[0].getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                        data: {
                        labels:  data['office_type_label'],
                        datasets: [{
                            data:  data['office_type_value'],
                            backgroundColor: data['backgroundColor']
                        }]
                    },
                    options: {
                        title: {
                            display: true,
                            text: 'HeadCount BY Office'
                        },
                    }
                });
            });
        },

        headcount_by_department:function (start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'get_headcount_by_department_pie_chart',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (data) {
                var ctx = self.$el.find('#HeadCountByDepartmentPieChart')[0].getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data['department_type_label'],
                        datasets: [{
                            data: data['department_type_value'],
                            backgroundColor: data['backgroundColor']
                        }]
                    },
                    options: {
                        title: {
                            display: true,
                            text: 'HeadCount By Department'
                        },
                    }
                });
            });
        },

        headcount_by_contract_type: function (start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            rpc.query({
                model: 'hr.employee',
                method: 'get_data_headcount_by_contract_type',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (result) {
                var ctx = self.$el.find('#head_count_contract_type')[0].getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: result['contract_type_label'],
                        datasets: [{
                            data: result['contract_type_value'],
                            backgroundColor:result['backgroundColor']
                        }]
                    },
                    options: {
                        title: {
                            display: true,
                            text: 'Head Count By Contract Type'
                        },
                    }
                });
            });
        },

        headcount_by_job_position: function (start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'get_headcount_by_job_position',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (data) {
                var ctx = self.$el.find('#headcountByEducationChart')[0].getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data['job_type_label'],
                        datasets: [{
                            data: data['job_type_value'],
                            backgroundColor: data['backgroundColor']
                        }]
                    },
                    options: {
                        title: {
                            display: true,
                            text: 'HandCount By Job Position'
                        },
                    }
                });
            });
        },
        headcount_by_age_range: function (start_date=null,end_date=null,company=null,department=null,gender=null,position=null) {
            var self = this;
            rpc.query({
                model: 'hr.employee',
                method: 'get_headcount_by_age_range',
                kwargs: {
                    'start_date':start_date,
                    'end_date' : end_date,
                    'company' : company,
                    'department' : department,
                    'gender' : gender,
                    'position' : position,
                },
            }).then(function (result) {
                var chart = new Chart("handCount_by_range_bar_chart", {
                    type: "bar",
                    data: {
                        labels: result[0],
                        datasets: [{
                            backgroundColor:  result[2],
                            label : "Age Range",
                            data: result[1],
                        }]
                    },
                    options: {}
                });
            });
        },
        renderChart: function () {
            var self = this;
             self.employee_type_position();
             self.headcount_by_office();
             self.headcount_by_department();
             self.headcount_by_contract_type();
             self.headcount_by_job_position();
             self.headcount_by_age_range();
            },
        });
    core.action_registry.add('hr_dashboard_tag', DashBoardHr);
    return;
});