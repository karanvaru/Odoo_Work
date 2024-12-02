odoo.define('activities_todo.knowsystem_readonly_formview', function (require) {
"use strict";

    var ToDoReadonlyFormController = require('activities_todo.todo_readonly_formcontroller');
    var config = require('web.config');
    var FormView = require('web.FormView');
    var view_registry = require('web.view_registry');


    var ToDoReadonlyFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: ToDoReadonlyFormController,
        }),
    });

    view_registry.add('todo_readonly_form', ToDoReadonlyFormView);

    return ToDoReadonlyFormView;

});