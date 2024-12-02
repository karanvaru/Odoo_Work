odoo.define('cue_website.hide_show_fields', function (require) {
    "use strict";

    require('web.dom_ready');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function(){
    function logSubmit(event) {
        const fi = document.getElementById('cv');
        const fname = document.getElementById('fname');
        document.getElementById('file_upload_validation').innerHTML = "";
        if (fi.files.length > 0) {
            for (var i = 0; i <= fi.files.length - 1; i++) {
                const fsize = fi.files.item(i).size;
                const file = Math.round((fsize / 1024));
                if (file >= 5096) {
                    document.getElementById('file_upload_validation').innerHTML = "PDF Only. Upto 5MB size.";
                    event.preventDefault();
                }
            }
        }
    }
    const form = document.getElementById("academy_form");
    if(form){
        form.addEventListener("submit", logSubmit);
    }
   });
});
