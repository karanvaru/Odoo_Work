odoo.define("asterisk_calls.channel", function (require) {
    "use strict";
  
    var WebClient = require('web.WebClient');
    var ajax = require('web.ajax');
    var utils = require('mail.utils');
    var session = require('web.session');    
    var channel = 'asterisk_calls_channels';

    WebClient.include({
        start: function(){
            this._super()
            self = this
            // Get open partner for setting
            ajax.rpc('/web/dataset/call_kw/res.users', {
                    "model": "res.users",
                    "method": "has_group",
                    "args": ['asterisk_common.group_asterisk_user'],
                    "kwargs": {},
            }).then(function (res) {
              if (res != true) { return }
              ajax.rpc('/web/dataset/call_kw/res.users', {
                      "model": "res.users",
                      "method": "read",
                      "args": [session.uid],
                      "kwargs": {'fields': ['name', 'calls_open_partner_form']},
              }).then(function (user) {
                self.open_partner_form = user[0].calls_open_partner_form
                //console.log('Open partner form: ', self.open_partner_form)
              })
              // Get channels
              ajax.rpc('/web/dataset/call_kw/res_users', {
                      "model": "res.users",
                      "method": "get_asterisk_channels",
                      "args": [session.uid],
                      "kwargs": {}
              }).then(function (channels) {
                self.asterisk_channels = channels
                // console.log(self.asterisk_channels)
              })
              // Start polling
              self.call('bus_service', 'addChannel', channel);
              self.call('bus_service', 'onNotification', self, self.asterisk_calls_on_notification)
              //console.log('Listening on asterisk_calls_channels.')
            })
        },

        asterisk_calls_on_notification: function (notification) {
          for (var i = 0; i < notification.length; i++) {
             var ch = notification[i][0]
             var msg = notification[i][1]
             if (ch == channel) {
                 try {
                  this.asterisk_calls_handle_message(msg)
                }
                catch(err) {console.log(err)}
             }
           }
        },

        asterisk_calls_handle_message: function(msg) {
          if (typeof msg == 'string')
            var message = JSON.parse(msg)
          else
            var message = msg
          var action = this.action_manager && this.action_manager.getCurrentAction()
          if (!action) {
              //console.log('Action not loaded')
              return
          }
          var controller = this.action_manager.getCurrentController()
          if (!controller) {
              //console.log('Controller not loaded')
              return
          }          
          if (controller.widget.modelName != "asterisk_calls.channel") {
            //console.log('Not Active Calls view')
            return
          }
          // Check if it's a call from partner to "me".
          //console.log(message)
          if ((this.asterisk_channels[message.system_name].includes(message.channel)) &&
                this.open_partner_form && 
                message.event != "hangup_channel") {
            //console.log('Opening partner form')
            // First check if we have open lead
            // console.log(message)
            if (message.lead_id) {
              this.do_action({
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'target': 'current',
                'res_id': message.lead_id,
                'views': [[message.view_id, 'form']],
                'view_mode': 'tree,form',
                
                })
              return
            } 
            // Now check if we have partner         
            else if (!message.lead_id && message.partner_id) {
              this.do_action({
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'target': 'current',
                'res_id': message.partner_id,
                'views': [[false, 'form']],
                'view_mode': 'tree,form',
                
                })
              return
            }          
          }
          // Just reload channels list
          if (message['auto_reload'] == true) {
            //console.log('Reload')
            controller.widget.reload()
          }
        },
    })
})
