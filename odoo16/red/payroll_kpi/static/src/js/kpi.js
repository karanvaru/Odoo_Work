odoo.define('payroll_kpi.list_renderer_extension', function (require) {
    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderRow: function (record) {
            var $row = this._super.apply(this, arguments);
            if (this.view.arch.attrs.name === 'payroll_kpi_ids') {
                $row.find('.o_list_record_remove').remove();
            }
            return $row;
        },
    });
});

