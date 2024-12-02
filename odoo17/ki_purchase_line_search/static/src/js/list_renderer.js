/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";


patch(ListRenderer.prototype, {
		setup() {
        super.setup();
		const { context, resModel } = this.env.searchModel;
		this.curretModelName = resModel;
	},




	purchase_line_input(ev) {
		let $input = $(ev.currentTarget).val();
		console.log("__________________  $input  ",$input)
		let table = document.getElementsByClassName("o_list_table table table-sm table-hover table-striped")
//		console.log("_________________   `table",table)

		if ($input) {
//		    console.log("_____________  $input",$input)
		    let filter = $input.toUpperCase();
            for (var i = 0; i < table[0].rows.length; i++) {
//                console.log("___________  table[0].rows.length",table[0].rows.length)
                if (table[0].rows[i].className.indexOf("o_data_row") > -1) {
//                    console.log("_____    table[0].rows[i].textContent",table[0].rows[i].textContent)
//                    console.log("_____    table[0].rows[i].innerText",table[0].rows[i].innerText)
                    var txtValue = table[0].rows[i].textContent || table[0].rows[i].innerText;
//                    console.log("______________   txtValue",txtValue)
//                    console.log("______________   filter",filter)
//                    console.log("______________   txtValue",txtValue.toUpperCase().indexOf(filter))
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
//                         console.log("______________   if")
                        table[0].rows[i].hidden = false
                    }
                    else {
//                        console.log("______________   Else")
                        table[0].rows[i].hidden = true
                    }
                }
            }
        }
        else {
            for (var i = 0; i < table[0].rows.length; i++) {

                table[0].rows[i].hidden = false
            }
        }
	},

});

