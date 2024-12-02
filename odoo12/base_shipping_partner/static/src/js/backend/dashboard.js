odoo.define('base_shipping_partner.backend.dashboard', function (require) {
    'use strict';

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var Dashboard = Widget.extend(ControlPanelMixin, {
        template: 'base_shipping_partner.ShippingDashboardMain',

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['base_shipping_partner.dashboard_visits'];
        },

        start: function () {
            var self = this;
            return this._super().then(function () {
                self.render_dashboards();
            });
        },

        render_dashboards: function () {
            var self = this;
            _.each(this.dashboards_templates, function (template) {
                self.$('.o_website_dashboard_content').append(QWeb.render(template, {widget: self}));
            });
        }
    });
    core.action_registry.add('backend_shipping_dashboard', Dashboard);
    return Dashboard;
});
