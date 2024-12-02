odoo.define('cue_website.recruitment_academic_form', function(require) {
	'use.strict';
    require('web.dom_ready');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

//$(document).ready(function(){
//console.log("+++aaaaaaaaaaaaaaaaaaaaaaaaaaa")
//
//	function logSubmit(event) {
//	 var phone = self.el.querySelector('#phone')['value'];
//
//	var regex1 =/^[0-9]{10}$/;
//
//
//	 if (!regex1.test(phone)) {
//	     this.displayNotification({
//            type: 'warning',
//            message: _t('Please Fill Valid Data.'),
//            sticky: false,
//        });
//	 }
//
//	    console.log("++++++++++++=aaaaaaaaaaaaaa")
//	}
//
//const form = document.getElementById("academy_form");
// console.log("+++++++++++++++++formformformform",form)
//    if(form){
//        console.log("+++++++++++++++++aaaaaaaaaaaaaaa")
//        form.addEventListener("submit", logSubmit);
//    }
//});

});