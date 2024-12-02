odoo.define("sh_pos_z_report.ZReportPostedSessionOptionPopup", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const rpc = require("web.rpc");
    
    class ZReportPostedSessionOptionPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
        async print(){
            var self = this;
            var sessionSelection = parseInt($(".sh_session_selection").val());
            if(self.env.pos.config.sh_allow_z_report_type == 'both'){
                var statementPrintValue = $("input[name='print_option']:checked").val();
                if(sessionSelection && statementPrintValue){
                    if (statementPrintValue == "pdf") {
                        await self.env.legacyActionManager.do_action('sh_pos_reports.pos_z_report_detail', {
                            additional_context: {
                                active_ids: [sessionSelection],
                            },
                        });
                    } else if (statementPrintValue == "receipt") {
                        await rpc.query({
                            model: 'pos.session',
                            method: 'get_session_detail',
                            args: [sessionSelection],
                        }).then(async function (session_detail) {
                            if(session_detail){
                                self.env.pos.is_z_report_receipt = true
                                self.env.pos.session_data = session_detail
                                self.showScreen("ReceiptScreen");
                            }
                        });
                    }
                }
            }else if(self.env.pos.config.sh_allow_z_report_type == 'pdf'){
                await self.env.legacyActionManager.do_action('sh_pos_reports.pos_z_report_detail', {
                    additional_context: {
                        active_ids: [sessionSelection],
                    },
                });
            }else if(self.env.pos.config.sh_allow_z_report_type == 'receipt'){
                await rpc.query({
                    model: 'pos.session',
                    method: 'get_session_detail',
                    args: [sessionSelection],
                }).then(async function (session_detail) {
                    if(session_detail){
                        self.env.pos.is_z_report_receipt = true
                        self.env.pos.session_data = session_detail
                        self.showScreen("ReceiptScreen");
                    }
                });
            }
            this.cancel()
        }
    }
    ZReportPostedSessionOptionPopup.template = "ZReportPostedSessionOptionPopup";
    Registries.Component.add(ZReportPostedSessionOptionPopup);

    return ZReportPostedSessionOptionPopup
});
