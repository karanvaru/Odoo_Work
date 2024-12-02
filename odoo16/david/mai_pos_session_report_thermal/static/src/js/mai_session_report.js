odoo.define('mai_pos_session_report_thermal.PosSessionPDFReportButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PosSessionPDFReportButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this.env;
            var pos_session_id = self.pos.pos_session.id;
            this.env.legacyActionManager.do_action(
                'mai_pos_session_report_thermal.action_report_session', {
                additional_context: {active_ids: [pos_session_id]},
            });
        }
    }
    PosSessionPDFReportButton.template = 'PosSessionPDFReportButton';

    ProductScreen.addControlButton({
        component: PosSessionPDFReportButton,
        condition: function() {
            return this.env.pos.config.do_session_report;
        },
    });

    Registries.Component.add(PosSessionPDFReportButton);

    return PosSessionPDFReportButton;

});


