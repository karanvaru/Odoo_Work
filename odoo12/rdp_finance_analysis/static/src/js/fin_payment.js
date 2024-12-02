odoo.define('finance_analysis.finance_report', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var ajax = require('web.ajax');
   var rpc = require('web.rpc');
   var Widget = require('web.Widget');
   var framework = require('web.framework');
   var QWeb = core.qweb;   
   var session = require('web.session');
   var _t = core._t;
   var ReportCustom = AbstractAction.extend({
   template: 'finance_payment_report',
       events: {
       //'click .expand_column': '_onClickAction',
       'click .o_payment_unfoldable': '_onClickUnfold',
       'click .o_payment_foldable': '_onClickFold',
       },
       init: function(parent, action) {
           this._super(parent, action);
       },
       start: function() {
           var self = this;
           //alert("++working done by kp++")
           self.load_data();
       },
       load_data: function () {
           var self = this;
                   var self = this;
                   self._rpc({
                       model: 'finance.analysis.report',
                       method: 'get_finance_analysis_inbound_data',
                       args: [],
                   }).then(function(datas) {
                   console.log("+++++++++++++++data", datas)
                       self.$('.table_view').html(QWeb.render('finance_payment_table',{
                            report_lines : datas,
                       }));
                   });
        },
        // get_operations: function(event) {
        //     var self = this;
        //     var $parent = $(event.currentTarget).closest('tr');            
        //     return this._rpc({
        //           model: 'finance.analysis.report',
        //           method: 'get_operations',
        //       })
        //       .then(function (result) {
        //           self.render_html(event, $parent, result);
        //       });
        //     },

        _onClickUnfold: function (ev) {
            var self = this;
            var redirect_function = $(ev.currentTarget).data('function');
        },
        _onClickFold: function (ev) {
            this._removeLines($(ev.currentTarget).closest('tr'));
            $(ev.currentTarget).toggleClass('o_payment_foldable o_payment_unfoldable fa-caret-right fa-caret-down');
        },
        // _onClickAction: function (ev) {            
        //     ev.preventDefault();            
        //     return this.do_action({
        //         type: 'ir.actions.act_window',
        //         res_model: $(ev.currentTarget).data('model'),                
        //         //res_id : $(ev.currentTarget).data('res-id'),
        //         //res_id : name,
        //         views: [[false, 'form']],
        //         view_mode: 'form',
        //         view_type: 'form',
        //         target: 'current',
        //     });
        // },

   });
   core.action_registry.add("finance_report", ReportCustom);
   return ReportCustom;
});