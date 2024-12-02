odoo.define('sh_pos_z_report.ShPosZReport', function(require) {
    'use strict';

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");
    const rpc = require("web.rpc");
    var { Gui } = require('point_of_sale.Gui');
    
    class ShPosZReport extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick(){
            var self = this;
            if(self && self.env && self.env.pos && self.env.pos.config && self.env.pos.config.sh_allow_z_report_type && self.env.pos.config.sh_allow_z_report_type == 'pdf'){
                await self.env.legacyActionManager.do_action('sh_pos_reports.pos_z_report_detail', {
                    additional_context: {
                        active_ids: [this.env.pos.pos_session.id],
                    },
                });
            }else if(self && self.env && self.env.pos && self.env.pos.config && self.env.pos.config.sh_allow_z_report_type && self.env.pos.config.sh_allow_z_report_type == 'receipt' && self.env.pos.pos_session && self.env.pos.pos_session.id){
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
            }else if(self && self.env && self.env.pos && self.env.pos.config && self.env.pos.config.sh_allow_z_report_type && self.env.pos.config.sh_allow_z_report_type == 'both' && self.env.pos.pos_session && self.env.pos.pos_session.id){
                let { confirmed } = await Gui.showPopup("ZReportOptionPopup");
                if (confirmed) {
                } else {
                    return;
                }
            }
        }
    }
    ShPosZReport.template = "ShPosZReport";

    ProductScreen.addControlButton({
        component: ShPosZReport,
        condition: function () {
            if(!this.env.pos.config.module_pos_hr){
                return this.env.pos.config.sh_enable_z_report && this.env.pos.user.sh_is_allow_z_report;
            }else{
                if(this.env.pos.get_cashier() && this.env.pos.get_cashier().name){
                    return this.env.pos.get_cashier().sh_is_allow_z_report && this.env.pos.config.sh_enable_z_report
                }else{
                    return false
                }
                
            }
        },
    })

    Registries.Component.add(ShPosZReport)

    return ShPosZReport;
    
});
