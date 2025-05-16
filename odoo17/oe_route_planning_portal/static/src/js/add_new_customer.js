$(document).ready(function() {

    $('#opencustomerModalButton').on('click', function() {
        $('#customerModalCenter').modal('show');
    });

    $('#closecustomerModalButton').on('click', function() {
        location.reload();
        $('#customerModalCenter').modal('hide');
    });
    $('#closecustomerEditModalButton').on('click', function() {
        location.reload();
        $('#customerModal').modal('hide');
    });
    $('#closeviewcustomerEditModalButton').on('click', function() {
        $('#viewCustomerModal').modal('hide');
    });


    $('#submitcustomerFormBtn').on('click', function() {
        const fileInput = $('#customer_image')[0];
        const file = fileInput.files[0];
        const customer_image = $('#customer_image')[0];
        const customer_name = $('#customer_name').val();
        const taxid = $('#vat').val();
        const licence = $('#licence').val();
        const street = $('#street').val();
        const city = $('#city').val();
        const country = $('#country').val();
        const state = $('#state').val();
        const zip = $('#zip').val();

        if (customer_image === '' || customer_name === '' || taxid === ''  || licence === ''  || street === '' || city === '' || country === '' || state === '' || zip === '') {
//        alert('Please fill in all required fields.');
        $('#message').html('<div class="alert alert-danger" role="alert">Please fill in all required fields.</div>');
        if (customer_image === '') $('#customer_image').addClass('alert-danger'); else $('#customer_image').removeClass('alert-danger');
        if (customer_name === '') $('#customer_name').addClass('alert-danger'); else $('#customer_name').removeClass('alert-danger');
        if (taxid === '') $('#vat').addClass('alert-danger'); else $('#vat').removeClass('alert-danger');
        if (licence === '') $('#licence').addClass('alert-danger'); else $('#licence').removeClass('alert-danger');
        if (street === '') $('#street').addClass('alert-danger'); else $('#street').removeClass('alert-danger');
        if (country === '') $('#country').addClass('alert-danger'); else $('#country').removeClass('alert-danger');
        if (state === '') $('#state').addClass('alert-danger'); else $('#state').removeClass('alert-danger');
        if (city === '') $('#city').addClass('alert-danger'); else $('#city').removeClass('alert-danger');
        if (zip === '') $('#zip').addClass('alert-danger'); else $('#zip').removeClass('alert-danger');
        return;
    }

        if (file) {
            let reader = new FileReader();
            reader.onload = function(event) {
                let base64String = event.target.result.split(',')[1];

                $.ajax({
                    url: '/new_customer/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                        customer_image: base64String,
                        customer_name: $('#customer_name').val(),
                        taxid: $('#vat').val(),
                        licence: $('#licence').val(),
                        street: $('#street').val(),
                        street2: $('#street2').val(),
                        country: $('#country').val(),
                        city: $('#city').val(),
                        state: $('#state').val(),
                        zip: $('#zip').val(),
                        notes: $('#notes').val()
                    }),
                    success: function(response) {
                        if (response.success) {
                        $('#submitcustomerFormBtn').prop('disabled', true);
                            $('#message').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalFormcustomer')[0].reset();

                            setTimeout(function() {
                                location.reload();
                            }, 3000);
                        } else {
                            $('#message').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                        $('#message').html('<div class="alert alert-danger" role="alert">Error: ' + error + '</div>');
                    }
                });
            };

            reader.readAsDataURL(file);
        } else {
            alert('Please select an image file.');
        }
    });
});





