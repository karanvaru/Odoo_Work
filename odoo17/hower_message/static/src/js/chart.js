///** @odoo-module */
//
//import { loadJS } from "@web/core/assets";
//import { useService } from "@web/core/utils/hooks";
//import { registry } from "@web/core/registry";
//
//import { getColor } from "@web/core/colors/colors";
//import { cookie } from "@web/core/browser/cookie";
//import { Component, onWillUnmount, useEffect, useRef, useState, onWillStart } from "@odoo/owl";
//console.log("_________________   8")
//
//export class dashboard extends Component {
////    setup() {
////        this.actionService = useService("action");
////        this.canvasRef = useRef('canvas');
////        this.state = useState({ monthly: true });
////        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
////        useEffect(() => this.renderChart());
////        onWillUnmount(() => {
////            if (this.chart) {
////                this.chart.destroy();
////            }
////        });
////    }
//
//    setup() {
//        super.setup();
//        this.orm = useService("orm");
//        this.state = useState({hierarchy: {}});
//        onWillStart(this.onWillStart);
//    }
//
//
//    onWillStart(){
//            console.log("______________________________")
//            var default_activity_id;
//            var default_activity_name;
//            var activity_data = [];
//            var self=this;
////            self.orm.call("activity.dashboard", "get_scheduled_activity", [
////            ]).then(function(result){
////            self.state.hierarchy = result
////            });
//}
//
//
//    /**
//     * @returns {string}
//     */
//    get tooltipInfo() {
//    console.log("_________________28")
//
//        return JSON.stringify({
//            help: this.props.help,
//        });
//    }
//
//    toggle() {
//    console.log("_________________   36")
//
//        this.state.monthly = !this.state.monthly;
//    }
//
//    /**
//     * @returns {object} The current chart data to be used depending on the state
//     */
//    get graphData() {
//    console.log("_________________   45")
//
//        return this.props.data[this.state.monthly ? 'monthly': 'yearly'];
//    }
//
//    /**
//     * Creates and binds the chart on `canvasRef`.
//     */
//    renderChart() {
//        if (this.chart) {
//            this.chart.destroy();
//        }
//        console.log("_________________-  call")
//        const ctx = this.canvasRef.el.getContext('2d');
//        this.chart = new Chart(ctx, this.getChartConfig());
//    }
//
//    /**
//     * @returns {object} Chart config for the current data
//     */
//    getChartConfig() {
//        console.log("_________________   66")
//
////        const type = this.props.type;
////        if (type === 'line') {
////            return this.getLineChartConfig();
////        } else if (type === 'bar') {
////            return this.getBarChartConfig();
////        } else if (type === 'stacked_bar') {
////            return this.getStackedBarChartConfig();
////        }
////        return {};
//    }
//
//    /**
//     * @returns {object} Chart config of type 'line'
//     */
////    getLineChartConfig() {
////        const data = this.graphData
////        const labels = data.map(function (pt) {
////            return pt.x;
////        });
////        const borderColor = this.props.is_sample ? '#dddddd' : '#875a7b';
////        const backgroundColor = this.props.is_sample ? '#ebebeb' : '#dcd0d9';
////        return {
////            type: 'line',
////            data: {
////                labels: labels,
////                datasets: [{
////                    data: data,
////                    fill: 'start',
////                    label: this.props.label,
////                    backgroundColor: backgroundColor,
////                    borderColor: borderColor,
////                    borderWidth: 2,
////                }],
////            },
////            options: {
////                plugins : {
////                    legend: {display: false},
////                    tooltip: {
////                        intersect: false,
////                        position: 'nearest',
////                        caretSize: 0,
////                    },
////                },
////                scales: {
////                    y: {
////                        display: false,
////                        beginAtZero: true,
////                    },
////                    x: {
////                        display: false
////                    },
////                },
////                maintainAspectRatio: false,
////                elements: {
////                    line: {
////                        tension: 0.000001,
////                    },
////                },
////            },
////        };
////    }
//
//    /**
//     * @returns {object} Chart config of type 'bar'
//     */
////    getBarChartConfig() {
////        const data = [];
////        const labels = [];
////        const backgroundColors = [];
////        const color19 = getColor(19, cookie.get("color_scheme"));
////        this.graphData.forEach((pt) => {
////            data.push(pt.value);
////            labels.push(pt.label);
////            let color;
////            if (this.props.is_sample) {
////                color = '#ebebeb';
////            } else if (pt.type === 'past') {
////                color = '#ccbdc8';
////            } else if (pt.type === 'future') {
////                color = '#a5d8d7';
////            } else {
////                color = color19;
////            }
////            backgroundColors.push(color);
////        });
////
////        return {
////            type: 'bar',
////            data: {
////                labels: labels,
////                datasets: [{
////                    data: data,
////                    fill: 'start',
////                    label: this.props.label,
////                    backgroundColor: backgroundColors,
////                }],
////            },
////            options: {
////                plugins : {
////                    legend: {display: false},
////                    tooltip: {
////                        intersect: false,
////                        position: 'nearest',
////                        caretSize: 0,
////                    },
////                },
////                scales: {
////                    yAxes:
////                        {
////                            display: false,
////                            beginAtZero: true,
////                        }
////                },
////                maintainAspectRatio: false,
////                elements: {
////                    line: {
////                        tension: 0.000001
////                    }
////                }
////            }
////        };
////    }
//
//    /**
//     * @returns {object} Chart config of type 'stacked bar'
//     */
////    getStackedBarChartConfig() {
////        const labels = [];
////        const datasets = [];
////        const datasets_labels = [];
////        let colors;
////        if (this.props.is_sample) {
////            colors = ['#e7e7e7', '#dddddd', '#f0f0f0', '#fafafa'];
////        } else {
////            colors = [getColor(13, cookie.get("color_scheme")), '#a5d8d7', '#ebebeb', '#ebebeb'];
////        }
////
////
////        Object.entries(this.graphData).forEach(([code, graphData]) => {
////            datasets_labels.push(code);
////            const dataset_data = [];
////            const formatted_data = []
////            graphData.forEach(function (pt) {
////                if (!labels.includes(pt.label)) {
////                    labels.push(pt.label);
////                }
////                formatted_data.push(`${code}: ${pt.formatted_value || pt.value}`);
////                dataset_data.push(pt.value);
////            })
////            datasets.push({
////                data: dataset_data,
////                label: code,
////                backgroundColor: colors[datasets_labels.length - 1],
////                formatted_data: formatted_data
////            })
////        });
////
////
////        return {
////            type: 'bar',
////            data: {
////                labels: labels,
////                datasets: datasets,
////            },
////            options: {
////                responsive: true,
////                plugins : {
////                    legend: {display: false},
////                    tooltip: {
////                        intersect: false,
////                        position: 'nearest',
////                        caretSize: 0,
////                        callbacks: {
////                            label: (tooltipItem) => {
////                                const { datasetIndex, index } = tooltipItem;
////                                return datasets[datasetIndex].formatted_data[index];
////                            },
////                        },
////                    },
////                },
////                scales: {
////                    x: {
////                        stacked: true,
////                    },
////                    y: {
////                        display: false,
////                        stacked: true,
////                        beginAtZero: true,
////                    }
////                },
////                maintainAspectRatio: false,
////                elements: {
////                    line: {
////                        tension: 0.000001
////                    }
////                }
////            }
////        }
////    }
//
//
//}
//
//dashboard.template = 'account_reports.AccountReportLineCustomizable';
////registry.category("actions").add("account_report", dashboard);
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
////import { AccountReportLine } from "@account_reports/components/account_report/line/line";
////import { loadJS } from "@web/core/assets";
////import { loadBundle } from "@web/core/assets";
////
//////import Chart from "chart.js"; // Ensure Chart.js is imported
////console.log("____________________________111")
////export class CustomAccountReportLine extends AccountReportLine {
////    static template = "account_reports.AccountReportLineCustomizable";
////
////    setup() {
////        super.setup();
////        this.popupVisible = false; // State to control popup visibility
////        this.popupStyle = { display: 'none' }; // Initial style for the popup
////        this.chartInstance = null; // Store the chart instance
//////        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
////        this.onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
////
////
////    }
////
////    get lineClasses() {
////        let classes = super.lineClasses;
////        if (this.props.line.level === 0) {
////            classes += " custom_class_based_on_level"; // Custom class
////        }
////        return classes;
////    }
////
////    showChartPopup() {
////        console.log("____________________________ 222")
////
////        this.popupVisible = true; // Show the popup
////        this.popupStyle = { display: 'block' }; // Change style to show popup
////
////        // Create chart if it doesn't exist yet
////        if (!this.chartInstance) {
////            const ctx = document.getElementById("operation_product_purchase").getContext("2d");
////            const chartData = {
////                labels: ["Label 1", "Label 2", "Label 3"],
////                datasets: [{
////                    label: "Demo Data",
////                    data: [12, 19, 3],
////                    backgroundColor: "rgba(75, 192, 192, 0.2)",
////                    borderColor: "rgba(75, 192, 192, 1)",
////                    borderWidth: 1,
////                }],
////            };
////
////            // Create a new chart
////            this.chartInstance = new Chart(ctx, {
////                type: "bar", // Type of the chart
////                data: chartData,
////                options: {
////                    scales: {
////                        y: {
////                            beginAtZero: true,
////                        },
////                    },
////                },
////            });
////        }
////    }
////
////    hideChartPopup() {
////        this.popupVisible = false; // Hide the popup
////        this.popupStyle = { display: 'none' }; // Change style to hide popup
////    }
////}
