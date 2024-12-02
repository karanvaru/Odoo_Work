//// static/src/js/custom_script.js
//function close_wizard() {
//    var wizard = $('.modal:visible');
//    wizard.modal('hide');
//}
//odoo.define('rdp_vendor_registration_form.custom_script', function (require) {
//    'use strict';
//
//    var core = require('web.core');
//    var _t = core._t;
//
//    function close_wizard() {
//        // Add logic to close the wizard if needed
//        console.log('Closing the wizard');
//    }
//
//    // Export the function to make it accessible
//    return {
//        close_wizard: close_wizard,
//    };
//});

//________________________  after gst portal verfication  is valid applicant data fill automatically in our vendor form_______
//<?xml version="1.0" encoding="utf-8"?>
//<odoo>
//    <template id="assets_backend" name="Your Module Assets" inherit_id="web.assets_backend">
//        <xpath expr="." position="inside">
//            <script type="text/javascript" src="/your_module/static/src/jquery.min.js"></script>
//            <script type="text/javascript" src="/your_module/static/src/vendor_registration_form.js"></script>
//        </xpath>
//    </template>
//</odoo>

//odoo.define('your_module.vendor_registration_form', function (require) {
//    'use strict';
//
//    var publicWidget = require('web.public.widget');
//
//    publicWidget.registry.VendorRegistrationForm = publicWidget.Widget.extend({
//        selector: '.o_web_form',
//        events: {
//            'change input[name="vat"]': '_onGstNumberChange',
//        },
//
//        _onGstNumberChange: function (ev) {
//            var gstNumber = $(ev.currentTarget).val();
//
//            // Make an Ajax request to your Odoo backend to validate and fetch GST data
//            this._rpc({
//                model: 'res.partner',
//                method: 'validate_and_fetch_gst_data',
//                args: [gstNumber],
//            }).then(function (result) {
//                // Update form fields with GST data if available
//                if (result && result.valid) {
//                    $('input[name="name"]').val(result.name || '');
//                    $('input[name="email"]').val(result.email || '');
//                    // Add more fields as needed
//
//                    // Optionally, disable GST number field after successful validation
//                    $('input[name="vat"]').prop('disabled', true);
//                } else {
//                    // Handle invalid GST number
//                    console.error('Invalid GST number');
//                }
//            });
//        },
//    });
//});
//
