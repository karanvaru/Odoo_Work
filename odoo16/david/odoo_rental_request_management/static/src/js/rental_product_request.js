odoo.define('rental_request_management.rental_product_request', function(require) {
"use strict";
    require('web.dom_ready');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var time = require('web.time');
    var utils = require('web.utils');
    var core = require('web.core');
    var _t = core._t;
    var Dialog = require('web.Dialog');


publicWidget.registry.RentalProductSale = publicWidget.Widget.extend({
        selector: '.rental_product_request_probc',
        events: {
            'click .add_rental_req_probc': '_onClickAddRentalProduct',
            'change .rental_product_templ_select': '_onChangeProductTmpl',
            'click .js_add_rent_qty': '_onClickAddQty',
            'change .rental_product_fade_qty': '_onChangeProductQty',
            'click #o_rental_date_submit': '_onClickSetRentalDates',
            'change .rental_product_variant_select': '_onChangeVariant',
            'change #rental_web_pricelist': '_onChangePricelist',
            'click .reset_rental_so_pricelist': '_onClickResetPricelist',
            'click .remove_order_line_trash': '_onClickRemoveRentalLine',
            'hidden.bs.modal .modal_add_rental_product': '_onHiddenModal',
            'change.datetimepicker': 'onRentalDateChange',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function(){
            var def = this._super.apply(this, arguments);

            this.$rental_product_variant = this.$('select[name="rental_product_variant_select"]');
            this.$variantOptions = this.$rental_product_variant.filter(':enabled').find('option:not(:first)');
            this.$variantPrice = 0.0
            this.$CurrencySymbol = $('select[name="rental_web_pricelist"]').attr("currency-symbol")
            this.$CurrencySymPosition = $('select[name="rental_web_pricelist"]').attr("currency-sym-position")
            
            this._onChangePricelist()
            this._onChangeProductTmpl();
            $(".buy_rental_product_fade").prop('disabled', true);
            $(".rental_web_pricelist_fade_div").addClass("o_hidden")
            $(".probc_select_2").select2()
            
            var today_date = new Date();
            _.each($('.input-group.date'), function(date_field){
                var minDate = $(date_field).data('mindate') || moment({ y: today_date.getFullYear(), m:today_date.getMonth(), d:today_date.getDate() });
                $('#' + date_field.id).datetimepicker({
                    minDate: minDate,
                    useCurrent: false,
                    viewDate: moment(new Date()).hours(0).minutes(0).seconds(0).milliseconds(0),
                    calendarWeeks: true,
                    icons: {
                        time: 'fa fa-clock-o',
                        date: 'fa fa-calendar',
                        next: 'fa fa-chevron-right',
                        previous: 'fa fa-chevron-left',
                        up: 'fa fa-chevron-up',
                        down: 'fa fa-chevron-down',
                    },
                    locale : moment.locale(),
                    allowInputToggle: true,
                    keyBinds: null,
                });
                $('#' + date_field.id).on('error.datetimepicker', function () {
                    return false;
                });
            })

            return def;
        },
        _onChangePricelist: function(ev){
            if ($("#rental_web_pricelist").val() == ""){
                $(".add_rental_req_probc").attr("disabled", true)
                $(".add_prod_disable_warning").removeClass("o_hidden")
            }
            else{
                this.$CurrencySymbol = $('select[name="rental_web_pricelist"] option:selected').attr("currency-symbol")
                this.$CurrencySymPosition = $('select[name="rental_web_pricelist"] option:selected').attr("currency-sym-position")
                $(".add_rental_req_probc").attr("disabled", false)
                $(".add_prod_disable_warning").addClass("o_hidden")
            }
        },
        _prepare_so_common_vals: function(ev){
            return {
                'sale_order_id': $("input[name='rental_sale_order_id']").val()
            }
        },
        _update_args_to_reset_line: function(args){
            var so_common_vals = this._prepare_so_common_vals
            $.extend(true,args,so_common_vals)
            return args
        },
        _ResetSaleorderLine: function(args){
            args = this._update_args_to_reset_line(args)
            ajax.jsonRpc("/json/reset/rental/soline", 'call', args
            ).then(function (data) {
                $(".rental_order_line_div_probc").load(location.href+" .rental_order_line_div_probc>*","")
                $(".rental_request_btn_div").load(location.href+" .rental_request_btn_div", "")
                $(".rental_request_confirmed_div").load(location.href+" .rental_request_confirmed_div")
                $(".rental_pricelist_div").load(location.href+" .rental_pricelist_div")
            });
        },
        _onClickRemoveRentalLine: function(ev){
            var order_line_id = $(ev.currentTarget).attr('line-id')
            this._ResetSaleorderLine({'order_line_id': order_line_id})
        },
        _onClickResetPricelist: function(ev){
            var self = this
            if ($("input[name='rental_sale_order_id']").val() == ''){
                $("#rental_web_pricelist").val('')
                this._onChangePricelist()
            }
            else{
                Dialog.confirm(this, (_t("Are you sure you want to reset pricelist? It will be remove all selected products")), {
                confirm_callback: function () {
                    self._ResetSaleorderLine({'sale_order_id': $("input[name='rental_sale_order_id']").val()})
                },
            });
            }
        },
        _pad2: function (number) {
            return (number < 10 ? '0' : '') + number
        },
        _price_to_str : function (price) {
            var l10n = _t.database.parameters;
            var precision = 2;

            if ($(".decimal_precision").length) {
                precision = parseInt($(".decimal_precision").last().data('precision'));
            }
            var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
            formatted[0] = utils.insert_thousand_seps(formatted[0]);
            return formatted.join(l10n.decimal_point);
        },
        _onClickAddRentalProduct: function(ev){
            var allow_to_add_product = true
            $(".o_rental_customer_contacts").each(function(ev){
                if(!$(this).val() || $(this).val() == " "){
                    $(this).attr("readonly", false)
                    allow_to_add_product = false
                    $(this).css("border","1px solid red")
                    $(this).focus()
                }
                else{
                    $(this).css("border","")
                }
            })
            if (allow_to_add_product == true){
                $(".o_rental_customer_fade").val($(".o_rental_customer_contacts[name='customer_id']").val())
                $(".o_rental_customer_email_fade").val($(".o_rental_customer_contacts[name='email']").val())
                $(".o_rental_customer_phone_fade").val($(".o_rental_customer_contacts[name='phone']").val())
                $("select[name='rental_web_pricelist_fade").val($("select[name='rental_web_pricelist']").val())

                $(".modal_add_rental_product").modal("show");
                this._onChangeProductTmpl()
            }
            
        },
        _onChangeProductTmpl: function (ev){
            var $productTmpl = this.$('select[name="rental_product_templ_select"]');
            var productTmplID = ($productTmpl.val() || 0);
            $('select[name="rental_product_variant_select"]').val("")
            this.$variantOptions.detach();
            var $displayedVariant = this.$variantOptions.filter('[product-tmpl-id=' + productTmplID + ']');
            var nb = $displayedVariant.appendTo(this.$rental_product_variant).show().length;
            this.$rental_product_variant.parent().toggle(nb >= 1);
            $(".variants_desc").addClass("o_hidden")
            this._ChangeRentalPrice()
            this._CheckProductAvailability()

        },
        _prepare_json_rental_product_avail_price_vals: function(ev){
            var product_id = $('select[name="rental_product_variant_select"]').val()
            var start_datetime = $("#input_rental_start_datetime").val()
            var end_datetime = $("#input_rental_end_datetime").val()
            var qty = $(".rental_product_fade_qty").val()
            var days = $(".rental_product_fade_days").val()
            var sale_id = $("input[name='rental_sale_order']").val()
            var pricelist_id = $("select[name='rental_web_pricelist_fade").val()
            
            return {
                'product_id': product_id,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'qty': qty,
                'days': days,
                'sale_id': sale_id,
                'pricelist_id': pricelist_id,
            }
        },
        _CheckProductAvailability: function(ev){
            var self = this
            var price_float = $('select[name="rental_product_variant_select"] option:selected').attr('lst-price')
            var start_datetime = $("#input_rental_start_datetime").val()
            var end_datetime = $("#input_rental_end_datetime").val()
            var qty = $(".rental_product_fade_qty").val()
            var days = $(".rental_product_fade_days").val()
            var json_check_avail_vals = this._prepare_json_rental_product_avail_price_vals(ev)
            json_check_avail_vals.check_availability = true

            ajax.jsonRpc("/json/rental/product/avail/status", 'call', json_check_avail_vals
            ).then(function (data) {
                if (data.reserved == true){
                    $(".o_js_rental_avail_status").addClass('alert-warning')
                    $(".o_js_rental_avail_status").removeClass('alert-success')
                    $("#rental_product_avail_status").html(data.availability_msg)
                    $(".buy_rental_product_fade").attr("disabled", true);
                }
                else{
                    $(".o_js_rental_avail_status").addClass('alert-success')
                    $(".o_js_rental_avail_status").removeClass('alert-warning')
                    $("#rental_product_avail_status").html(data.availability_msg)
                    if (data.first_load_fade == true){
                        $(".buy_rental_product_fade").attr("disabled", true);
                    }
                    else{
                        $(".buy_rental_product_fade").attr("disabled", false);
                    }
                }
            });
        },
        _ChangeRentalPrice: function(ev){
            var self = this
            var json_so_vals = this._prepare_json_rental_product_avail_price_vals(ev)
            json_so_vals.get_product_rental_price = true

            ajax.jsonRpc("/json/rental/product/price", 'call', json_so_vals
            ).then(function (data) {
                self.$variantPrice = data.rental_price
                var rental_price = self._price_to_str(parseFloat(self.$variantPrice))
                
                self.$CurrencySymbol
                self.$CurrencySymPosition
                
                if (self.$CurrencySymPosition == 'before'){
                    rental_price = self.$CurrencySymbol + ' ' + rental_price
                }
                else{
                    rental_price = rental_price + ' ' + self.$CurrencySymbol
                }
                $("span.rental_variant_price").html(rental_price)
                $(".rental_product_fade_price").val(parseFloat(self.$variantPrice))
            });
        },
        _onChangeVariant: function(ev){
            this._ChangeRentalPrice()
            this._CheckProductAvailability()
            var variant_id = $('select[name="rental_product_variant_select"] option:selected').val()
            $(".variants_desc").addClass("o_hidden")
            $("#variant_desc_"+variant_id).removeClass("o_hidden")
        },
        _diff_hours: function (start_datetime, end_datetime, is_weekend=false){

            var new_start_dttime = new Date(start_datetime)
            var new_end_dttime = new Date(end_datetime)
            var diff_hours = Math.abs(new_start_dttime.getTime() - new_end_dttime.getTime()) / 36e5;
            var days = diff_hours/24.00;

            var hrs = parseInt(Number(diff_hours));
            var mins = Math.round((Number(diff_hours)-hrs) * 60);
            if(isNaN(diff_hours)){
                $(".rental_product_fade_hours").val(this._pad2(0)+':'+this._pad2(0))
            }
            else{
                $(".rental_product_fade_hours").val(this._pad2(hrs)+':'+this._pad2(mins))
            }

            if (isNaN(days)){
                $(".rental_product_fade_days").val(this._pad2(0))
            }
            else{
                 $(".rental_product_fade_days").val(days.toFixed(2));
            }

        },
        _onChangeRentalDate: function(ev){
            var start_datetime = $("#input_rental_start_datetime").val()
            var end_datetime = $("#input_rental_end_datetime").val()
            if (start_datetime.length && end_datetime.length){
                this._diff_hours(start_datetime, end_datetime)
                this._ChangeRentalPrice()
                this._CheckProductAvailability()
            }
        },
        _onClickSetRentalDates: function(ev){
            var startDate = new Date($('#start_datetime_fade').val());
            var endDate = new Date($('#end_datetime_fade').val());
div_fade_date_compare_warning
            if ($("#start_datetime_fade").val() == '' || $("#end_datetime_fade").val() == ''){
                $("#div_fade_date_warning").removeClass("o_hidden")
                $("#div_fade_date_warning").html("Startdate Enddate Must be Set")
            }
            else if(startDate > endDate){
                $("#div_fade_date_warning").removeClass("o_hidden")
                $("#div_fade_date_warning").html("End Date Must Be Greater Then Start Date")
            }
            else{
                $("#div_fade_date_warning").addClass("o_hidden")
                var fad_start_date = $("#start_datetime_fade").val()
                var fad_end_date = $("#end_datetime_fade").val()
                $("#input_rental_start_datetime").val(fad_start_date)
                $("#input_rental_end_datetime").val(fad_end_date)
                $("#start_end_date_fade").modal("hide")
                this._onChangeRentalDate()
            }
        },
        onRentalDateChange: function(ev){
            this._onChangeRentalDate()
        },
        _onChangeProductQty: function(ev){
            this._CheckProductAvailability()
        },
        _onClickAddQty: function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.input-group').find("input");
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
            return false;
        },
        _onHiddenModal: function(ev){
            $(ev.currentTarget).find('form').trigger('reset');
            $(".probc_select_2").select2('val', '')
        },
    });
    return publicWidget.registry.RentalProductSale
});
//http://localhost:2020/web/image/product.product/31/image_1920/100x100?unique=e09e335
