odoo.define('cue_website.CueHelpme', function (require) {
'use strict';

const dom = require('web.dom');
var publicWidget = require('web.public.widget');
// var PortalSidebar = require('portal.PortalSidebar');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.CueHelpme = publicWidget.Widget.extend({
    selector: '.cue_helpme',
    events: {
        'click .__qustion_start_btn': '_onClickStart',
        'click .__qustion_next_btn': '_onClickNext',
        'click .__qustion_submit_btn': '_onClickSubmit',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
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
			params: {}
//            model: 'product.tag.category',
//            method: 'action_prepare_question',
//            args: [],
        }).then(function (html){
            self.$('.__qustion_box').html(html);
            $target.addClass('invisible');
        });
    },

    _onClickNext: function(ev) {
        let $target = $(ev.currentTarget);
        let $tagBox = $target.parents('.tab_box');
        if($tagBox.find('input:checked').length) {
            $tagBox.addClass('d-none');
            $tagBox.next().removeClass('d-none');
        }else {
            this.displayNotification({
                type: 'warning',
                message: _t('Please select Any Option.'),
                sticky: false,
            });
        }
    },

    _onClickSubmit: function(ev) {
        let $target = $(ev.currentTarget);
        let $tagBox = $target.parents('.tab_box');
        if($tagBox.find('input:checked').length) {
            let form_data = $target.closest('form').serializeArray();
            this._rpc({
				route: '/action_question_result/',
				params: {'form_data': form_data}
//                model: 'product.tag.category',
//                method: 'action_question_result',
//                args: [form_data],
            }).then(function (html){
                self.$('.__qustion_box').html(html);
            });
        }else {
            this.displayNotification({
                type: 'warning',
                message: _t('Please select Any Option.'),
                sticky: false,
            });
        }
    }
});
});
