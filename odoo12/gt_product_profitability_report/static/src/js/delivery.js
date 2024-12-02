odoo.define('delivery_date.delivery', function(require) {
	"use strict";
	var base = require('web_editor.base');
	var core = require('web.core');
	var sale = require('website_sale.cart');
	var ajax = require('web.ajax');
	var payment = require('website_sale.cart')
	var _t = core._t;
	
	$(document).ready(function() {
	    $('#datePicker')
	        .datepicker({
	            autoclose: true,
	            format: 'yyyy-mm-dd'
	        });
//	$(function () {
//		  $("#datepicker").datepicker({ 
//		  });;
//		});
	
	
		
	$('#b_date').change(function(){
		
		var date = $('#b_date').val();
	    var today = new Date();
	    today = moment(today).format("YYYY-MM-DD");
	    console.log(today);
	    console.log(date);
	    if (date < today) {
//	    	alert("Please entered right date");
	    	document.getElementById("b_date").value = "";
	    	var rec = $('.currect_date')
			rec.show();
	    	var msg = $('.date_alert');
			msg.hide();
			var element_div = $("#display_timeslots");
			element_div.hide()
	     return true
	    }

		if(date !== undefined){
			ajax.jsonRpc("/shop/deliverydate", 'call', {
				'b_date' : date,
		
			}).then(function (data)
					{
				var msg = $('.date_alert');
					msg.show();
					var rec = $('.currect_date')
					rec.hide();
					var element_div = $("#display_timeslots");
					element_div.show()
				
				var element_div = $("#display_timeslots");
				element_div.empty();
				var i;
				var count = 16;
				var value = 0;
				var margin_top = '6%';
				var margin_top2 = '2.5%'
				for(i=0; i< data.length; i++){
					console.log(i);
					console.log(count);
					console.log(value);
					console.log(margin_top);
					if(i != 0 && i < 6)
					{
						value = count;
						count = count + 16;
						margin_top = '-5%';
						
					}
					
					console.log(i >=6 && i<=12);
					if (i >=6 && i<=12)
					{
						if( i == 6)
							{
							value = 0;
							margin_top = '2.5%';
							count = 16;
							}
						else{
							value = count;
							count = count + 16;
							margin_top = '-5%';
						}
						
						
					}
					var v = data[i]['value'];
					var d = '<time style="color: #5f5e97;">' + data[i]['value'] + '</time></div>';
					var d = '<div class="timeslot_' + String(data[i]['key']) + '" style="border: 2px solid #ccc;height: 31px;box-shadow: inset 1.5em 0em 0em #F0F0F0;width:14%;margin-top:' + margin_top +';border-radius:10%;margin-left:' + String(value)+ '%;">\
           			<input type="radio" name="choice-time" style="float:left; margin-top: 4%; width: 17%;" id="choice-delivery-times_'+ String(data[i]['key']) +'" value="' + v + '"/>\
               			<time style="color: #5f5e97; margin-left:6px">' + v + '</time></div>'
               		element_div.append(d);
				}
				});
		}
		
		});
	$("#display_timeslots").on("change",function()
	{	
	var date = $('#b_date').val();
	var s_id = $('#sale_order').val();
	var d = $("#display_timeslots input:radio:checked").val();
	ajax.jsonRpc("/shop/add_delivery_to_sale_order", 'call', {
		'delivery_date' : date,
		'order' : s_id,
		'time' : d,
	}).then(function (data){
		
			return true
	});
	}
	);
	
	$("#disable_comment").on("change",function()
	{	
	var comment = $('#disable_comment').val();
	var s_id = $('#sale_order').val();
	ajax.jsonRpc("/shop/add_comment_to_sale_order", 'call', {
		'comment' : comment,
		'order' : s_id,
	}).then(function (data){
			return true
	});
	}
	);
	});

});
	




	
