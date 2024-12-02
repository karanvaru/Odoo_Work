odoo.define('warranty_management.warranty_reg', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');

    $(document).ready(function () {

        $('.warranty_reg').on('click', function (e) {
            var orderLine = parseInt($(this).find('.ord_line').first().val(), 10);
            ajax.jsonRpc("/warranty/modal/", 'call', { 'ol': orderLine, 'modal': 'wk_warranty_reg_modal'})
                .then(function (vals) {
                    var $modal = $(vals);
                    $modal.appendTo('#wrap')
                        .modal('show')
                        .on('hidden.bs.modal', function () {
                            $(this).remove();
                        });

                });
        });

        $(document).on('click', '#wrnty_reg_submit', function (event) {
            var warrantyLot = $('#wrnty_lot').val();
            var self = this;
            var orderLine = document.getElementById('ol_id').value
            if (!event.isDefaultPrevented()) {
                if (warrantyLot === "") {
                    $("#error-enter-serial").show();
                    $("#lot-box").addClass("has-error");
                } else {
                    ajax.jsonRpc("/check/serial/", 'call', { 'serial_number': warrantyLot, 'line_id': orderLine })
                        .then(function (vaildSerail) {
                            if (vaildSerail.length > 0) {
                                document.getElementById("validlot_").value = vaildSerail[0];
                                $(self).closest('form').submit();
                            } else {
                                $("#error-invalid-serial").show();
                                $("#lot-box").addClass("has-error");
                            }
                        });
                }
            }
        });


        $('.warranty_reg_more').on('click', function (e) {
            var orderLine = parseInt($(this).find('.ord_line').first().val(), 10);
            ajax.jsonRpc("/warranty/modal/", 'call', { 'ol': orderLine, 'modal': 'wk_warranty_reg_more_modal'})
                .then(function (vals) {
                    var $modal = $(vals);
                    $modal.appendTo('#wrap')
                        .modal('show')
                        .on('hidden.bs.modal', function () {
                            $(this).remove();
                        });

                });
        });

        $(document).on('click', '#wrnty_reg_more_submit', function (event) {
            var warantySerail = document.getElementsByClassName("enter_lot");
            var serialArr = {};
            for (let i = 0; i < warantySerail.length; i++) {
                serialArr[warantySerail[i].name] = warantySerail[i].value;
            }
            var self = this;
            var orderLine = document.getElementById('ol_id').value
            console.log('orderLine', orderLine);
            console.log('serialArr', serialArr);
            if (!event.isDefaultPrevented()) {
                ajax.jsonRpc("/check/serial/more", 'call', { 'serial_number': serialArr, 'line_id': orderLine })
                    .then(function (vaildSerail) {
                        if (Object.keys(vaildSerail).length > 0) {
                            for (var key in vaildSerail) {
                                var inputElem = document.getElementById(key);
                                if (inputElem) {
                                    inputElem.value = vaildSerail[key];
                                }
                            }
                            $(self).closest('form').submit();
                        } else {
                            $("#error-invalid-serial").show();
                        }
                    });
            }
        });

        $(document).on('click', '.wk_remove', function (event) {
            $(this).parent().parent().remove();
        });

        $('.warranty_dwnld1').on('click', function (e) {
            var orderLine = parseInt($(this).find('.ord_line').first().val(), 10);
            ajax.jsonRpc("/warranty/modal/", 'call', { 'ol': orderLine, 'modal': 'wk_warranty_dwnld_modal' })
                .then(function (vals) {
                    var $modal = $(vals);
                    $modal.appendTo('#wrap')
                        .modal('show')
                        .on('hidden.bs.modal', function () {
                            $(this).remove();
                        });

                });
        });


    });
});

