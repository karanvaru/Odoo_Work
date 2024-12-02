odoo.define('bi_helpdesk_ticket_timer.helpdesk_ticket_timer', function (require) {

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var fields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var time = require('web.time');

var _t = core._t;

var TimeCounter = AbstractField.extend({
    supportedFieldTypes: [],
    /**
     * @override
     */
    willStart: function () {
        var self = this;
        var def = this._rpc({
            model: 'ticket.timer',
            method: 'search_read',
            domain: [
                ['helpdesk_ticket_id', '=', this.record.data.id],
            ],
        }).then(function (result) {
            if (self.mode === 'readonly') {
                var currentDate = new Date();
                self.duration = 0;
                _.each(result, function (data) {
                    self.duration += data.pause_time ?
                        self._getDateDifference(data.play_time, data.pause_time) :
                        self._getDateDifference(time.auto_str_to_date(data.play_time), currentDate);
                });
            }
        });
        return $.when(this._super.apply(this, arguments), def);
    },

    destroy: function () {
        this._super.apply(this, arguments);
        clearTimeout(this.timer);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    isSet: function () {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Compute the difference between two dates.
     *
     * @private
     * @param {string} dateStart
     * @param {string} dateEnd
     * @returns {integer} the difference in millisecond
     */
    _getDateDifference: function (dateStart, dateEnd) {
        return moment(dateEnd).diff(moment(dateStart));
    },
    /**
     * @override
     */
    _render: function () {
        this._startTimeCounter();
    },
    /**
     * @private
     */
    _startTimeCounter: function () {
        var self = this;
        clearTimeout(this.timer);
        if (this.record.data.run_timer) {
            this.timer = setTimeout(function () {
                self.duration += 1000;
                self._startTimeCounter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
        this.$el.html($('<span style="color:red;font-weight: bold;margin-left:10px">' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
    },
});

field_registry
    .add('ticket_timer', TimeCounter);
});
