odoo.define('cue_helpdesk.file_validation', function(require) {
	'use.strict';
	var ajax = require('web.ajax');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	require('web.dom_ready');
    var rpc = require('web.rpc');
    var _t = core._t;


	var DynamicHelpdeskValidation= publicWidget.Widget.extend({
		selector: '.cue_helpdesk_form',
		start: function() {
            var self = this

            function logSubmit(event) {
                console.log("+222222222222222222222222")
                const fi = document.getElementById('upload_file');
                document.getElementById('helpdesk_file_upload').innerHTML = "";
                if (fi.files.length > 0) {
                    for (var i = 0; i <= fi.files.length - 1; i++) {
                        const fsize = fi.files.item(i).size;
                        const file = Math.round((fsize / 1024));
                        if (file >= 5096) {
                            document.getElementById('helpdesk_file_upload').innerHTML = "Upto 5MB size.";
                            event.preventDefault();
                        }
                    }
                }
            }
            const form = document.getElementById("Ticket_form");
            console.log("+++++++Aaaaaaaaaaaaaaa",form)
            if(form){
                console.log("+11111111111111111111111111")
                form.addEventListener("submit", logSubmit);
            }
        },
    });
    publicWidget.registry.DynamicHelpdeskValidation = DynamicHelpdeskValidation ;
});
