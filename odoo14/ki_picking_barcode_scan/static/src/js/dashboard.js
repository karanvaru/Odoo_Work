odoo.define("ki_picking_barcode_scan.search_picking", function(require) {
	"use strict";
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var ajax = require('web.ajax');
	var operation_types;
    var move_line_lst = [];
	var PosDashboard = AbstractAction.extend({
		template: 'Dashboard',

		events: {
			'change #picking_name': 'search_picking',
			'change #picking_product': 'search_products',
			'change #picking_product_lot': 'search_products',
			'change #search_by_lot': 'search_by_lot',
			'click #picking_validate': 'on_click_validate',
			'click #next_button': 'next_button',
			'click #form': 'click_form',
		},

		init: function(parent, context) {
			this._super(parent, context);
			this.dashboards_templates = ['DashboardOrders'];
		},

		willStart: function() {
			var self = this;
			return this._super()
				.then(function() {
					var def2 = self._rpc({
						model: 'search.barcode.product.picking.wizard',
						method: 'get_data'
					}).then(function(result) {
						self.stock_picking_dict = result['stock_picking_dict']
						self.product_ids_dict = result['product_ids_dict']
						self.picking_type_dict = result['picking_type_dict']
					});
					return $.when(def2);
				});
		},

		start: function() {
			var self = this;
			this.set('title', 'Dashboard');
			return this._super().then(function() {
				self.render_dashboards();
			});
		},

		next_button: function(ev) {
//			window.location.reload();
//            $('#picking_name').empty()
//            $('#picking_product').empty()
            $('#picking_product_lot').empty()
            $('#alert').hide()
            $('#picking_alert').hide()
            $('#picking_validate').hide()

            $('#product_lines').empty()
			$('#picking_name').val('');;
			$('#picking_number').val('');;
			$('#picking_product').val('');;

        },

        click_form: function(ev) {
            document.getElementById('picking_product_lot').value = '';
        },

		on_click_validate: function(ev) {
			var self = this;
			var $table = $("#move_lines")
			var rows = []
			var header = [];

			$table.find("thead th").each(function () {
			    header.push($(this).html());
			});

			$table.find("tbody tr").each(function () {
			    var row = {};

			    $(this).find("td").each(function (i) {
			        var key = header[i],
			            value = $(this).find('span').html();
			        row[key] = value;
			    });
			    rows.push(row);
			});
			var move_lines = JSON.stringify(rows)
			var picking_id = $('#picking_number').val();

			var def3 = self._rpc({
				route: '/validatestockpicking/',
				params: {
					'move_lines': move_lines,
					'picking_id': picking_id,
					'move_line_lst': move_line_lst,
				}
			}).then(function(result) {
			    if ('error' in result){

				    $('#picking_alert').show();
					$('#picking_alert').html('<span>' + result['error'] +  '</span>');
					$('#picking_validate').hide();
					//window.location.reload();
					$('#picking_name').val('');;
					$('#picking_number').val('');;
					$('#picking_product').val('');;
		            $('#product_lines').empty()
					
				}
				else {
		            $('#product_lines').empty()
					$('#picking_name').val('');;
					$('#picking_number').val('');;
					$('#picking_product').val('');;
				}
			});
            $('#product_lines').empty()
			$('#picking_name').val('');;
			$('#picking_number').val('');;
			$('#picking_product').val('');;
			//return $.when(def3);
		},


		search_picking: function(ev) {
			var self = this;
			var enter_picking_name = $('#picking_name').val();
			var picking_search_by = $('input[name="picking_search_by"]:checked').val();
            var picking_type = $('#picking_type').find(":selected").attr('data-key');

			self._rpc({
				route: '/searchpicking/',
				params: {
					'picking': enter_picking_name,
					'search_by': picking_search_by,
					'picking_type': picking_type,
				}
			}).then(function(result) {
                $('#product_lines').empty()
				$("#product_lines").append(result['message']);
				if ('error' in result){
				    $('#picking_alert').show();
				    $('#picking_validate').hide();
//					$('#alert').append('<span>' + result['error'] +  '</span>');
					$('#picking_alert').html('<span>' + result['error'] +  '</span>');
				}
				else {
				    $('#picking_alert').hide();
				    $('#picking_validate').show();
				}
			});
		},
        search_by_lot: function(ev) {
            var is_lot = $("#search_by_lot").is(":checked");
            if (is_lot === true) {
                $('#lot_no_box').show();
            }
            else{
                $('#lot_no_box').hide();
            }
        },

		search_products: function(ev) {

			var self = this;
			var picking_id = $('#picking_number').val();
			var product_search_by = $('input[name="product_search_by"]:checked').val();
			var product_name = $('#picking_product').val();
			var product_lot_number = $('#picking_product_lot').val();
			var is_lot = $("#search_by_lot").is(":checked");


			self._rpc({
				route: '/searchproduct/',
				params: {
					'picking': picking_id,
					'search_by': product_search_by,
					'product_name': product_name,
					'product_lot_number': product_lot_number,
					'is_lot': is_lot,
				}
			}).then(function (result) {
                if ('error' in result) {
                    $('#alert').show();
                    $('#alert').html('<span>' + result['error'] +  '</span>');
                } else {
                    $('#alert').hide();
                    var move_id = result['move_id']
                    var move_line = result['move_line']
                    var StockMoveLineQty = result['StockMoveLineQty']
                    var table = $('#move_lines')
                    var span = table.find('span#' + move_id);
                    var tr = table.find('tr#' + move_id);
                    var h6 = table.find('h6#' + move_id);
                    if (product_lot_number){
                        if (!move_line_lst.includes(move_line)) {
                            move_line_lst.push(move_line)
                            var qty = parseInt(span.text());
                            span.text(qty + StockMoveLineQty)
                            tr.removeClass('text-muted')

						var	current_lot = $(tr).find("td[name='lot_id']");
//							$(current_lot).find('span').text(product_lot_number)
							 current_lot.text(product_lot_number)
                        }
                        else{
                            alert("This Lot Number is Already Scanned.");
                            document.getElementById('picking_product_lot').value = '';
                        }
                    }
                    if (is_lot === false) {
                        if (!product_lot_number) {
                            if (!move_line_lst.includes(move_line)) {
                                move_line_lst.push(move_line)
                                var qty = parseInt(span.text());
                                span.text(qty + StockMoveLineQty)
                                tr.removeClass('text-muted')
                            }
                            else{
                                alert("This Lot Number is Already Scanned.");
                                document.getElementById('picking_product_lot').value = '';
                            }
                        }
                    }
                }
			});
		},

		render_dashboards: function() {
			var self = this;
			_.each(this.dashboards_templates, function(template) {
				self.$('.o_pos_dashboard').append(QWeb.render(template,
					{
						widget: self, stock_picking_dict: self.stock_picking_dict,
						widget: self, product_ids_dict: self.product_ids_dict,
						widget: self, picking_type_dict: self.picking_type_dict,
						//            widget: self, stock_move_dict:self.stock_move_dict,
					}));
			});
		},
	});
	core.action_registry.add('search_picking', PosDashboard);
	return PosDashboard;
});
