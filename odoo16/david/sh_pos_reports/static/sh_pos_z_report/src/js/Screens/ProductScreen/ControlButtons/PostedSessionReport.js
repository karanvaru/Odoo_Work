odoo.define('sh_pos_z_report.PostedSessionReport', function(require) {
    'use strict';

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");
    const rpc = require("web.rpc");
    var { Gui } = require('point_of_sale.Gui');
    
    class PostedSessionReport extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick(){
            var self = this;
            if(self && self.env && self.env.pos && self.env.pos.db && self.env.pos.db.posted_session_ids && self.env.pos.db.posted_session_ids.length > 0){
                let { confirmed } = await Gui.showPopup("ZReportPostedSessionOptionPopup");
                if (confirmed) {
                } else {
                    return;
                }
            }else{
                alert("No Any Posted Session Found.")
            }
        }
    }
    PostedSessionReport.template = "PostedSessionReport";

    ProductScreen.addControlButton({
        component: PostedSessionReport,
        condition: function () {
            if(!this.env.pos.config.module_pos_hr){
                return this.env.pos.config.sh_enable_z_report && this.env.pos.user.sh_is_allow_z_report && this.env.pos.config.sh_allow_posted_session_report;
            }else{
                if(this.env.pos.get_cashier() && this.env.pos.get_cashier().name){
                    return this.env.pos.get_cashier().sh_is_allow_z_report && this.env.pos.config.sh_enable_z_report && this.env.pos.config.sh_allow_posted_session_report
                }else{
                    return false
                }
                
            }
            return this.env.pos.config.sh_allow_posted_session_report;
        },
    })

    Registries.Component.add(PostedSessionReport)

    return PostedSessionReport;
    
});
