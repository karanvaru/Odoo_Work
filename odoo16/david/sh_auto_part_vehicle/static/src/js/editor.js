odoo.define("sh_auto_part_vehicle.editor", function (require) {
    "use strict";

    require("web.dom_ready");
    var ajax = require("web.ajax");
    var core = require("web.core");
    var options = require("web_editor.snippets.options");
    var Animation = require("website.content.snippets.animation");
    var weContext = require("web_editor.context");
    var _t = core._t;

    options.registry.js_editor_sh_motorcycle_snippet_tmpl_1 = options.Class.extend({
        //for select category
        selectClass: function (previewMode, value, $li) {
            this._super.apply(this, arguments);

            if (value && value.length && value != "") {
                var val_2 = value;
                var category_id = 0;
                category_id = val_2.replace("sh_moto_categ_", "");
                category_id = parseInt(category_id);
                this.$target.find('input[name="category"]').val(category_id);
            } else if (value && value.length && value == "") {
                this.$target.find('input[name="category"]').val("");
            }
        },
    });
});
