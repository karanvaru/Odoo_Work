odoo.define('ki_crm_bid.bid_picker', function (require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var time = require('web.time');

    $(document).ready(function() {
        var datepickersOptions = {
            icons : {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                next: 'fa fa-chevron-right',
                previous: 'fa fa-chevron-left',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down',
            },
            widgetPositioning : {
                horizontal: 'auto',
                vertical: 'top',
            },
            locale : moment.locale(),
            format : 'DD/MM/YYYY HH:mm:ss',
        };
        $('#datetime_bid_container').datetimepicker(datepickersOptions);
        $('#published_bid_container').datetimepicker(datepickersOptions);
        $('#priority_1').change(function(ev){
            var checked = ev.currentTarget.checked
            if (!checked) {
                $('#priority_2')[0].checked = false
                $('#priority_3')[0].checked = false
            }
        })
        $('#priority_2').change(function(ev){
            var checked = ev.currentTarget.checked
            if (checked) {
                $('#priority_1')[0].checked = true
            }
            else {
                $('#priority_3')[0].checked = false
            }
        })
        $('#priority_3').change(function(ev){
            var checked = ev.currentTarget.checked
            if (checked) {
                $('#priority_1')[0].checked = true
                $('#priority_2')[0].checked = true
            }
        })
    });
})