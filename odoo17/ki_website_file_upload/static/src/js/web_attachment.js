/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, markup, xml } from "@odoo/owl";
import publicWidget from "@web/legacy/js/public/public_widget";
import { KeepLast } from "@web/core/utils/concurrency";

publicWidget.registry.MailGroupMessage = publicWidget.Widget.extend({
selector: '.file_upload_website',
    read_events: {
        'click .hide_show_attach': 'hide_show_attach',
        'click .delete_attach': 'delete_attach',
		'click .sale_attach_class': 'onClick_attach'
    },
    init: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },

     hide_show_attach: function (ev) {
         $('.hide_show_table').toggleClass('o_hidden');
         $('.hide_show_attach').trigger('change');
     },

    async onClick_attach(ev) {
      	var sale_id = ev.currentTarget.name;
      	var self = this
        var attachment = $("#sale_attachment")[0].files[0];
        if (attachment){
            var reader = new FileReader();
            reader.readAsDataURL(attachment);
            reader.onloadend = function() {
                var base64data = reader.result;
                var data = base64data.split(",");
                var attachment_value = {
                    'name': attachment.name,
                    'datas': data[1],
                    'res_model': 'sale.order',
                    'res_id': sale_id,
                }
                self.rpc("/web/dataset/call_kw/sale.order/website_upload_attach", {
                    model: 'sale.order',
                    method: 'website_upload_attach',
                    args: [attachment_value],
                    kwargs: {}
                }).then(function (attachment){
                    setTimeout("location.reload();", 100);
                })
            }
        }
        $('#upload_sale_attachment').trigger('change');
    },

    async delete_attach(ev) {
        var self = this
      	var attach_id = ev.currentTarget.id;
       	self.rpc("/web/dataset/call_kw/sale.order/website_delete_attach", {
            model: 'sale.order',
            method: 'website_delete_attach',
            args: [attach_id],
            kwargs: {}
        }).then(function (attachment){
            setTimeout("location.reload();", 100);
            $('.hide_show_table').toggleClass('table hide_show_table');
        });
        $('.delete_attach').trigger('change');
	}
});