/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
$(document).ready(function () {
	odoo.define('website_estimated_delivery.website_estimated_delivery', function (require) {
    "use strict"
	    var ajax = require('web.ajax');
	   
		$('.oe_website_sale').each(function ()
		{
		    var oe_website_sale = this;
			var message = '';
			var product_template_id = $('#product_details').find($("input[name='product_template_id']")).val();
			ajax.jsonRpc('/website/change/pincode', 'call', {'template_id':product_template_id}).then(function (res)
			{
				if (res != false)
				{	console.log(res);
					$('.pincode_ckeck').val(res.pincode);
					$('.availability_message').show();
					$('.change_pincode').show();
					/* $('.advanced_estimated_delivery').hide(); */
					$('.availability_message').css({"padding": "5px"});

					if (res.status == true)
					{	
						$('.availability_message').text(res.message);
						/* $('.availability_message').css({"background-color": "#B9F6CA",'color':'green'}); */

					}
					else
					{	
						$('.availability_message').text(res.message);
						$('.availability_message').css({"background-color": "#B9F6CA",'color':'red'});
					}
				}

			}).fail(function (err){});

	   		$('.check_availability_button').on('click',function(ev)
	      	{
	        	var pincode = $('.pincode_ckeck').val();
	        	setTimeout(function() {$('.pincode_ckeck').popover('destroy')},3000);
	        	if (pincode.length == 0)
		        	{
		        		
		        		$('.pincode_ckeck').popover({
	              			content:"Please Enter Your Pincode",
	             			placement:"top",
	           		 	});
	          		  $('.pincode_ckeck').popover('show');
	        		}
	        	
	        	else
	        	{
					
					ajax.jsonRpc('/website/check/pincode', 'call', {'pincode':pincode,'template_id':product_template_id}).then(function (res)
					{

						/* $('.advanced_estimated_delivery').hide(); */
						$('.availability_message').css({"padding": "5px"});
						if (res.status == true)
						{
							$('.availability_message').show();
							$('.availability_message').text(res.message);
							/* $('.availability_message').css({"background-color": "#B9F6CA",'color':'green'}); */
							$('.change_pincode').show();
						}
						else
						{
							$('.availability_message').show();
							$('.availability_message').text(res.message);
							$('.availability_message').css({"background-color": "#B9F6CA",'color':'red'});
							$('.change_pincode').show();
						}
					}).fail(function (err){});
		        }
	       	});

			$('.change_pincode').on('click',function(ev)
			{
				$(this).hide();
				$('.advanced_estimated_delivery').show();
				$('.availability_message').hide();
			});


		// ###############  functionality for the cart page input pincode check ##################
			var order_id = $(this).find('.cart_pincode_input').attr('order_id');
			var order_line_ids= $(this).find('.cart_pincode_input').attr('lines');
			if (order_line_ids){
				order_line_ids = JSON.parse(order_line_ids);
			}
			
			ajax.jsonRpc('/website/cart/pincode', 'call', {'order_id':order_id}).then(function (res)
			{
				if (res != false)
				{
					$('.cart_pincode_input').val(res);
					$('.change_pincode_cart').show();
					$('.cart_check_pincode_button').hide();
					$('.cart_pincode_input').hide();
					$('.set_value_outer').show();
					$('.set_value').html(res);
				}
				
			}).fail(function (err){});

			$('.change_pincode_cart').on('click',function(ev)
			{
				$(this).hide();
				$('.cart_check_pincode_button').show();
				$('.cart_pincode_input').show();
				$('.set_value_outer').hide();
			});


			$('.cart_check_pincode_button').on('click',function(ev)
	        {
	        	var input_obj = $(this).parent().parent().find('.cart_pincode_input')
	        	var pincode = input_obj.val();
	        	var order_id = $(this).parent().parent().parent().find('.cart_pincode_input').attr('order_id');
	        	setTimeout(function() {input_obj.popover('destroy')},3000);
	        	if (pincode.length == 0)
	        	{
	        		input_obj.popover({
	          			content:"Please Enter Your Pincode",
	         			placement:"top",
	       		 	});
	      		  input_obj.popover('show');
	    		}
	        	else
		        {
					ajax.jsonRpc('/website/check/pincode/cart', 'call', {'pincode':pincode,'order_id':order_id}).then(function (res)
					{
						if (res != false)
						{
							$('.change_pincode_cart').show();
							$('.cart_check_pincode_button').hide();
							$('.cart_pincode_input').hide();
							$('.set_value_outer').show();
							$('.set_value').text(res);
							
							$.each(order_line_ids, function( i, val ) 
							{
								ajax.jsonRpc('/website/check/pincode/cart/message', 'call', {'pincode':pincode,'order_line_id':val}).then(function (res)
								{

									if (res.status == 'available')
									{
										$('#cart_line-'+val).show();
										$('#cart_line-'+val).html(res.final_message);
										$('#cart_line-'+val).css({'color':'green'});
										$('#cart_line-'+val).addClass('product_available');
										$('#cart_line-'+val).removeClass('product_unavailable');
									}
									else
									{
										$('#cart_line-'+val).show();
										$('#cart_line-'+val).text(res.final_message);
										$('#cart_line-'+val).css({'color':'red'});
										$('#cart_line-'+val).removeClass('product_available');
										$('#cart_line-'+val).addClass('product_unavailable');
										
									}
								
								}).fail(function (err){});
							});
						}
					}).fail(function (err){});
		        }
	       	});

	 	// #########################  Validation for the prodcess checkout ###################################

	 	 	$(oe_website_sale).on('click', '.oe_cart .btn.btn-primary.float-right.d-none.d-xl-inline-block, .card-body .btn.btn-secondary.float-right.d-none.d-xl-inline-block', function (ev)
	        {
				var $self  = $(this)
	    		$.each(order_line_ids, function( i, val ) 
	    		{	
	    			if ($('#cart_line-'+val).hasClass('product_unavailable'))
	    			{
	    				ev.preventDefault();
		                $self.popover({
		                  content:"Sorry!!!, some of the products in the cart are not available to your location.",
		                  title:"WARNING!!",
		                  placement:"top",
		                  trigger:'focus',
		                });
		                $self.popover('show');
		            }
		            setTimeout(function() {$self.popover('hide')},3000);
	    		});
	      	});
		});
	});
});
