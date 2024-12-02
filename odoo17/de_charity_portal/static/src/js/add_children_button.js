/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";
var rowCounter = 2;

    $(document).on('click', '#add-row-delete', function () {
         const rowId = $(this).closest('tr').find('td:first input').val();
        $(this).closest('tr').remove();
            jsonrpc('/delete/row', {
            'child_id': rowId,
        })
    });


$(document).on('click', '#add-row-button', function () {
    event.preventDefault();
    var tableBody = document.querySelector('#dynamic-table tbody');
    var newRow = document.createElement('tr');

    var column0 = document.createElement('td');
    var column1 = document.createElement('td');
    var column2 = document.createElement('td');
    var column3 = document.createElement('td');
    var column4 = document.createElement('td');
    var column5 = document.createElement('td');
    var column6 = document.createElement('td');

    column0.innerHTML = '<input type="hidden" class="form-control"  name="child_id_' + rowCounter + '" placeholder="Enter Id"/>';
    column1.innerHTML = '<input type="text" class="form-control"  name="child_name_' + rowCounter + '" placeholder="Enter Name"/>';
    column2.innerHTML = '<input type="number" class="form-control"  name="child_age_' + rowCounter + '"placeholder="Enter Age"/>';
    column3.innerHTML = `<input class="form-check-input" type="radio" id="living_yes_${rowCounter}" name="child_living_${rowCounter}" value="True" />
                         <label class="form-check-label" for="living_yes_${rowCounter}">Yes</label>
                         <input class="form-check-input" type="radio" id="living_no_${rowCounter}" name="child_living_${rowCounter}" value="False" />
                         <label class="form-check-label" for="living_no_${rowCounter}">No</label>`;
    column4.innerHTML = '<input type="text" class="form-control"  name="child_edu_' + rowCounter + '"placeholder="Enter Education"/>';
    column5.innerHTML = `<select class="form-control" name="child_marital_${rowCounter}">
                             <option value="" disabled selected>Select..</option>
                             <option value="SINGLE">Single</option>
                             <option value="STEADY">Going Steady</option>
                             <option value="MARRIED">Married</option>
                             <option value="DIVORCED">Divorced</option>
                             <option value="WIDOWED">Widowed</option>
                        </select>`;

    column6.innerHTML = '<button type="button" class="btn btn-primary"  id="add-row-delete"> <i class="fa fa-trash"/> </button>';

    column0.style.display = 'none';
    newRow.appendChild(column0);
    newRow.appendChild(column1);
    newRow.appendChild(column2);
    newRow.appendChild(column3);
    newRow.appendChild(column4);
    newRow.appendChild(column5);
    newRow.appendChild(column6);

    tableBody.appendChild(newRow);
    rowCounter++;
});

