odoo.define('ks_odoo12_sticky_pivot.stick_header', function (require) {
'use strict';
    var ks_ListView = require('web.PivotRenderer');
    var ks_PivotController = require('web.PivotController');
    var ks_Session = require('web.session');
    var ks_old_render = ks_ListView.prototype._render;
    ks_ListView.prototype._render = function(){
        var ks_self=this;
        var ks_res = ks_old_render.call(this);
        var ks_o_content_area = $(".o_pivot")[0];
        var ks_el = ks_self.$el;

        //Sticking the header of the table pivot table
        function ks_sticky(){
           if(ks_Session.ks_pivot_status_header){
                if(ks_el.parents(".o_dashboard").length===0){
                   ks_el.each(function () {
                           $(this).stickyTableHeadersPivot({scrollableArea: ks_o_content_area, fixedOffset: 0.1,stickStatus: ks_Session.ks_pivot_status_header});
                    });
                }
           }
        }
			
        if(this.$el.parents('.o_field_one2many').length===0){
          if(typeof(ks_o_content_area)==="undefined")
             {
                _.delay(function () {
                    ks_o_content_area = $(".o_pivot")[0];
                    ks_sticky();
              }, 200);
             }
             else{
                 ks_sticky();
             }
            ks_stick_frist_Column();
            this.$el.css("overflow-x","visible");
            $(window).unbind('scroll',ks_sticky).bind('scroll', ks_sticky);

        }
        $("div[class='o_sub_menu']").css("z-index",4);

        return ks_res;
    }
     //Sticking the first column of the pivot table if the status is checked in the res.config
    function ks_stick_frist_Column(){
         if(ks_Session.ks_pivot_status_header){
             _.each($(".o_pivot table tbody .o_pivot_header_cell_opened"), function(ks_pivot_cell) {
                    $(ks_pivot_cell).css({
                       'left' : '0',
                       'position' : 'sticky'
                    });
                      $(ks_pivot_cell).css({
                       'position' : ' -webkit-sticky;'
                    });
               });
                _.each($(".o_pivot table tbody .o_pivot_header_cell_closed"), function(ks_pivot_cell) {
                    $(ks_pivot_cell).css({
                       'left' : '0',
                       'position' : 'sticky'
                    });
                     $(ks_pivot_cell).css({
                       'position' : ' -webkit-sticky'
                    });
               });
         }
         else{
            $(".ks_header_cell_cover").css({
                "display":"none",
            })
         }
    }


});
