odoo.define("cue_website_profile.signup", function (require) {
    "use strict";

    require('web.dom_ready');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    $(document).ready(function(){
        $('.signup_send_mail').show();
        var login = $('#login').val();
        if (login){
            $('.oe_signup_form').show();
           	$('.signup_send_mail').hide();
        }

        $('.send_mail_btn').on('click', function (ev){
            var QueryString = (new URL(location.href)).searchParams.get('redirect');
            var email = $('#email').val();
            var email_val = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
            if(!email_val.test(email)){
                $('.email_validation').show();
            }
            else{
                $('.thanks_div').show();
                $('.email_validation').hide();
                var emailId = $('#email').val();
                ajax.jsonRpc('/signup_mail', 'call',{
                    'user_email':emailId,
                    'QueryString':QueryString,
                })
            }
        });
    });
});
