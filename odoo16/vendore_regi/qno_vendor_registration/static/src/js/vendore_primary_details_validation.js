odoo.define("qno_vendor_registration.reason_field", function (require) {
    "use strict";

    $(document).ready(function(){
        $('#is_other_bank').on('change', function (ev){
            var additionalBankDetails = document.querySelector('#other_bank_account');
            var isOtherBankCheckbox = document.getElementById('is_other_bank');

            if (isOtherBankCheckbox.checked) {
                $('#other_bank_account').show()
            }
            else {
                $('#other_bank_account').hide()
            }
        })
        $('#msme_type').on('change', function () {
            var msmeNoInput = $('#msme_no');
            if (this.value !== "none") {
                $('#msme_no').show();
            }
            else {
                $('#msme_no').hide();
            }
        });
    });
});