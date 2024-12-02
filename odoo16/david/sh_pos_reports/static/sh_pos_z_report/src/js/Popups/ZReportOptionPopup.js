odoo.define("sh_pos_z_report.ZReportOptionPopup", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const rpc = require("web.rpc");
    
    class ZReportOptionPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
        async print() {
            var self = this;
            var statementPrintValue = $("input[name='print_option']:checked").val();

            if (statementPrintValue) {
                if (statementPrintValue == "pdf") {
                    await self.env.legacyActionManager.do_action('sh_pos_reports.pos_z_report_detail', {
                        additional_context: {
                            active_ids: [this.env.pos.pos_session.id],
                        },
                    });
                } else if (statementPrintValue == "receipt" && self.env.pos.pos_session && self.env.pos.pos_session.id) {
                    await rpc.query({
                        model: 'pos.session',
                        method: 'get_session_detail',
                        args: [self.env.pos.pos_session.id],
                    }).then(async function (session_detail) {
                        if(session_detail){
                            self.env.pos.is_z_report_receipt = true
                            self.env.pos.session_data = session_detail
                            self.showScreen("ReceiptScreen");
                        }
                    });
                }
            }     
            this.cancel()       
        }
    }
    ZReportOptionPopup.template = "ZReportOptionPopup";
    Registries.Component.add(ZReportOptionPopup);

    return ZReportOptionPopup
});
