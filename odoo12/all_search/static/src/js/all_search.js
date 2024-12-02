odoo.define('all_search.allsearch', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');

    var SearchIconMenu = Widget.extend({
        template: 'SearchIcon',
        events: {
            'click .odoo_search_icon': '_showWindow',
            'click .odoo_search_click': '_search_result_query', 
            'keydown .open_search': '_search_result_query_enter',
            'click .odoo_search_close': '_close_search',
			'click .toggle-btn': 'fold_toggle',
            'click .fold-all': 'fold_all',
            'click .unfold-all': 'unfold_all',
            'click .show-more': 'show_more',
            'click .show-all': 'show_all',
            'click .rec-link': '_close_search_link',

        },
        start: function(){
          this._super();
          //this._onLoadGlobalSearch();
        },
//        _onLoadGlobalSearch: function(){
//            new GlobalSearch(this).appendTo($('body'));
//        },
        
		fold_toggle: function (ev) {
        	var ele = $(ev.target).next()
        	if (ele.height() == 0){
        		ele.css('height', '')
        	}
        	else{
	        	ele.css('height', '0px')
	        	ele.css('overflow-y', 'hidden')
        	}
        },
        
        fold_all: function (ev) {
        	$('.header-table-div').css('height', '0px')
        	$('.header-table-div').css('overflow-y', 'hidden')
        },
        
        unfold_all: function (ev) {
        	$('.header-table-div').css('height', '')
        },
        
        
        show_more: function (ev) {
        	var ele = $(ev.target).parents('.header-table-div')
        	var tr = $(ev.target).parents('td').parents('tr')
        	tr.nextAll().slice(0,11).css('display', 'table-row')
        	
        	$(ev.target).parents('td').parents('tr').remove()
        	
        },
        
        show_all: function (ev) {
        	var ele = $(ev.target).parents('.header-table-div')
        	var tr = $(ev.target).parents('td').parents('tr')
        	tr.nextAll().css('display', 'table-row')
        	
        	$(ev.target).parents('td').parents('tr').remove()
        	ele.find('.show-more').parents('tr').remove()
        	ele.find('.show-all').parents('tr').remove()
        },
        

        _search_result_query_enter: function (ev) {
        	var self = this
        	if (ev.keyCode == 13){
        		$(".search_field").prop('disabled', true);
        		self._search_result_query()
        	}
        },
        
        _search_result_query: function (ev) {
        	$(".search_field").prop('disabled', true);
        	
        	$('.search_results').css('display','block')
			//$('.dummy_class').css('display','block')
			$('.search_results').empty()
			$('.search_results').append("<div style='color: black; text-align: center; margin-top:60px; font-size: xx-large; color: #7d7cad;'><i class='fa fa-spinner fa-spin' /></div>")
        	
        	$.ajax({
		        url : "/fetch_query_data", 
				data: { query: $('.search_field').val(), stage: $('.search-level').val()},
				
				success : function(data) {
					if(data.indexOf('Please contact to Administrator') <= -1)
					{
						$('.search_results').css('display','block')
						$('.search_results').empty()
						$('.search_results').append(data)
						$(".search_field").prop('disabled', false);
						$('.unfold-all').css('display','unset');
						$('.fold-all').css('display','unset');
						$('.header-table-div').each(function(i, obj) {
							if( $(obj).find('.show-more').length == 0 ){
								$(obj).css('height', '')
				        	}
						});
					}
					else{
						$('.search_results').css('display','block');
						$('.search_results').empty();
						$('.search_results').append(data);
						$(".search_field").prop('disabled', false);
						$('.unfold-all').css('display','unset');
						$('.fold-all').css('display','unset');
					}
				},
				fail: function(data){
					$(".search_field").prop('disabled', false);
				},
		    });
        	
        },

        _close_search: function (ev) {
            ev.preventDefault();
            $('.search_results').empty()
			$('.search_field').val('')
			$('.search_results').css('display','none')
			$('.dummy_class').css('display','none')
            $('.search_panel').css('display', 'none');
        },
        
        _close_search_link: function (ev) {
            $('.search_results').empty();
            $('.search_field').val('');
            $('.search_results').css('display','none');
            $('.dummy_class').css('display','none');
            $('.search_panel').css('display', 'none');
        },
        
        _showWindow: function (ev) {
            ev.preventDefault();
            $('.search_panel').css('display', 'block');
            $('.search_field').focus();
        },

    });
    
    
    
    SystrayMenu.Items.push(SearchIconMenu)
});