$(document).ready(function(){
    $(document).on("click", ".edit-customer", function(){
        var customerId = $(this).data("customer-id");
        $.ajax({
            url: '/get/customer/values',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                'customer_id': customerId,
            }),
            success: function(response) {
            const countries = response.countries;
        const states = response.states;

        const countryOptions = countries.map(country => {
            const selected = response.country_id === country.id ? 'selected' : '';
            return `<option value="${country.id}" ${selected}>${country.name}</option>`;
        }).join('');

        const stateOptions = states.map(state => {
            const selected = response.state_id === state.id ? 'selected' : '';
            return `<option value="${state.id}" ${selected}>${state.name}</option>`;
        }).join('');


var modalBodyHtml = `
    <form id="modalUpdateFormcustomer">
        <div class="form-group">
            <label for="customer_image">Customer Image</label>
            <div id="current-image">
                <img src="${response.customer_image_url}" class="img-fluid" id="customer_image_update" alt="customer Image" style="width:100px">
            </div>
            <div id="image-preview" style="display:none;">
                <img src="" id="preview-image" alt="Preview Image" style="width:100px">
            </div>
            <input type="file" id="new-image" accept="image/*">
        </div>
        <div class="form-group">
            <label for="customer_name">Customer Name</label>
            <input type="text" class="form-control" id="customer_name_update" value="${response.customer_name}">
        </div>
        <div class="form-group">
            <label for="inputField3">VAT</label>
            <input type="text" class="form-control" id="vat_update" value="${response.taxid}"/>
        </div>
        <div class="form-group">
            <label for="inputField3">License</label>
            <input type="text" class="form-control" id="licence_update" value="${response.licence}"/>
        </div>
        <div class="form-group">
            <label for="address">Address</label>
            <input type="text" class="form-control" id="street_update" value="${response.street}"/>
            <input type="text" class="form-control" id="street2_update" value="${response.street2}"/>
        </div>
        <div class="form-group">
            <label for="city">City</label>
            <input type="text" class="form-control" id="city_update" value="${response.city}"/>
        </div>
        <div class="form-group">
            <label for="country">Country</label>
            <select class="form-control" id="country_update">
                ${countryOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="state">State</label>
            <select class="form-control" id="state_update">
                ${stateOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="zip">ZIP</label>
            <input type="text" class="form-control" id="zip_update" value="${response.zip}"/>
        </div>
        <div class="form-group">
            <label for="inputField1">Description</label>
            <input type="text" class="form-control" id="notes_update" value="${response.notes.replace(/<[^>]+>/g, '')}">
            <input type="hidden" class="form-control" id="customer_id_update" value="${response.customer_id}">
        </div>
    </form>
    <div id="message_update" class="mt-3"></div>
`;


                // Set the HTML content of the modal body
                $("#customerModal .modal-body").html(modalBodyHtml);

                // Add event listener to file input field
                $("#new-image").on("change", function(){
                    var file = this.files[0];
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        $("#preview-image").attr("src", e.target.result);
                        $("#current-image").hide();
                        $("#image-preview").show();
                    };
                    reader.readAsDataURL(file);
                });

                $("#customerModal").modal("show");
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error(error);
            }
        });
    });

    $("#updatecustomer").on("click", function(){
        const fileInput = $('#new-image')[0];
        const file = fileInput.files[0];
        if (!file){
        const fileInput = $('#customer_image_update');
        const file = fileInput.files;
        }

        if (file) {
            let reader = new FileReader();
            reader.onload = function(event) {
                let base64String = event.target.result.split(',')[1];

                $.ajax({
                    url: '/new_customer/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                       customer_image: base64String,
                        customer_name: $('#customer_name_update').val(),
                        taxid: $('#vat_update').val(),
                        licence: $('#licence_update').val(),
                        street: $('#street_update').val(),
                        street2: $('#street2_update').val(),
                        country: $('#country_update').val(),
                        state: $('#state_update').val(),
                        zip: $('#zip_update').val(),
                        notes: $('#notes_update').val(),
                        customer_id: $('#customer_id_update').val(),
                    }),
                    success: function(response) {
                        if (response.success) {
                            $('#message_update').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalUpdateFormcustomer')[0].reset();

                            setTimeout(function() {
                                location.reload();
                            }, 3000);
                        } else {
                            $('#message_update').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                        $('#message_update').html('<div class="alert alert-danger" role="alert">Error: ' + error + '</div>');
                    }
                });
            };

            reader.readAsDataURL(file);
        } else {
            $.ajax({
                    url: '/new_customer/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                        customer_name: $('#customer_name_update').val(),
                        taxid: $('#vat_update').val(),
                        licence: $('#licence_update').val(),
                        street: $('#street_update').val(),
                        street2: $('#street2_update').val(),
                        country: $('#country_update').val(),
                        state: $('#state_update').val(),
                        zip: $('#zip_update').val(),
                        notes: $('#notes_update').val(),
                        customer_id: $('#customer_id_update').val(),
                    }),
                    success: function(response) {
                        if (response.success) {
                            $('#message_update').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalUpdateFormcustomer')[0].reset();

                            setTimeout(function() {
                                location.reload();
                            }, 3000);
                        } else {
                            $('#message').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', error);
                        $('#message_update').html('<div class="alert alert-danger" role="alert">Error: ' + error + '</div>');
                    }
                });
        }
    });

    $(document).on("click", ".view-customer", function(){
        var customerId = $(this).data("customer-id");
        $.ajax({
            url: '/get/customer/values',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                'customer_id': customerId,
            }),
            success: function(response) {
            const countries = response.countries;
        const states = response.states;

        const countryOptions = countries.map(country => {
            const selected = response.country_id === country.id ? 'selected' : '';
            return `<option value="${country.id}" ${selected}>${country.name}</option>`;
        }).join('');

        const stateOptions = states.map(state => {
            const selected = response.state_id === state.id ? 'selected' : '';
            return `<option value="${state.id}" ${selected}>${state.name}</option>`;
        }).join('');


var modalBodyHtml = `
    <form id="modalViewFormcustomer">
        <div class="form-group">
            <label for="customer_image">Customer Image</label>
            <div id="current-image">
                <img src="${response.customer_image_url}" class="img-fluid" id="customer_image_view" alt="customer Image" style="width:100px" readonly="1">
            </div>
        </div>
        <div class="form-group">
            <label for="customer_name">Customer Name</label>
            <input type="text" class="form-control" id="customer_name_view" value="${response.customer_name}" readonly="1">
        </div>
        <div class="form-group">
            <label for="inputField3">VAT</label>
            <input type="text" class="form-control" id="vat_view" value="${response.taxid}" readonly="1"/>
        </div>
        <div class="form-group">
            <label for="inputField3">License</label>
            <input type="text" class="form-control" id="licence_view" value="${response.licence}" readonly="1"/>
        </div>
        <div class="form-group">
            <label for="address">Address</label>
            <input type="text" class="form-control" id="street_view" value="${response.street}" readonly="1"/>
            <input type="text" class="form-control" id="street2_view" value="${response.street2}" readonly="1"/>
        </div>
        <div class="form-group">
            <label for="city">City</label>
            <input type="text" class="form-control" id="city_view" value="${response.city}" readonly="1"/>
        </div>
        <div class="form-group">
            <label for="country">Country</label>
            <select class="form-control" id="country_view" readonly="1">
                ${countryOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="state">State</label>
            <select class="form-control" id="state_view" readonly="1">
                ${stateOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="zip">ZIP</label>
            <input type="text" class="form-control" id="zip_view" value="${response.zip}" readonly="1"/>
        </div>
        <div class="form-group">
            <label for="inputField1">Description</label>
            <input type="text" class="form-control" id="notes_view" value="${response.notes.replace(/<[^>]+>/g, '')}" readonly="1"/>
        </div>
    </form>
    <div id="message_update" class="mt-3"></div>
`;
                $("#viewCustomerModal .modal-body").html(modalBodyHtml);
                $("#viewCustomerModal ").modal("show");
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error(error);
            }
        });
    });
});

$(document).ready(function(){
        var numberInputs = document.querySelectorAll('input[type="number"]');

        numberInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                if (this.value < 0) {
                    this.value = 0;
                }
            });
        });
    });

    $(document).ready(function(){
    var searchInput = document.getElementById('searchInput');

        // Check if the element exists before adding the event listener
        if (searchInput) {
            searchInput.addEventListener('input', function(event) {
                if (event.target.value === '') { // Check if the input field is empty
                    refreshUrl();
                }
            });
        }

    function refreshUrl() {
        // Get the current URL without any query parameters
        var url = window.location.href.split('?')[0];
        // Reload the page with the new URL
        window.location.href = url;
    }

    });


    function updateStates() {
        var countryId = document.getElementById('country').value;
        var stateSelect = document.getElementById('state');
        
        // Clear the current options
        stateSelect.innerHTML = '<option value="">Select a state</option>';

        if (countryId) {
            fetch('/get_states?country_id=' + countryId)
                .then(response => response.json())
                .then(data => {
                    data.forEach(state => {
                        var option = document.createElement('option');
                        option.value = state.id;
                        option.text = state.name;
                        stateSelect.add(option);
                    });
                });
        }
    }
