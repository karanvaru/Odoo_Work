odoo.define('activities_todo.todo_readonly_formcontroller', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var FormController = require('web.FormController');

    var ToDoReadonlyFormController = FormController.extend({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.activeActions = false;
        },
    });
    return  ToDoReadonlyFormController;

});