$(document).ready(function () {

if ($('.gem-form-part').length) {
        var state_options = $("select[name='state']:enabled option:not(:first)");
        $('.gem-form-part').on('change', "select[name='country']", function () {
            var select = $("select[name='state']");
            state_options.detach();
            var displayed_state = state_options.filter("[data-country_id="+($(this).val() || 0)+"]");
            var nb = displayed_state.appendTo(select).show().size();
            select.parent().toggle(nb>=1);
        });
        $('.gem-form-part').find("select[name='country']").change();
    }
    $(".o_service_categories").select2(); //multi_selection
    $(".o_service_product_cat").select2();
    $(".o_service_states").select2();
    $(".o_service_dist").select2();
    $(".o_service_type").select2();
    $(".o_service_delivery").select2();
    $(".o_other_brand").select2();
});
