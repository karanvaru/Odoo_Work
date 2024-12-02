/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

$(document).ready(function() {

	if(location.href.indexOf('attachment_id')!=-1){
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        location=location.href.substring(0, location.href.indexOf('attachment_id')-1);
        if (hashes == "attachment_id=True")
        {
            msg = "Images has been uploaded Successfully."
            $('#msg-box').append('<div id="msg" style="margin-top:5px;margin-bottom:5px;" class="alert alert-success">\
                                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\
                                <strong></strong>'+msg+'</div>');
        }
        else
        {
        	msg = " Error in image uplaoding. "
        	$('#msg-box').append('<div id="msg" style="margin-top:5px;margin-bottom:5px;" class="alert alert-success">\
                                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\
                                <strong></strong>'+msg+'</div>');
        }

        setTimeout(function() {$('#msg').fadeOut(4000)},4000);
    }


	odoo.define('rma.website_rma', function (require)
    {
        "use strict";
        var ajax = require('web.ajax');
	    var return_qty;

		$('.rma-return').on('click',function(e)
		{
			var order_line = parseInt($(this).find('.order_line').first().val(),10);
			ajax.jsonRpc("/return/rma/", 'call', {'order_line': order_line})
			.then(function (vals)
			{
	            var $modal = $(vals);
	            $modal.appendTo('#wrap')
	                .modal('show')
	                .on('hidden.bs.modal', function () {
	                    $(this).remove();
	                });
	            var return_qty = parseFloat($('#rma_product_qty').val());
				var unit_price = parseFloat($('#rma_product_unit_price').val());
				$('#refund_amount_span .oe_currency_value').text((return_qty * unit_price).toString());
				var return_type  = $('#rma_return_type').val();
				if (return_type === "refund")
					$("#refund-amount-box").show();
				else
					$("#refund-amount-box").hide();
				var term_condition = $('#rma_term_condition').val();
				$('.wk_content').html(term_condition);
	        });
		});

		$(document).on('click','#return_submit', function (event)
		{
			$('.rma_error').hide();//Reset All error messages

			return_qty = parseFloat($('#rma_product_qty').val());
			var i_agree = $('#i-agree-value:checked').val();
			var return_type = $('#rma_return_type').val();
			var reason_type = $('#rma_reason').val();
			var max_return_qty = parseFloat($('#max_return_qty').val());
			if (!event.isDefaultPrevented()) {

				if (return_type === "Select Request Type")
				{
					$("#error-resolution-type").show();
					$("#resolution-div").addClass("has-error");
				}
				else if (reason_type === "Select Reason")
				{
					$("#error-reason-type").show();
					$("#reason-div").addClass("has-error");
				}
				else if ($("#rma_refund_problem").val() === "")
				{
					$("#problem-box").addClass("has-error");
					$("#error-msg-problem").show();
				}
				else if (return_qty === 0.0 || return_qty < 0.0 || !return_qty)
				{
					$("#error-msg-qty").show();
				}
				else if (i_agree != "on")
				{
					$("#t-c").show();
					$("#i-agree").addClass("has-error");
				}
				else
				{
					$(this).closest('form').submit();
				}
			}
		});

		$('.rma_view').on('click',function(e)
		{
			var order_line = parseInt($(this).find('.order_line').first().val(),10);
			ajax.jsonRpc("/rma/view/", 'call', {'order_line': order_line})
			.then(function (vals)
			{
	            var $modal = $(vals);
	            $modal.appendTo('#wrap')
	                .modal('show')
	                .on('hidden.bs.modal', function () {
	                    $(this).remove();
	                });
	        });
		});
		$(document).on('change', "input#rma_product_qty", function()
		{
			return_qty = parseFloat($('#rma_product_qty').val());
			var unit_price = parseFloat($('#rma_product_unit_price').val());
			var max_return_qty = parseFloat($('#max_return_qty').val());
			$("#qty-box").removeClass("has-error");
			$("#error-msg-qty").hide();
			if (!$.isNumeric(return_qty))
			{
				alert("Please enter integer value only.");
				$('#rma_product_qty').val(max_return_qty);
				$('#refund_amount_span .oe_currency_value').text((parseFloat($('#rma_product_qty').val()) * unit_price).toString());
				$('#rma_refund_amount').val((parseFloat($('#rma_product_qty').val()) * unit_price).toString());
			}

			if (return_qty === 0.0 || return_qty < 0.0 || !return_qty)
			{
				$("#qty-box").addClass("has-error");
				$("#error-msg-qty").show();
			}
			if (return_qty > max_return_qty)
			{
				alert("You can return only " +max_return_qty + " quantity.");
				$('#rma_product_qty').val(max_return_qty);
				$('#refund_amount_span .oe_currency_value').text((parseFloat($('#rma_product_qty').val()) * unit_price).toString());
				$('#rma_refund_amount').val((parseFloat($('#rma_product_qty').val()) * unit_price).toString());
			}
			if (return_qty <= max_return_qty)
			{
				$('#refund_amount_span .oe_currency_value').text((parseFloat($('#rma_product_qty').val()) * unit_price).toString());
				var x = $("#refund_amount_span .oe_currency_value").text();
				$('#rma_refund_amount').val((return_qty * unit_price).toString());
				$('#refund_amount_span').text(parseFloat(return_qty * unit_price).toFixed(2).toString());
			}
		});
		$(document).on('keyup', '#rma_refund_problem',function()
		{
			$('.rma_error').hide();//Reset All error messages

			$("#problem-box").removeClass("has-error");
			$("#error-msg-problem").hide();
			if ($("#rma_refund_problem").val() === "")
			{
				$("#problem-box").addClass("has-error");
				$("#error-msg-problem").show();
			}
		});

        $(document).on("change","#rma_return_type", function()
		{
			$('.rma_error').hide();//Reset All error messages

			var return_type  = $(this).val();
			if (return_type === "Select Resolution Type")
			{
				$(document).find("#resolution-div").addClass("has-error");
				$(document).find("#refund-amount-box").hide();
				$(document).find("#error-resolution-type").show();
			}
			else if (return_type === "refund")
			{
				$(document).find("#resolution-div").removeClass("has-error");
				$(document).find("#refund-amount-box").show();
				$(document).find("#error-resolution-type").hide();
			}
			else
			{
				$(document).find("#resolution-div").removeClass("has-error");
				$(document).find("#refund-amount-box").hide();
				$(document).find("#error-resolution-type").hide();
			}
		});

		$(document).on("change","#rma_reason", function()
		{
			$('.rma_error').hide();//Reset All error messages

			var return_type  = $(this).val();
			if (return_type === "Select Reason")
			{
				$(document).find("#reason-div").addClass("has-error");
				$(document).find("#error-reason-type").show();
			}
			else
			{
				$(document).find("#resolution-div").removeClass("has-error");
				$(document).find("#error-reason-type").hide();
			}
		});

		$(document).on("change","#i-agree-value", function()
		{
			$('.rma_error').hide();//Reset All error messages
			var i_agree = $(this).val();
			if ($(this).prop('checked') != true)
			{
				$(document).find("#t-c").show();
				$(document).find("#i-agree").addClass("has-error");
			}
			else
			{
				$(document).find("#t-c").hide();
				$(document).find("#i-agree").removeClass("has-error");
			}
		});
	var temp = 0;
    var currentUrl = location.href;
    var title = $(document).find("title").text();
    $(document).ready(function() {
    	$(".attachment-delete").click(function( event ) {
    		var $tbody = $(this);
    		var attachment_id = parseInt($tbody.find('input[name="attachment_id"]').first().val(),10);
    		var rma_id = parseInt($(document).find('input[name="rma_id"]').first().val(),10);
    		var x = $('#deleted-msg');
    		var y;
    		ajax.jsonRpc("/rma/remove_upload", 'call',
            {
                'attachment_id': attachment_id,
                "rma_id" : rma_id
            })
            .then(function (msg)
            {
            	location.reload();
            });
		});
	    $('.wk_website_rma').each(function(ev){
	    	var wk_website_rma  = this;
	    	$(wk_website_rma).on('click', 'a.file_browse_btn', function(){
	    		var data = $('input.file_browse').val();
	    		var $form = $(this).closest('form');
	    		$form.find('input[type="file"]').click();
	    	});

	    	$(wk_website_rma).find('input[type="file"]').on('change', function(){
		    	var $form = $(this).closest('form');
		    	var name = $(this)[0].files[0].name;
			var file_extenison = name.slice((name.lastIndexOf(".") - 1 >>> 0) + 2);
			var ext = name.split('.').pop().toLowerCase();
			var arr = ["jpeg", "png", "bmp", "gif", "tiff", "jpg"]
		    	if ((!name) || name === '' || !(jQuery.inArray(name.split('.').pop().toLowerCase(), arr) != -1))
		    	{
				$(document).find('#file-upload-error-msg').show();
		    	}
		    	else
		    	{
				$(document).find('#file-upload-error-msg').hide();
		    		if (temp == 0)
		    		{
		    			$('span.input-group-btn a').after('<button type="submit" class="btn btn-danger file_upload_btn fa fa-upload">&#032;Upload File</button>');
		    			temp = 1;
		    		}
		    		$('button.file_upload_btn').show();
		    		$('div#file-upload-name').html('<span class="fa fa-file-o"></span>&#032;'+name);
		    	}
		    });
	    });
	});
	});
});
