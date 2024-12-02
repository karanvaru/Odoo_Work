odoo.define("website_helpdesk_support_ticket_extend.reason_field", function (require) {
    "use strict";

    $(document).ready(function(){
        $('.click_radio').on('change', function() {
            var is_varify = $("input[name='varify']:checked").val();
            if (is_varify === 'no'){
                $('.varify_reason').show();
                document.getElementById("reason").required = true;
            }
            if (is_varify === 'yes'){
                $('.varify_reason').hide();
                document.getElementById("reason").required = false;
            }
        });
    });
});