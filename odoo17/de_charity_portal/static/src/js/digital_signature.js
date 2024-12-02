/** @odoo-module **/
import dom from "@web/legacy/js/core/dom";
import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";


publicWidget.registry.SignatureWidget = PortalSidebar.extend({
    selector: '.confidential_policy',
    events: {
         'click .clear-signature': '_onClearSignature',
         'click .save-signature': '_onSaveSignature',
         'click .confirm-data': '_onConfirmData',
    },
    start: function () {
    var partner = $('#id_partner').val();
     const thanks_div = document.getElementById('thanks_page_id');
        const content_div = document.getElementById('content_div');
             jsonrpc('/thanks_page', {
            'partner': partner,
        }).then((data) => {
            if (data['data']['is_content'] == false) {
            thanks_div.style.display = 'none';
            content_div.style.display = 'block';
        }
             if (data['data']['is_content'] == true) {
            thanks_div.style.display = 'block';
            content_div.style.display = 'none';
        }

        })
        this._super.apply(this, arguments);
        this._initSignaturePad();
        this.orm = this.bindService("orm");
        this.notification = this.bindService("notification");
    },
    _initSignaturePad: function () {
        const canvas = this.el.querySelector('canvas');
        this.signaturePad = new SignaturePad(canvas, {
            backgroundColor: 'rgba(255, 255, 255, 0)',
            penColor: 'black',
        });
    },
    _onClearSignature: function () {
        this.signaturePad.clear();
    },
    _onConfirmData: function () {
        var partner = $('#id_partner').val();
        var new1 = $('#pid').val('1');
        const thanks_div = document.getElementById('thanks_page_id');
        const content_div = document.getElementById('content_div');

        thanks_div.style.display = 'block';
        content_div.style.display = 'none';
         jsonrpc('/new_page', {
            'partner': partner,
        })
    },
    _onSaveSignature: function () {
        var partner = $('#id_partner').val();
        if (this.signaturePad.isEmpty()) {
                return this.notification.add(_t("Please provide a signature first"), {
                type: 'warning',
            });
//            alert("Please provide a signature first.");
        } else {
            const dataURL = this.signaturePad.toDataURL();
            this._saveSignature(dataURL,partner);
        }
    },
    _saveSignature: function (dataURL,partner) {
        jsonrpc('/save_signature', {
            'signature': dataURL,
            'partner': partner,
        })
    },
});

return publicWidget.SignatureWidget;
