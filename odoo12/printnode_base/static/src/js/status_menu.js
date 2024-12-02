odoo.define('printnode.status_menu', function (require) {
  "use strict";

  var ajax = require('web.ajax');
  var SystrayMenu = require('web.SystrayMenu');
  var Widget = require('web.Widget');

  var ActionMenu = Widget.extend({
    template: 'printnode_status_menu',

    init: function(parent, options) {
      this._super(parent);

      this.limits = [];
      this.releases = [];
      this.newRelease = false;
      this.loaded = false;
    },

    willStart: function() {
      // Rate Us URL
      let odooVersion = odoo.session_info.server_version;
      // This attribute can include some additional symbols we do not need here (like 12.0e+)
      odooVersion = odooVersion.substring(0, 4);
      this.rateUsURL = 'https://apps.odoo.com/apps/modules/' + odooVersion + '/printnode_base/#ratings';

      const limitsPromise = this._rpc({ model: 'printnode.account', method: 'get_limits' });

      // Check if model with releases already exists 
      const releasesPromise = ajax.post("/dpc/release-model-check", {}).then((data) => {
        const status = JSON.parse(data);

        // If model exists load releases
        if (status) {
          return this._rpc({ model: 'printnode.release', method: 'search_read' });
        }
        // If not exist return empty array
        return [];
      });
      
      return Promise.all([limitsPromise, releasesPromise]).then(([limits, releases]) => {
        // Process limits
        this.limits = limits;

        // Process accounts
        this.releases = releases;
        this.newRelease = releases.length > 0;

        // Loading ended
        this.loaded = true;
      });
    }
  });

  SystrayMenu.Items.push(ActionMenu);

  return ActionMenu;
});
