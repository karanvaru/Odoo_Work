odoo.define("sh_auto_part_vehicle.snippets", function (require) {
    "use strict";

    require("web.dom_ready");
    var ajax = require("web.ajax");
    var core = require("web.core");
    var publicWidget = require("web.public.widget");

    var _t = core._t;

    publicWidget.registry.sh_motorcycle_snippet_tmpl_1 = publicWidget.Widget.extend({
        selector: "#sh_motorcycle_snippet_section_1",
        start: function () {
            this._super.apply(this, arguments);
            var self = this;

            ajax.jsonRpc("/sh_motorcycle/is_user_logined_in", "call", {}).then(function (rec) {
                if (rec.is_user_logined_in){
                    $(".id_sh_motorcycle_snippet_login_to_acc_garage_link").hide();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").show();
                } else {
                    $(".id_sh_motorcycle_snippet_login_to_acc_garage_link").show();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").hide();
                }

				if (!rec.sh_is_show_garage){
					$(".id_sh_motorcycle_snippet_login_to_acc_garage_link").hide();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").hide();
				}
            });

            /* add category to select saved bike button. */

            $(".id_sh_motorcycle_snippet_select_saved_bike_div > a").remove();
            ajax.jsonRpc("/sh_motorcycle/get_saved_bike", "call", {}).then(function (data) {
                _.each(data, function (moto) {
                    self.$el.find(".id_sh_motorcycle_snippet_select_saved_bike_div").append('<a class="dropdown-item" href="' + moto.moto_url + '">' + moto.name + "</a>");
                });

                //category selected in snippet options.
                var categ_id = $('input[class="id_input_sh_moto_categ_id"]').val();
                if (categ_id && categ_id.length) {
                    var alinks = $(".id_sh_motorcycle_snippet_select_saved_bike_div").children("a");
                    if (alinks) {
                        alinks.each(function (index) {
                            var href = $(this).attr("href");
                            href = href + "&category=" + categ_id;
                            $(this).attr("href", href);
                        });
                    }
                }
            });
        },
    });



	publicWidget.registry.sh_motorcycle_snippet_tmpl_2 = publicWidget.Widget.extend({
        selector: "#sh_motorcycle_snippet_section_4",
        start: function () {
            this._super.apply(this, arguments);
            var self = this;

            ajax.jsonRpc("/sh_motorcycle/is_user_logined_in", "call", {}).then(function (rec) {
                if (rec.is_user_logined_in){
                    $(".id_sh_motorcycle_snippet_login_to_acc_garage_link").hide();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").show();
                } else {
                    $(".id_sh_motorcycle_snippet_login_to_acc_garage_link").show();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").hide();
                }

				if (!rec.sh_is_show_garage){
					$(".id_sh_motorcycle_snippet_login_to_acc_garage_link").hide();
                    $(".id_sh_motorcycle_snippet_select_saved_bike_dropdown").hide();
				}
            });

            /* add category to select saved bike button. */

            $(".id_sh_motorcycle_snippet_select_saved_bike_div > a").remove();
            ajax.jsonRpc("/sh_motorcycle/get_saved_bike", "call", {}).then(function (data) {
                _.each(data, function (moto) {
                    self.$el.find(".id_sh_motorcycle_snippet_select_saved_bike_div").append('<a class="dropdown-item" href="' + moto.moto_url + '">' + moto.name + "</a>");
                });

                //category selected in snippet options.
                var categ_id = $('input[class="id_input_sh_moto_categ_id"]').val();
                if (categ_id && categ_id.length) {
                    var alinks = $(".id_sh_motorcycle_snippet_select_saved_bike_div").children("a");
                    if (alinks) {
                        alinks.each(function (index) {
                            var href = $(this).attr("href");
                            href = href + "&category=" + categ_id;
                            $(this).attr("href", href);
                        });
                    }
                }
            });
        },
    });


});
