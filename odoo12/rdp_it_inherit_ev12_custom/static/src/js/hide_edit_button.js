odoo.define('rdp_it_inherit_ev12_custom.hide_buttons', function (require) {
    'use strict';

    var FormController = require('web.FormController');
    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    function hideButtons(controller, buttonClass, models) {
        if (models.includes(controller.modelName)) {
            rpc.query({
                model: 'res.users',
                method: 'has_group',
                args: ['base.group_system'],
            }).then(function (has_group) {
                if (!has_group) {
                    controller.$buttons.find(buttonClass).hide();
                }
            });
        }
    }

    FormController.include({
        renderButtons: function ($node) {
            this._super($node);
            if (this.$buttons) {
                hideButtons(this, '.o_form_button_edit', ['product.product', 'product.template']);
                hideButtons(this, '.o_form_button_create', ['product.product', 'product.template']);
            }
        },
    });

    ListController.include({
        renderButtons: function ($node) {
            this._super($node);
            if (this.$buttons) {
                hideButtons(this, '.o_list_button_add', ['product.product', 'product.template']);
            }
        },
    });

    KanbanController.include({
        renderButtons: function ($node) {
            this._super($node);
            if (this.$buttons) {
                hideButtons(this, '.o-kanban-button-new', ['product.product', 'product.template']);
            }
        },
    });

});
