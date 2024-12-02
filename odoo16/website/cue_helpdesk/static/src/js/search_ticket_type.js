odoo.define('cue_helpdesk.search_ticket_type', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var DynamicSnippetTicket= publicWidget.Widget.extend({
		selector: '.cue_helpdesk_form',
		start: function() {
		    var self = this;
		    let category_ticket = self.el.querySelector('#contact53');
		    $('#contact51').on('change', function(ev) {
                var category_id = $(this).val();
                self._rpc({
                    route: '/ticket_type/',
                    params: {
                        'ticket_type': category_id
                    }
                }).then(html => {
                    category_ticket.innerHTML = ""
                    category_ticket.innerHTML = html.message
                })
			})
		},
    });
	publicWidget.registry.DynamicSnippetTicket = DynamicSnippetTicket;
});