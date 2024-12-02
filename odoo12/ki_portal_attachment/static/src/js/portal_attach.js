odoo.define('ki_portal_attachment.multi_attachment', function (require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');

    var qweb = core.qweb;

    var PortalChatter = require('portal.chatter').PortalChatter;

    PortalChatter.include({
        events: _.extend({}, PortalChatter.prototype.events, {
            "click .o_portal_chatter_attachment_btn" : "_onClickbutton_attach",
        }),
        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function(){
                this.$('.o_portal_chatter_file_input')[0].value = false;
            });
        },
        _loadTemplates: function(){
            return $.when(this._super(), ajax.loadXML('/ki_portal_attachment/static/src/xml/portal_attachment.xml', qweb));
        },
        _onClickbutton_attach: function(){
            this.$('.o_portal_chatter_file_input').click();
        }
    });
})