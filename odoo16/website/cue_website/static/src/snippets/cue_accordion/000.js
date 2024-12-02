odoo.define('cue_website.Accodion', function (require) {
'use strict';

const dom = require('web.dom');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.Accodion = publicWidget.Widget.extend({
    selector: '.accordion',
    events: {
//        'click .__qustion_start_btn': '_onClickStart',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
		console.log("HIIIIIIIIIMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",this.target)
		
		var a = $(this.target).find('a:first');
			var div = $(this.target).find('div.collapse:first');

		a.attr('aria-expanded', 'true')
		a.removeClass('collapsed')
		div.addClass('show')
		
	//	a.toggle('hide');
		console.log("a ...............",a)
		
        return def;
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickStart: function (ev) {
        ev.preventDefault();
        var self = this;
        let $target = $(ev.currentTarget);
        this._rpc({
			route: '/action_prepare_question/',
        }).then(function (html){
            self.$('.__qustion_box').html(html);
            $target.addClass('invisible');
        });
    },

});
});
