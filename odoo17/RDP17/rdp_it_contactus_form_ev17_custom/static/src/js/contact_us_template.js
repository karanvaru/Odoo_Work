const toggleSwitch = document.getElementById("toggle_switch_type_form");
const emailInput = document.querySelector('.email-input');
const serialInput = document.querySelector('.serial-input');


$('#toggle_switch_type_form').on('change', function(){
    const isChecked = toggleSwitch.checked;
    if (isChecked) {
        window.location.href = '/asp_type';
    } else {
        window.location.href = '/customer_type';
    }
});

if (emailInput) {
    emailInput.addEventListener('blur', function () {
    const email = emailInput.value.trim();
    if (email) {
        $.ajax({
            url: '/fetch_data',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({ partner_email: email }),
            contentType: 'application/json',
            success: function(response) {
                populateFields(response, 'email');
            },
            error: function(xhr, status, error) {
                console.error("Error while fetching contact data:", error);
            }
        });
    }
    });
}

if (serialInput) {
    serialInput.addEventListener('blur', function () {
    const serial = serialInput.value.trim();
    $.ajax({
        url: '/fetch_data',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify({ serial_no: serial }),
        contentType: 'application/json',
        success: function(response) {
            populateFields(response, 'serial');
        },
        error: function(xhr, status, error) {
            console.error("Error while fetching product data:", error);
        }
    });
    });
}

function populateFields(response, fieldType) {
    const data = response.result || {};
    if (data && response.result.success === true) {
        if (fieldType === 'email') {
            const nameField = document.querySelector('[name="partner_name"]');
            const mobileField = document.querySelector('[name="contact_mobile"]');
            const emailField = document.querySelector('[name="partner_email"]');

            if (nameField) {
                nameField.value = data.partner_name || '';
                nameField.readOnly = !!data.partner_name;
            }
            if (mobileField) {
                mobileField.value = data.contact_mobile || '';
                mobileField.readOnly = !!data.contact_mobile;
            }
            if (emailField) {
                emailField.value = data.partner_email || emailInput.value;
                emailField.readOnly = false;
            }
        } else if (fieldType === 'serial') {
            const productField = document.querySelector('[name="product_name"]');
            if (productField) {
                productField.value = data.product_name || '';
                productField.readOnly = true;
            }else{
                console.error("productField not found.");
            }
        }
    }
    else {
        if (fieldType === 'email') {
            const nameField = document.querySelector('[name="partner_name"]');
            const mobileField = document.querySelector('[name="contact_mobile"]');
            const emailField = document.querySelector('[name="partner_email"]');

            if (nameField) {
                nameField.value = '';
                nameField.readOnly = false;
            }
            if (mobileField) {
                mobileField.value = '';
                mobileField.readOnly = false;
            }
            if (emailField) {
                emailField.value = emailInput.value;
                emailField.readOnly = false;
            }
        } else if (fieldType === 'serial') {
            const productField = document.querySelector('[name="product_name"]');

            if (productField) {
                productField.value = '';
                productField.readOnly = true; ;
            }
            alert("No product found with the specified serial number.");
        }
    }
}

