/** @odoo-module **/

import { WarningDialog } from "@web/core/errors/error_dialogs";

import { patch } from 'web.utils';

const components = { WarningDialog };

patch(components.WarningDialog.prototype, 'sh_barcode_scanner_adv/static/src/js/dialog_sound.js', {

	
	setup(...args) {

    		this._super(...args)      

            /****************************************************************
             * softhealer custom code start here
             * SH_BARCODE_SCANNER_ is a code to identi
             * fy that message is coming from barcode scanner.
             * here we remove code for display valid message and play sound.
             * ***************************************************************
             */
    		var self = this;		
		
            if (self.message.length) {
                //for auto close popup start here
                var auto_close_ms = self.message.match("AUTO_CLOSE_AFTER_(.*)_MS&");
                if (auto_close_ms && auto_close_ms.length == 2) {
                    auto_close_ms = auto_close_ms[1];
                    var original_msg = "AUTO_CLOSE_AFTER_" + auto_close_ms + "_MS&";
                    self.message = self.message.replace(original_msg, "");
                    setTimeout(function () {
                        $(".o_technical_modal").find('button:contains("Ok")').trigger("click");
                    }, auto_close_ms);
                }
                //for auto close popup ends here
                //for play sound start here
                //if message has SH_BARCODE_SCANNER_
                var str_msg = self.message.match("SH_BARCODE_SCANNER_");
                if (str_msg) {
                    //remove SH_BARCODE_SCANNER_ from message and make valid message
                    self.message = self.message.replace("SH_BARCODE_SCANNER_", "");
                    //play sound
                    var src = "/sh_barcode_scanner_adv/static/src/sounds/error.wav";
                    $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                }
                //for play sound ends here
            }
            //softhealer custom code ends here		
		

    }
	
	
	
});





