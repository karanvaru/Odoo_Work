odoo.define('asterisk_common.support', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var Support = AbstractAction.extend({
        template: 'asterisk_common.support',

        init: function (parent, action) {
            this._super.apply(this, arguments);
        },

    });

    core.action_registry.add('asterisk_common.support', Support);
});

odoo.define('asterisk_common.addons', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var Addons = AbstractAction.extend({
        template: 'asterisk_common.addons',

        init: function (parent, action) {
            this._super.apply(this, arguments);
        },

    });

    core.action_registry.add('asterisk_common.addons', Addons);
});



