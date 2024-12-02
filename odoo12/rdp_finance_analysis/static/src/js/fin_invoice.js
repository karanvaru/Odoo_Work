odoo.define('finance_analysis.finance_report', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var rpc = require('web.rpc');
   var QWeb = core.qweb;
   var ReportCustom = AbstractAction.extend({
   template: 'finance_invoice_report',
       events: {
       },
       init: function(parent, action) {
           this._super(parent, action);
       },
       start: function() {
           var self = this;
           //alert("++working++")
           self.load_data();
       },
       load_data: function () {
           var self = this;
                   var self = this;
                   self._rpc({
                       model: 'finance.analysis.report',
                       method: 'get_finance_analysis_data',
                       args: [],
                   }).then(function(datas) {
                   console.log("+++++++++++++++data", datas)
                       self.$('.table_view').html(QWeb.render('finance_invoice_table', {
                                  report_lines : datas,
                       }));
                   });
           },
   });
   core.action_registry.add("finance_report", ReportCustom);
   return ReportCustom;
});