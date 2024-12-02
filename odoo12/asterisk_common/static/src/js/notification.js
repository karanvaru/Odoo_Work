odoo.define("remote_agent.notification", function (require) {
    "use strict";
  
    var WebClient = require('web.WebClient');
    var ajax = require('web.ajax');
    var utils = require('mail.utils');
    var session = require('web.session');    
    var channel = 'remote_agent_notification_' + session.uid;

    WebClient.include({
        start: function() {
            this._super()
            var self = this
            ajax.rpc('/web/dataset/call_kw/res.users', {
                    "model": "res.users",
                    "method": "has_group",
                    "args": ['asterisk_common.group_asterisk_user'],
                    "kwargs": {},            
            }).then(function (res) {
              if (res == true) {
                self.call('bus_service', 'addChannel', channel);
                self.call('bus_service', 'onNotification', self,
                          self.remote_agent_on_notification)
                // console.log('Listening on', channel)
              }
            })
        },

        remote_agent_on_notification: function (notification) {
          for (var i = 0; i < notification.length; i++) {
             var ch = notification[i][0]
             var msg = notification[i][1]
             if (ch == channel) {
                 try {
                  this.remote_agent_handle_message(msg)
                }
                catch(err) {console.log(err)}
             }
           }
        },

        remote_agent_handle_message: function(msg) {
          if (typeof msg == 'string')
            var message = JSON.parse(msg)
          else
            var message = msg
          // Check if this is a reload message.
          if (message.reload) {
            return this.remote_agent_handle_reload_message(message)
          }
          // Check if this is a notification message
          if (message.message) {
            return this.remote_agent_handle_notification_message(message) 
          }
        },

        remote_agent_handle_reload_message: function(message) {
          var action = this.action_manager && this.action_manager.getCurrentAction()
          if (!action) {
              // console.log('Action not loaded')
              return
          }
          var controller = this.action_manager.getCurrentController()
          if (!controller) {
              // console.log('Controller not loaded')
              return
          }
          if (controller.widget.modelName != message.model) {
              // console.log('Not message model view')
              return
          }
          // console.log('Reload')
          controller.widget.reload()
        },

        remote_agent_handle_notification_message: function(message) {
          // console.log(msg)
          if (message.warning == true)
            this.do_warn(message.title, message.message, message.sticky)
          else
            this.do_notify(message.title, message.message, message.sticky)
      },


    })
})
