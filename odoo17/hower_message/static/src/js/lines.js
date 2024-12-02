/** @odoo-module **/
console.log("+++++++++++++++++++++++++  Lines")
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class AccountReportLineCustomizableCustom extends Component {
    // Method to handle hover-in (mouseenter)
    onMouseEnter() {
        console.log("+++++++++++++++++++++++++  mouse click")
        console.log("Mouse entered");
        const popup = this.el.querySelector('.popup');
        if (popup) {
            popup.style.display = 'block';  // Show the popup
        }
    }

    // Method to handle hover-out (mouseleave)
    onMouseLeave() {
        console.log("Mouse left");
        const popup = this.el.querySelector('.popup');
        if (popup) {
            popup.style.display = 'none';  // Hide the popup
        }
    }
}

AccountReportLineCustomizableCustom.template = "hower_message.AccountReportLineCustomizable_custom";

// Register the component
registry.category("components").add("AccountReportLineCustomizableCustom", AccountReportLineCustomizableCustom);



///** @odoo-module **/
//console.log("___________________________")
//import { Component } from "@odoo/owl";
//import { registry } from "@web/core/registry";
//import { AccountReportLine } from "@account_reports/components/account_report/line/line";
//
////class AccountReportLine extends Component {
//export class CustomAccountReportLine extends AccountReportLine {
//      onMouseEnter() {
//        console.log("Mouse Entered");
//        // Add your custom logic, like showing a popup or tooltip
//    }
////    onClickButton() {
////        alert("Button Clicked!");
////        // Add your custom logic here
////    }
//}
//
//CustomAccountReportLine.template = "hower_message.AccountReportLineCustomizable_custom";
//
////registry.category("components").add("components", AccountReportLine);












///** @odoo-module */
//console.log("_________________________ js")
//import { AccountReportLine } from "@account_reports/components/account_report/line/line";
////import Chart from "chart.js";
//   import { FormView } from "@web/views/form/form_view";
//import { FormController } from "@web/views/form/form_controller";
////    import { FormView } from "@web/views/form/form_view";
//    import { useService } from "@web/core/utils/hooks";
//    import { patch } from "@web/core/utils/patch";
//
//
//patch(FormController.prototype, {
//        setup(){
//            super.setup();
//            this.rpc = useService("rpc");
//        },
//          onClickButton() {
//        alert("Button Clicked!");
//        // Add your custom logic here
//    }
////        _onButtonClicked(event) {
////            console.log("_________________________")
////            console.log(event);
////        }
//    });
//
//
//
//
////
////export class CustomAccountReportLine extends AccountReportLine {
////    get lineClasses() {
////        console.log("__________________________________________")
////        let classes = super.lineClasses;
////
////        if (this.props.line.level === 0) {
////            classes += " custom_class_based_on_level";
////        }
////        return classes;
////    }
////
////    OpenChart(ev) {
////    console.log("_+++++++++++++++++++++++++++++++")
//////            var index = [...ev.currentTarget.parentNode.children].indexOf(ev.currentTarget);
//////            if (ev.currentTarget.tagName === 'TH') {
//////                index += 1;
//////            }
//////            this.el.querySelectorAll('td:nth-child(' + (index + 1) + ')').forEach(elt => elt.classList.add('o_cell_hover'));
////        }
////
////
////    showChartPopup(ev) {
////        console.log("________________________ call")
////        const canvas = document.getElementById("operation_product_purchase");
////        console.log("________________________ canvas",canvas)
////
////        // Check if the canvas is available
////        if (canvas) {
////            const ctx = canvas.getContext("2d");
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
////            new Chart(ctx, {
////                type: "bar", // Change this to the type of chart you want
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
////}
