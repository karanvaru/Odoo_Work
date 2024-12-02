odoo.define('ki_helpdesk_extend.helpdesk', function (require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');
    console.log("AAAAAAAAAAAAAAAAAAAAA",ajax);
    console.log("this____________",this);
    $(document).ready(function() {

        $("#email_input_search_1").on("change", function(ev){
            var email = $(ev.target).val();
            $("#email_input_search_2").val(email)
        });
      $(".stage_wise_records").on("click", function(ev){
                  var state_count = $(ev.target);
                  var count = $('#stage_count');
//                  ajax.jsonRpc("/my/tickets", 'call', {})
                  console.log('ev______________________',count.innerText);
                  console.log('Button______________________',state_count.context.innerText);
                  var s
       });

        $("#helpdesk_team_select_id").on("change", function(ev) {
            var team_id = $(ev.target).val();
            if (team_id) {
                ajax.jsonRpc('/ticket/helpdesk_team/validate', 'call', {'team_id': team_id})
                .then(function (result) {
                    $("#helpdesk_team_user_id").empty();
                    for (var i = 0; i < result.length; i++) {
                        $("#helpdesk_team_user_id")[0].appendChild(new Option(result[i]['name'], result[i]['id']));
                    }
                })
                .fail(function () {
                    $("#helpdesk_team_user_id").empty();
                });
            }
            else {
                $("#helpdesk_team_user_id").empty();
            }
        });

        $("#helpdesk_team_select_id").trigger('change');
    });
})