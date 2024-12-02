odoo.define("sh_pos_multi_branch.chrome", function (require) {
    "use strict";
    
    const Chrome = require("point_of_sale.Chrome");
    const Registries = require("point_of_sale.Registries");

    const PosResChrome = (Chrome) =>
        class extends Chrome {
            async start() {
                await super.start();
                if(this.env.pos.config.iface_start_categ_id && this.env.pos.config.iface_start_categ_id[0] && this.env.pos.db.category_by_id && !this.env.pos.db.category_by_id[this.env.pos.config.iface_start_categ_id[0]]){
                    this.env.pos.selectedCategoryId = 0;
                }
            }
        };
    Registries.Component.extend(Chrome, PosResChrome);
        
});
