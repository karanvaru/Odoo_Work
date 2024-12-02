odoo.define('ki_crm_portal.mark_lost', function (require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');

    $(document).ready(function() {

        $(".crm_portal_assigned_bid .js_assigned_bid_lost").on("change", function(ev){
            var $parent = $(ev.target).closest('.crm_portal_assigned_bid');
            var show_mark_lost_button = false;
            var mark_checked = $parent.find('.js_assigned_bid_lost:checked');
            if (mark_checked.length > 0) {
                show_mark_lost_button = true;
            }
            if (show_mark_lost_button) {
                $parent.find('.js_update_bd_lost').removeClass('d-none');
            }
            else {
                $parent.find('.js_update_bd_lost').addClass('d-none');
            }
        });

        $(".crm_portal_assigned_bid #js_button_mark_lost").on("click", function(ev) {
            var $parent = $(ev.target).closest('.crm_portal_assigned_bid');
            var values = []
            _.each($parent.find('.js_assigned_bid_lost:checked'), function (el) {
                var id = el.getAttribute("data-value_id");
                if (id) {
                    values.push(id)
                }
            })
            $parent.find('input[name="lost_bid_ids"]').val(values);
            $('.crm_portal_assigned_bid #bid_lost_all').modal('show');
        });

        $('.crm_portal_assigned_bid #bid_lost_all').on('hidden.bs.modal', function (event) {
            var modal = $(this)
            modal.find('.modal-body input[name="lost_bid_ids"]').val('')
        })

        $(".crm_portal_assigned_bid #js_select_all_bid").on("click", function(ev) {
            var $parent = $(ev.target).closest('.crm_portal_assigned_bid');
            var mark_checked = $parent.find('.js_assigned_bid_lost');
            var self = this;
            _.each(mark_checked, function (el) {
                el.checked = self.checked;
            });
            if (this.checked) {
                $parent.find('.js_update_bd_lost').removeClass('d-none');
            }
            else {
                $parent.find('.js_update_bd_lost').addClass('d-none');
            }
        });
    });
})