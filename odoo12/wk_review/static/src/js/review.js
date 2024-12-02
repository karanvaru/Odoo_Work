/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

$(document).ready(function() {

  var form_being_submitted = false
  if(location.href.indexOf('auto_publish')!=-1){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    location=location.href.substring(0, location.href.indexOf('message')-1);
    if (hashes[1] == "auto_publish=False")
    {
      var msg = decodeURIComponent((hashes[0] + '').replace(/\+/g, '%20'));
      msg = msg.replace('message=','');
    }
    else
      var msg = "Congratulation!!! your review has been submitted successfully.";
    $('#submit-msg').after('<div id="msg" class="alert alert-success">\
                            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\
                            <strong></strong>'+msg+'</div>');
  }
  odoo.define('wk_review.wk_review', function (require)
  {
    "use strict";
    var ajax = require('web.ajax');

    $("#valstar").rating({
    starCaptions: {1: "Poor", 2: "Ok", 3: "Good", 4: "Very Good", 5: "Excellent"},
    starCaptionClasses: {1: "badge badge-danger", 2: "badge badge-warning", 3: "badge badge-info", 4: "badge badge-primary", 5: "badge badge-success"},
    });

    $('#btnsave').on('click',function (e){
      if(form_being_submitted){
        alert("form is being submitted please wait");
        $(this).disabled = true;
        e.preventDefault();
      }
      var rate = $("#valstar").val();
      if (rate<=0){
        $("#errordiv").html("Please add your rating !!!");
        e.preventDefault();
        form_being_submitted = false;
        return false
      }
      form_being_submitted = true
      return ;
    });


    // New Code
        var offset = 0;
        $('#morebtn').on('click',function (e)
        {
            var total_product_reviews = $('#total_product_reviews').html();
            var product_id =  parseInt($('.box-review').find('input[type="hidden"][name="product_id"]').first().val(),10);
            var limit =  parseInt($('.box-review').find('input[type="hidden"][name="limit"]').first().val(),10);
            offset=offset+limit ;
            ajax.jsonRpc("/shop/product/load/review", 'call',
            {
                'product_id':product_id,
                'offset': offset,
                'limit': limit
            })
            .then(function (result)
            {
                var $review =$(result);
                var what = $(result).appendTo('#all-review');
                var $input = $(what).find('input.rating'), count = Object.keys($input).length;
                if (count > 0) {
                  $input.rating();
                }
            });

      ajax.jsonRpc("/shop/product/load/review/count", 'call',
      {
        'product_id':product_id,
        'offset': offset,
        'limit': limit
      })
      .then(function (result)
      {
        if (result > 0)
          $('#viewed').text(offset+result);
        if (total_product_reviews == offset+result)
          $('#morebtn').hide();
      });
    });


    $('.tot-rating').on('mouseenter', function()
    {
      var $form = $(this).closest('form');
      var avg_review =  parseFloat($form.find('input[type="hidden"][name="review_id"]').first().val(),10);
      var user_reviews = $form.find('input[type="hidden"][name="user_reviews"]').first().val();
      if (avg_review)
      {
        var avg_review = avg_review.toFixed(1);
        var avg_review_per = avg_review*20;
        avg_review_per = avg_review_per.toString();

        var placement="top";
        if ($(this).closest('.oe_list').index()==0){
          placement='right';
        }
        $(this).popover({
        placement :placement,
        title:"<center>Average Rating</center>",
        trigger : 'focus',
        html : true,
        content :  '<div class="review-popover" style="color: orange;">\
                        <div class="fa-stack fa-2x">\
                            <i class="fa fa-star fa-stack-2x"></i>\
                            <p style="font-size:15px;" class="fa-stack-1x fa-stack-text fa-inverse">'+avg_review+'</p>\
                        </div>\
                        <div>Out Of 5</div>\
                        <div class="progress" style="height:15px; margin-top:1px;  margin-bottom: 1px;">\
                            <div class="progress-bar bg-warning" role="progressbar" aria-valuenow="70" aria-valuemin="0" aria-valuemax="100" style="width:'+avg_review_per+'%">\
                            </div>\
                        </div>\
                        <span style="color:#555555;font-size:12px"><u><b>'+user_reviews+'</b>&nbspReviews</u></span>\
                    </div>'
        });
        $(this).popover('show');
        $(this).on('mouseenter', function()
        {
          $(this).popover('show');
        });
        $(this).on('mouseleave', function()
        {
         $(this).popover('hide');
        });
      }
    });

    $("body").on('click', ".sprite", function(e){
      var dislike = 100;
      if ($(this).hasClass('TopLeft')) {
        var self = this


        var $form = $(this).closest('.review_div');
        var review_id =  parseInt($form.find('input[type="hidden"][name="review_id"]').first().val(),10);
        var vote = 1;
        ajax.jsonRpc("/shop/review/vote", 'call',
        {
          'review_id': review_id,
          'vote': vote
        })

        .then(function (result)
        {
          if (result)
          {
            $form.find('#review_likes').text(result[0]);
            $form.find('#review_dislikes').text(result[1]);
            $(self).removeClass('TopLeft');
            $(self).addClass('BottomLeft');
          }
          else{
            $('#login-modal').modal('show');
          }
        });
        $form.find('.BottomRight').addClass('TopRight').removeClass('BottomRight');
        return;
      }

      if ($(this).hasClass('TopRight')) {
        var self = this
        
        var $form = $(this).closest('.review_div');
        var review_id =  parseInt($form.find('input[type="hidden"][name="review_id"]').first().val(),10);
        var vote = -1;
        ajax.jsonRpc("/shop/review/vote", 'call',
        {
          'review_id': review_id,
          'vote': vote
        })
        .then(function (result)
        {
          if (result)
          {
            $(self).removeClass('TopRight');
            $(self).addClass('BottomRight');
            $form.find('#review_dislikes').text(result[1]);
            $form.find('#review_likes').text(result[0]);
          }

          else{
            $('#login-modal').modal('show');
          }
        });
        $form.find('.BottomLeft').addClass('TopLeft').removeClass('BottomLeft');
        return;

      }
      if ($(this).hasClass('BottomLeft')) {
        $(this).removeClass('BottomLeft');
        $(this).addClass('TopLeft');
        var $form = $(this).closest('.review_div');
        var review_id =  parseInt($form.find('input[type="hidden"][name="review_id"]').first().val(),10);
        var vote = 2;
        ajax.jsonRpc("/shop/review/vote", 'call',
        {
          'review_id': review_id,
          'vote': vote
        })

        .then(function (result)
        {
          if (result)
          {
            $form.find('#review_likes').text(result[0]);
            $form.find('#review_dislikes').text(result[1]);
          }
        });
        return;
      }
      if ($(this).hasClass('BottomRight')) {
        $(this).removeClass('BottomRight');
        $(this).addClass('TopRight');
        var $form = $(this).closest('.review_div');
        var review_id =  parseInt($form.find('input[type="hidden"][name="review_id"]').first().val(),10);
        var vote = -2;
        ajax.jsonRpc("/shop/review/vote", 'call',
        {
          'review_id': review_id,
          'vote': vote
        })

        .then(function (result)
        {
          if (result)
          {
            $form.find('#review_dislikes').text(result[1]);
            $form.find('#review_likes').text(result[0]);
          }
        });
        return;
      }
    });
    $(document).ready(function() {
      $("abbr.timeago").timeago();
    });
  });
});
