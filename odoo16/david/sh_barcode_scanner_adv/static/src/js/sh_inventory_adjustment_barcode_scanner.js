/** @odoo-module **/


import { patch } from 'web.utils';

import { ListRenderer } from "@web/views/list/list_renderer";

const components = { ListRenderer };
import session from 'web.session';

var core = require('web.core');
var QWeb = core.qweb;

const { useExternalListener, useRef, useState, onWillStart } = owl;
import { useService } from "@web/core/utils/hooks";
var Dialog = require('web.Dialog');

import { _t } from "web.core";
patch(components.ListRenderer.prototype, 'sh_barcode_scanner/static/src/js/sh_inventory_adjustment_barcode_scanner.js', {

    setup() {
        this.sh_inventory_adjustment_barcode_scanner_js_class = this.env.config.viewSubType;
        if (this.env.config.viewSubType != 'inventory_report_list') {
            return this._super();
        }
        onWillStart(async () => {
            await this._sh_barcode_scanner_load_widget_data()
        });
        this.state = useState({ value: 1 });

        this._super();


    },


    async _sh_barcode_scanner_load_widget_data() {
        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_get_widget_data', {});
        this.sh_barcode_scanner_user_is_stock_manager = result.user_is_stock_manager;
        this.sh_barcode_scanner_user_has_stock_multi_locations = result.user_has_stock_multi_locations;
        this.sh_barcode_scanner_locations = result.locations;
        this.sh_inven_adjt_barcode_scanner_auto_close_popup = result.sh_inven_adjt_barcode_scanner_auto_close_popup;
        this.sh_inven_adjt_barcode_scanner_warn_sound = result.sh_inven_adjt_barcode_scanner_warn_sound;
        this.sh_barcode_scanner_location_selected = localStorage.getItem('sh_barcode_scanner_location_selected') || '';
        this.sh_scan_negative_stock = localStorage.getItem('sh_barcode_scanner_is_scan_negative_stock') || '';
    },


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * This method is called when barcode is changed above tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_change_sh_barcode_scanner_stock_quant_tree_input_barcode: async function (ev) {
        var self = this;
        var barcode = $(ev.currentTarget).val();
        var location_id = false;
        var scan_negativstore_stock = false;
        var location_name = '';
        var scan_negative_stock = $(ev.currentTarget).closest('.js_cls_sh_barcode_scanner_scanning_wrapper').find('.scan_negative_stock_cls').prop('checked');
        var $location_select = $(ev.currentTarget).closest('.js_cls_sh_barcode_scanner_scanning_wrapper').find('.js_cls_sh_barcode_scanner_location_select');
        if ($location_select.length) {
            location_id = $location_select.val();
            location_name = $location_select.find("option:selected").text();
        }
        if (location_id) {
            location_id = parseInt(location_id);
        }

        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_search_stock_quant_by_barcode', {
            'barcode': barcode,
            'location_id': location_id,
            'location_name': location_name,
            'scan_negative_stock': scan_negative_stock,
        });



        if (result.result) {
            var message = _t(result.message);

            // in order to compatible both mobile view and desktop view.
            if ($(document).find(".o_searchview_input").length) {
                $(document).find(".o_searchview_input").focus();
                const kevt = new window.KeyboardEvent('keydown', { key: "Enter" });
                document.querySelector('.o_searchview_input').dispatchEvent(kevt);
            } else {
                var th_write_date = $(document).find('th[data-name="write_date"]');
                if (th_write_date.length) {
                    th_write_date.click();
                    th_write_date.click();
                }
            }

            var msg = $('<div class="alert alert-info mt-3" role="alert">' + message + ' </div>')
            $(document).find('.js_cls_alert_msg').html(msg);

        } else {
            var message = _t(result.message);
            var msg = $('<div class="alert alert-danger mt-3" role="alert">' + message + ' </div>')
            $(document).find('.js_cls_alert_msg').html(msg);
            // Play Warning Sound
            if (self.sh_inven_adjt_barcode_scanner_warn_sound) {
                var src = "/sh_barcode_scanner_adv/static/src/sounds/error.wav";
                $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
            }

        }
        $(document).find('.js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode').val('');
        // ---------------------------------------
        // auto focus barcode input            
        $(document).find('.js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode').focus();
        $(document).find('.js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode').focus().keydown();
        $(document).find(".js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode").focus()
        $(document).find('.js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode').trigger({ type: 'keydown', which: 13 });

    },




    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * This method is called when barcode is changed above the tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_click_js_cls_sh_barcode_scanner_stock_quant_tree_btn_apply: async function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var self = this;
        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_stock_quant_tree_btn_apply', {});
        var error = false;
        var title = _t("Something went wrong");
        if (result.result) {
            title = _t("Inventory Succeed");
            // self.trigger_up('reload');
            if ($(document).find(".o_searchview_input").length) {
                $(document).find(".o_searchview_input").focus();
                const kevt = new window.KeyboardEvent('keydown', { key: "Enter" });
                document.querySelector('.o_searchview_input').dispatchEvent(kevt);
            } else {
                var th_write_date = $(document).find('th[data-name="write_date"]');
                if (th_write_date.length) {
                    th_write_date.click();
                    th_write_date.click();
                }
            }

        } else {
            title = _t("Something went wrong");
            error = true;
        }
        var message = _t(result.message);
        var dialog = new Dialog(this, {
            title: title,
            $content: $('<p>' + message + '</p>')
        });
        dialog.open();

        // auto close dialog.
        if (error && self.sh_inven_adjt_barcode_scanner_auto_close_popup > 0) {
            setTimeout(function () {
                if (dialog) {
                    dialog.close();
                }
            }, self.sh_inven_adjt_barcode_scanner_auto_close_popup);
        }
        // Play Warning Sound
        if (error && self.sh_inven_adjt_barcode_scanner_warn_sound) {
            var src = "/sh_barcode_scanner_adv/static/src/sounds/error.wav";
            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
        }


    },


    /**
     * This method is called when location is changed above tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_change_sh_barcode_scanner_location_select: async function (ev) {
        ev.stopPropagation();
        var location = $(ev.currentTarget).val();
        localStorage.setItem('sh_barcode_scanner_location_selected', location);
        this.sh_barcode_scanner_location_selected = localStorage.getItem('sh_barcode_scanner_location_selected') || '';

    },

    on_change_scan_negative_stock_cls: async function (ev) {
        ev.stopPropagation();
        var self = this;
        var scan_negative_stock = $(ev.currentTarget).prop('checked');
        if (scan_negative_stock) {
            scan_negative_stock = 'true';
        } else {
            scan_negative_stock = 'false';
        }
        self.sh_scan_negative_stock = scan_negative_stock;
        localStorage.setItem('sh_barcode_scanner_is_scan_negative_stock', scan_negative_stock);

    },


});




