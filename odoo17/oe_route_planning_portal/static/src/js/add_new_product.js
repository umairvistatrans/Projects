$(document).ready(function() {
    $('#openProductModalButton').on('click', function() {
        $('#productModalCenter').modal('show');
    });

    $('#closeProductModalButton').on('click', function() {
        location.reload();
        $('#productModalCenter').modal('hide');
    });
    $('#closeProductEditModalButton').on('click', function() {
        location.reload();
        $('#productModal').modal('hide');
    });

    $('#submitProductFormBtn').on('click', function() {
        const fileInput = $('#product_image')[0];
        const file = fileInput.files[0];
        const product_image = $('#product_image')[0];
        const product_name = $('#product_name').val();
        const product_type = $('#product_type').val();
        const brand = $('#brand').val();
        const internal_reference = $('#internal_reference').val();
        const notes = $('#notes').val();

        if (product_image === '' || product_name === '' || product_type === ''|| brand === ''|| internal_reference === '') {
//        alert('Please fill in all required fields.');
        $('#message').html('<div class="alert alert-danger" role="alert">Please fill in all required fields.</div>');
        if (product_name === '') $('#product_name').addClass('alert-danger'); else $('#product_name').removeClass('alert-danger');
        if (product_type === '') $('#product_type').addClass('alert-danger'); else $('#product_type').removeClass('alert-danger');
        if (brand === '') $('#brand').addClass('alert-danger'); else $('#brand').removeClass('alert-danger');
        if (internal_reference === '') $('#internal_reference').addClass('alert-danger'); else $('#internal_reference').removeClass('alert-danger');
        if (product_image === '') $('#product_image').addClass('alert-danger'); else $('#product_image').removeClass('alert-danger');
        return;
    }

        if (file) {
            let reader = new FileReader();
            reader.onload = function(event) {
                let base64String = event.target.result.split(',')[1];

                $.ajax({
                    url: '/new_product/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                        product_image: base64String,
                        product_name: $('#product_name').val(),
                        product_type: $('#product_type').val(),
                        brand: $('#brand').val(),
                        internal_reference: $('#internal_reference').val(),
                        notes: $('#notes').val()
                    }),
                    success: function(response) {
                        if (response.success) {
                        $('#submitProductFormBtn').prop('disabled', true);
                            $('#message').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalFormProduct')[0].reset();

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
    $(document).on("click", ".edit-product", function(){
        var productId = $(this).data("product-id");
        $.ajax({
            url: '/get/product/values',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                'product_id': productId,
            }),
            success: function(response) {
                var modalBodyHtml = `
                    <form id="modalUpdateFormProduct">
                        <div class="form-group">
                            <label for="product_image">Product Image</label>
                            <div id="current-image">
                                <img src="${response.product_image_url}" class="img-fluid" id="product_image_update" alt="Product Image" style="width:100px">
                            </div>
                            <div id="image-preview" style="display:none;">
                                <img src="" id="preview-image" alt="Preview Image" style="width:100px">
                            </div>
                            <input type="file" id="new-image" accept="image/*">
                        </div>
                        <div class="form-group">
                            <label for="product_name">Product Name</label>
                            <input type="text" class="form-control" id="product_name_update" value="${response.product_name}">
                        </div>
<div class="form-group">
  <label for="product_type">Product Type</label>
  <select class="form-control" id="product_type_update">
    <option value="">Select an option</option>
    <option value="company_products" ${response.product_type === 'company_products' ? 'selected' : ''}>Company Products</option>
    <option value="company_materials" ${response.product_type === 'company_materials' ? 'selected' : ''}>Company Materials</option>
    <option value="competitor_products" ${response.product_type === 'competitor_products' ? 'selected' : ''}>Competitor Products</option>
    <option value="competitor_materials" ${response.product_type === 'competitor_materials' ? 'selected' : ''}>Competitor Materials</option>
  </select>
</div>                        <div class="form-group">
                            <label for="brand">Brand</label>
                            <input type="text" class="form-control" id="brand_update" value="${response.brand}">
                        </div>
                        <div class="form-group">
                            <label for="internal_reference">Internal Reference</label>
                            <input type="text" class="form-control" id="internal_reference_update" value="${response.internal_reference}">
                        </div>
                        <div class="form-group">
                            <label for="internal_reference">Description</label>
                            <input type="text" class="form-control" id="notes_update" value="${response.notes.replace(/<[^>]+>/g, '')}">
                            <input type="hidden" class="form-control" id="product_id_update" value="${response.product_id}">
                        </div>
                    </form>
                    <div id="message_update" class="mt-3"></div>
                `;

                // Set the HTML content of the modal body
                $("#productModal .modal-body").html(modalBodyHtml);

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

                $("#productModal").modal("show");
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error(error);
            }
        });
    });

    $("#updateProduct").on("click", function(){
        const fileInput = $('#new-image')[0];
        const file = fileInput.files[0];
        if (!file){
        const fileInput = $('#product_image_update');
        const file = fileInput.files;
        }

        if (file) {
            let reader = new FileReader();
            reader.onload = function(event) {
                let base64String = event.target.result.split(',')[1];

                $.ajax({
                    url: '/new_product/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                        product_image: base64String,
                        product_name: $('#product_name_update').val(),
                        product_type: $('#product_type_update').val(),
                        brand: $('#brand_update').val(),
                        internal_reference: $('#internal_reference_update').val(),
                        notes: $('#notes_update').val(),
                        product_id: $('#product_id_update').val(),
                    }),
                    success: function(response) {
                        if (response.success) {
                            $('#message_update').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalUpdateFormProduct')[0].reset();

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
                    url: '/new_product/submit_form',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({
                        product_name: $('#product_name_update').val(),
                        product_type: $('#product_type_update').val(),
                        brand: $('#brand_update').val(),
                        internal_reference: $('#internal_reference_update').val(),
                        notes: $('#notes_update').val(),
                        product_id: $('#product_id_update').val(),
                    }),
                    success: function(response) {
                        if (response.success) {
                            $('#message_update').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                            $('#modalUpdateFormProduct')[0].reset();

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
});