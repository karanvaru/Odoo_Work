/* @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
const { DateTime } = luxon;

// const DateTimePickerWidget = require('web.datetime_picker_widget');

publicWidget.registry.portalWidgetJobsPortal = publicWidget.Widget.extend({
    selector: '.add_job_hr_form',
    start: function() {
        this._super.apply(this, arguments);
        var self = this;
        this.$("#job_functional_area").select2({
            placeholder: "Select job by function area",
            allowClear: true
        });
        this.$allDates = this.$el.find('.date');
        for (const field of this.$allDates) {
            const input = field.querySelector("input");
            const defaultValue = input.getAttribute("value");
            this.call("datetime_picker", "create", {
                target: input,
                pickerProps: {
                    type: field.matches('.date') ? 'date' : 'datetime',
                    value: defaultValue && DateTime.fromSeconds(parseInt(defaultValue)),
                },
            }).enable();
        }
        this.$allDates.addClass('s_website_form_datepicker_initialized');
        return this._super.apply(this, arguments);
    },
});

publicWidget.registry.recruitmentWidgetportal = publicWidget.Widget.extend({
    selector: '.main_form_job_cl_ap',
    events: {
        'click .next-step': '_onClickNextStep',
        'click .prev-step': '_onClickPrevStep',
        'click .add_new_row_for_job': '_onClickNewRowForJob',
        'submit form#hr_recruitment_form': '_onSubmit',
        'change .applicant_country_cl': '_onClickApplicantCountry_cl'
    },
    init: function() {
        this._super.apply(this, arguments);
    },
    start: function() {
        var self = this;
        this.$allDates = this.$el.find('.date');
        for (const field of this.$allDates) {
            const input = field.querySelector("input");
            const defaultValue = input.getAttribute("value");
            this.call("datetime_picker", "create", {
                target: input,
                pickerProps: {
                    type: field.matches('.date') ? 'date' : 'datetime',
                    value: defaultValue && DateTime.fromSeconds(parseInt(defaultValue)),
                    maxDate: luxon.DateTime.now(),
                },
            }).enable();
        }
        this.$allDates.addClass('s_website_form_datepicker_initialized');
        return this._super.apply(this, arguments);
    },
    _onSubmit: function(ev) {
        var disc = {
            'academic_details': [],
            'certificate_details': [],
            'professional_details': []
        }
        var academic_dats = $(ev.currentTarget).find('.academic_details_info_cl tr').toArray();
        var certificate_dats = $(ev.currentTarget).find('.certificate_details_info_cl tr').toArray();
        var professional_dats = $(ev.currentTarget).find('.professional_details_info_cl tr').toArray();
        academic_dats.forEach(function(el, val) {
            var personal_course_name = $(el).find("input[name='personal_course_name']").val();
            var personal_branch = $(el).find("input[name='personal_branch']").val();
            var personal_organization = $(el).find("input[name='personal_organization']").val();
            var personal_start_date = $(el).find("input[name='personal_start_date']").val();
            var personal_end_date = $(el).find("input[name='personal_end_date']").val();
            var personal_marks = $(el).find("input[name='personal_marks']").val();
            disc['academic_details'].push({
                'course_name': personal_course_name,
                'branch': personal_branch,
                'organization': personal_organization,
                'start_date': personal_start_date,
                'end_date': personal_end_date,
                'marks': personal_marks
            });
        });
        certificate_dats.forEach(function(el, val) {
            var certificate_course_name = $(el).find("input[name='certificate_course_name']").val();
            var certificate_branch = $(el).find("input[name='certificate_branch']").val();
            var certificate_organization = $(el).find("input[name='certificate_organization']").val();
            var certificate_certificate_des = $(el).find("input[name='certificate_certificate_des']").val();
            var certificate_start_date = $(el).find("input[name='certificate_start_date']").val();
            var certificate_end_date = $(el).find("input[name='certificate_end_date']").val();
            var filedata = $(el).find("input[name='attachemnt_ids']").attr('data_type_64');
            var filename = $(el).find("input[name='attachemnt_ids']").attr('data_file_name');
            var filetype = $(el).find("input[name='attachemnt_ids']").attr('data_file_type');
            disc['certificate_details'].push({
                'course_name': certificate_course_name,
                'branch': certificate_branch,
                'organization': certificate_organization,
                'start_date': certificate_start_date,
                'end_date': certificate_end_date,
                'certificate_des': certificate_certificate_des,
                'filename': filename,
                'filedata': filedata,
                'filetype': filetype
            });
        });
        professional_dats.forEach(function(el, val) {
            var professional_name = $(el).find("input[name='professional_name']").val();
            var professional_organization = $(el).find("input[name='professional_organization']").val();
            var professional_department = $(el).find("input[name='professional_department']").val();
            var professional_work_des = $(el).find("input[name='professional_work_des']").val();
            var professional_work_exp = $(el).find("input[name='professional_work_exp']").val();
            var professional_start_date = $(el).find("input[name='professional_start_date']").val();
            var professional_end_date = $(el).find("input[name='professional_end_date']").val();
            var professional_projects = $(el).find("input[name='professional_projects']").val();

            disc['professional_details'].push({
                'name': professional_name,
                'department': professional_department,
                'organization': professional_organization,
                'work_des': professional_work_des,
                'work_exp': professional_work_exp,
                'start_date': professional_start_date,
                'end_date': professional_end_date,
                'projects': professional_projects
            });
        });
        var datas = JSON.stringify(disc);
        $(ev.currentTarget).append("<input type='text' class='d-none' name='all_details_data' value='" + datas + "'/>");
    },
    _onClickNextStep: function(ev) {
        var $active = $('.main_form_job_cl_ap .wizard .nav-tabs li.active');
        this._nextTab($active);
    },
    _nextTab: function(elem) {
        var cel = $(elem).find('a[data-bs-toggle="tab"]').attr('href');
        var fel = $('.main_form_job_cl_ap ' + cel);
        var flag = this._check_required_fields(fel);
        if (flag) {
            return false;
        }
        $(elem).next().removeClass('disabled');
        $('.main_form_job_cl_ap .nav-tabs > li.active').removeClass('active')
        $(elem).next().find('a[data-bs-toggle="tab"]')[0].click();
        $(elem).next().find('a[data-bs-toggle="tab"]').parent().addClass('active');
    },
    _onClickPrevStep: function(ev) {
        var $active = $('.main_form_job_cl_ap .wizard .nav-tabs li.active');
        this._prevTab($active);
    },
    _prevTab: function(elem) {
        $('.main_form_job_cl_ap .nav-tabs > li.active').removeClass('active')
        $(elem).prev().find('a[data-bs-toggle="tab"]')[0].click();
        $(elem).prev().find('a[data-bs-toggle="tab"]').parent().addClass('active');
    },
    _check_required_fields: function(elem) {
        var eml = $(elem).find("input[required], select[required]");
        $(elem).find("input[required], select[required]").removeClass('error_msg_cl');
        var flag = false;
        var emlArray = eml.toArray();
        emlArray.forEach(function(elmv) {
            if (!$(elmv).val()) {
                $(elmv).addClass('error_msg_cl');
                flag = true
            }
        });
        return flag;
    },
    _onClickNewRowForJob: function(ev) {
        var self = this;
        var ptype = $(ev.currentTarget).attr('data-type');
        jsonrpc('/job/add/row', {
            'type': ptype,
        }).then((data) => {
            var $tableBody = $(ev.currentTarget).closest('.card-body').find('table tbody');
            $tableBody.append(data.data);

            $tableBody.on('click', '.remove_btn_row', function(ev) {
                self.remove_added_row(ev);
            });
            $tableBody.on('change', ".job_apply_form_cl input[name='attachemnt_ids']", function(ev) {
                self.previewFileCertificate(ev);
            });

            self.$allDates = $tableBody.find('.datepicker_start, .datepicker_end')
            for (const field of self.$allDates) {
                const input = field.querySelector("input");
                const defaultValue = input.getAttribute("value");
                this.call("datetime_picker", "create", {
                    target: input,
                    pickerProps: {
                        type: field.matches('.datepicker_start, .datepicker_end') ? 'date' : 'datetime',
                        value: defaultValue && DateTime.fromSeconds(parseInt(defaultValue)),
                    },
                }).enable();
            }
            self.$allDates.addClass('s_website_form_datepicker_initialized');
        })
    },

    _onClickApplicantCountry_cl: function(ev) {
        var countryID = $('#select_country').val();
        jsonrpc('/change_country', {
            'country_id': countryID
        }).then(function(state) {
            if (state.length != 0) {
                const state_select = document.getElementById('select_state');
                $(state_select).css("display", "block");
                $(state_select).empty();
                for (let i = 0; i < state.length; i++) {
                    const state_select_item = document.createElement("option");
                    state_select_item.innerText = state[i].name;
                    $(state_select_item).attr('value', state[i].id);
                    state_select.appendChild(state_select_item);
                }

            } else {
                const state_select = document.getElementById('select_state')
                const state_select_item = document.createElement("option");
                $(state_select).empty();
                state_select_item.innerText = 'Select state';
                $(state_select_item).attr('value', '');
                state_select.appendChild(state_select_item);

            }

        });
    },
    remove_added_row: function(ev) {
        $(ev.currentTarget).closest('tr').remove();
    },
    previewFileCertificate: function(ev) {
        var file = ev.currentTarget.files[0];
        const reader = new FileReader();
        reader.addEventListener("load", function() {
            var b64 = reader.result.replace(/^data:.+;base64,/, '')
            $(ev.currentTarget).attr('data_type_64', b64);
            $(ev.currentTarget).attr('data_file_name', file.name);
            $(ev.currentTarget).attr('data_file_type', file.type);
        }, false);

        if (file) {
            reader.readAsDataURL(file);
        }
    },
});