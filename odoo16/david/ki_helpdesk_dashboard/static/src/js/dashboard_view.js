odoo.define("ki_helpdesk_dashboard.dashboard_view", function (require) {
    "use strict";

    const AbstractAction = require("web.AbstractAction");
    const core = require("web.core");
    const rpc = require("web.rpc");
    var ajax = require("web.ajax");
    const { DateTime } = luxon;
    const _t = core._t;
    const QWeb = core.qweb;
    const DashBoard = AbstractAction.extend({
        template: "HelpDesk_Dashboard",
        events: {
            "click .inbox_tickets": "tickets_inbox",
            "click .inprogress_tickets": "tickets_inprogress",
            "click .done_tickets": "tickets_done",
            "click .team_card": "helpdesk_teams",
            "click .ticket_team": "ticket_teams",
            "click .urgent_action": "urgent_action",
            "click .unassign_action": "unassign_action",
            "click .open_action": "open_action",
            "click .close_action": "close_action",
            "click .fail_action": "fail_action"
        },
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['DashBoardHelpDesk'];

        },

        willStart: function(){
        var self = this;
        self.dashboard_dict = {}
        return this._super()
        .then(function() {

        var def1 = self._rpc({
                model: 'helpdesk.support',
                method: 'get_tickets_all_count'
        }).then(function(result) {
            self.dashboard_dict = result
        });


        return $.when(def1);
        });
    },

        start: function () {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function () {
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });

        },
        render_graphs: function () {
            var self = this;
            self.render_tickets_month_graph();
            self.render_team_ticket_count_graph();
//            self.render_projects_ticket_graph();
//            self.render_billed_task_team_graph();
//            self.render_team_ticket_done_graph();

        },
      render_tickets_month_graph: function () {
    var self = this;
    var ctx = self.$(".ticket_month");
    rpc.query({
        model: "helpdesk.support",
        method: "get_tickets_view",
    }).then(function (values) {
        var data = {
            labels: ['New', 'In Progress', 'Solved'],
            datasets: [{
                data: [values.inbox_count, values.progress_count, values.done_count],
                backgroundColor: [
                    '#fa7720',
                            '#4682B4',
                    "#dee4fa"
                ],
                borderColor: [
                      '#fa7720',
                            '#4682B4',
                    "#dee4fa"
                ],
                borderWidth: 1
            }]
        };

        //options
        var options = {
            responsive: true,
            title: false,
            legend: {
                display: true,
                position: "right",
                labels: {
                    fontColor: "#333",
                    fontSize: 16
                }
            },
            scales: {
                yAxes: [{
                    gridLines: {
                        color: "rgba(0, 0, 0, 0)",
                        display: false,
                    },
                    ticks: {
                        min: 0,
                        display: false,
                    }
                }]
            }
        };

        //create Chart class object
        var chart = new Chart(ctx, {
            type: "doughnut",
            data: data,
            options: options
        });
    });
},

        render_team_ticket_count_graph: function () {
            var self = this
            var ctx = self.$(".team_ticket_count");
            rpc.query({
                model: "helpdesk.support",
                method: "get_team_ticket_count_pie",
            }).then(function (arrays) {
                var data = {
                    labels: arrays[1],
                    datasets: [{
                        label: "",
                        data: arrays[0],
                        backgroundColor: [
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
//                            'rgba(75, 192, 192, 0.2)',
//                            'rgba(54, 162, 235, 0.2)',
//                            'rgba(153, 102, 255, 0.2)',
//                            'rgba(201, 203, 207, 0.2)'
                        ],
                        borderColor: [
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
                            '#fa7720',
                            '#4682B4',
//                            'rgb(75, 192, 192)',
//                            'rgb(54, 162, 235)',
//                            'rgb(153, 102, 255)',
//                            'rgb(201, 203, 207)'
                        ],
                        borderWidth: 1
                    },]
                };

                //options
                var options = {
                    responsive: true,
                    title: false,
                    maintainAspectRatio: true,
                    legend: {
                        display: false //This will do the task
                    },
                    scales: {
                        yAxes: [{
                            display: true,
                            ticks: {
                                beginAtZero: true,
                                steps: 10,
                                stepValue: 5,
                                // max: 100
                            }
                        }]
                    }
                };

                //create Chart class object
                var chart = new Chart(ctx, {
                    type: "bar",
                    data: data,
                    options: options
                });
            });
        },


        render_dashboards: function () {
            var self = this;
            var templates = ['DashBoardHelpDesk'];
            _.each(templates, function (template) {
                self.$('.helpdesk_dashboard_main').append(QWeb.render(template, {widget: self, dashboard_dict:self.dashboard_dict,}));
            });
            rpc.query({
                model: "helpdesk.support",
                method: "get_tickets_count",
                args: [],
            })
                .then(function (result) {
                    $("#inbox_count").append("<span class='stat-digits'>" + result.inbox_count + "</span>");
                    $("#inprogress_count").append("<span class='stat-digits'>" + result.progress_count + "</span>");
                    $("#done_count").append("<span class='stat-digits'>" + result.done_count + "</span>");
                    $("#team_count").append("<span class='stat-digits'>" + result.team_count + "</span>");


                        var priorityCounts = {
                        very_low: result.very_low_count1,
                        low: result.low_count1,
                        normal: result.normal_count1,
                        high: result.high_count1,
                        very_high : result.very_high_count1
                        // Add other priorities and their corresponding count properties
                    };

                    // Loop through the priorities and create progress bars
                    for (var priority in priorityCounts) {
                        var progressBarWidth = priorityCounts[priority] + "%";

                        var progressBar = $("<div class='progress-bar'></div>").css("width", progressBarWidth);
                        var progressBarContainer = $("<div class='progress'></div>").append(progressBar);
                        var progressValue = $("<div class='progress-value'></div>").text(priorityCounts[priority] + "%");

                        // Append the progress bar container to elements with class corresponding to the priority
                        $("." + priority + "_count").append(progressBarContainer);
                        $("." + priority + "_count .progress-value").append(progressValue);

                    }

                         var tbody = $(".ticket-details");
                        var ticket_details = result.ticket_details;

                        for (var i = 0; i < ticket_details.length; i++) {
                            var ticket = ticket_details[i]; // Get the current ticket object
                            var row = $("<tr></tr>");

                            row.append("<td class='td'>" + ticket.ticket_name + "</td>");
                            row.append("<td class='td'>" + ticket.customer_name + "</td>");
                            row.append("<td class='td'>" + ticket.assigned_category + "</td>");
                            row.append("<td>" + ticket.assigned_to + "</td>");
                            row.append("<td>" + ticket.subject + "</td>");
                            row.append("<td>" + ticket.stage + "</td>");
                            tbody.append(row);
                        }


                });
        },


        //events
        tickets_inbox: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Inbox"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['stage_id.stage_type', '=', 'new']],
                context: {default_stage_id_stage_type: 'new'},
                target: 'current'
            });
        },

        tickets_inprogress: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("In Progress"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['stage_id.stage_type', '=', 'work_in_progress']],
                context: {create: false},
                target: 'current'
            });
        },
        tickets_done: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Done"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['stage_id.stage_type', '=', 'closed']],
                context: {create: false},
                target: 'current'
            });
        },
        helpdesk_teams: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: _t("Teams"),
                type: 'ir.actions.act_window',
                res_model: 'support.team',

                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },

        ticket_teams: function (ev) {
        var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("Teams"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)]],
                target: 'current'
            });
        },

        unassign_action: function (ev) {
        var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("unassigned"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)],['user_id', '=', false]],
                target: 'current'
            });
        },


        fail_action: function (ev) {
        var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("fail"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)],['is_failed', '=', true]],
                target: 'current'
            });
        },

        urgent_action: function (ev) {
        var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("urgent"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)],['priority', '=', 2]],
                target: 'current'
            });
        },

        open_action: function (ev) {
         var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("open"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'list,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)]],
                target: 'current'
            });
        },

        close_action: function (ev) {
        var category_id = $(ev.currentTarget).attr('data-id');
            var self = this;
            ev.stopPropagation();
            this.do_action({
                name: _t("close"),
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.support',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['team_id', '=', parseInt(category_id)],['stage_id.stage_type', '=', 'closed']],
                target: 'current'
            });
        },


    });

    core.action_registry.add("helpdesk_dashboard", DashBoard);
    return DashBoard;
});
