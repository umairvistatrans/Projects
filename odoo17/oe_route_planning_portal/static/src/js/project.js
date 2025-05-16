/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";

publicWidget.registry.ProjectPortalSidebar = PortalSidebar.extend({
    selector: '.o_project_portal_sidebar',
    events: {
        'click .tablinks': '_onClicktab',
        'click .save_button': '_onSave',
        'change input[type="radio"]': '_onRadioChange',
        'click .request-reschedule-btn': '_onRequestReSchedule',
        'click .request-cancel-btn': '_onRequestCancel',
        'click .current_position': '_getCurrentPosition',
        'change .image_upload': '_onImageUploadChange',
        'change .multiple_image_upload': '_onMultipleImageUploadChange',
        'click .checkin-btn': '_getCurrentPosition',
    },

    _onClicktab: function (ev) {
        var typeName = ev.currentTarget.innerHTML;
        var tabcontent = document.getElementsByClassName("tabcontent");
        for (var i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        var tablinks = document.getElementsByClassName("tablinks");
        debugger;
        for (var i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(typeName).style.display = "block";
        ev.currentTarget.className += " active";
    },

     _onImageUploadChange: function(ev) {
            var input = ev.currentTarget;
            var file = input.files[0];
            var reader = new FileReader();

            reader.onload = function(e) {
                // Create an image element
                var img = document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100px';  // Set desired width
                img.style.height = '100px'; // Set desired height

                // Remove any existing image preview
                var existingPreview = input.nextElementSibling;
                if (existingPreview && existingPreview.tagName.toLowerCase() === 'img') {
                    existingPreview.remove();
                }

                // Insert the image after the file input
                input.parentNode.insertBefore(img, input.nextSibling);

                // Store the base64 encoded image data in the input's dataset
                input.dataset.base64 = e.target.result;
            };

            if (file) {
                reader.readAsDataURL(file);
            }
     },

     _onMultipleImageUploadChange: function(ev) {
         var input = ev.currentTarget;
         var files = input.files; // For multiple files
         var previewContainer = input.nextElementSibling; // Container for image previews

         // Clear existing previews
         while (previewContainer.firstChild) {
             previewContainer.removeChild(previewContainer.firstChild);
         }

         for (var i = 0; i < files.length; i++) {
             var reader = new FileReader();

             reader.onload = (function(file) {
                 return function(e) {
                     // Create an image element
                     var img = document.createElement('img');
                     img.src = e.target.result;
                     img.style.width = '100px';  // Set desired width
                     img.style.height = '100px'; // Set desired height
                     img.style.margin = '5px';

                     // Append the image to the preview container
                     previewContainer.appendChild(img);
                 };
             })(files[i]);

             reader.readAsDataURL(files[i]);
         }
     },

    _onSave: function (ev) {
        var visit_id = $(ev.currentTarget).data('visit-id');
        var quantities = {};
        var availability = {};
        var companyMaterialComments = {};
        var competitorProductsComments = {};
        var competitorMaterialsComments = {};
        var companyMaterialImages = {};
        var competitorProductsImages = {};
        var competitorMaterialsImages = {};
        var multipleImagesData = [];
        var feedback = $('.feedback-div textarea').val();

        // Iterate over all input fields with class .qty_input
        $('.qty_input').each(function() {
            var product_id = $(this).data('product-id');
            var quantity = $(this).val();
            if (product_id !== undefined) {
                quantities[product_id] = quantity;
                debugger;
            }

            // Get selected availability for each product
            var availability_value = $('input[name="type_availability_' + product_id + '"]:checked').val();
            availability[product_id] = availability_value;
        });

        // Collect comments for Company Material
        $('.comment-boxx-comp-material textarea').each(function() {
            
            var product_id = $(this).closest('.card').data('product-id');
            var comment = $(this).val();
            companyMaterialComments[product_id] = comment;
        });

        // Collect comments for Competitor Products
        $('.comment-boxx-competitor-pro textarea').each(function() {
            var product_id = $(this).closest('.card').data('product-id');
            var comment = $(this).val();
            competitorProductsComments[product_id] = comment;
        });

        // Collect comments for Competitor Materials
        $('.comment-boxx-competitor-mat textarea').each(function() {
            var product_id = $(this).closest('.card').data('product-id');
            var comment = $(this).val();
            competitorMaterialsComments[product_id] = comment;
        });

        // Function to handle file reading and return a promise
        function readFileAsync(file, product_id, targetDict) {
            return new Promise((resolve, reject) => {
                var reader = new FileReader();
                reader.onload = function(e) {
                    targetDict[product_id] = e.target.result;
                    resolve();
                };
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
        }

        // Collect images and create promises
        var filePromises = [];

        // Collect images for Company Material
        $('.upload-boxx-comp-material input[type="file"]').each(function() {
            var product_id = $(this).closest('.card').data('product-id');
            var file = this.files[0];
            if (file) {
                filePromises.push(readFileAsync(file, product_id, companyMaterialImages));
            }
        });

        // Collect images for Competitor Products
        $('.upload-boxx-competitor-pro input[type="file"]').each(function() {
            var product_id = $(this).closest('.card').data('product-id');
            var file = this.files[0];
            if (file) {
                filePromises.push(readFileAsync(file, product_id, competitorProductsImages));
            }
        });

        // Collect images for Competitor Materials
        $('.upload-boxx-competitor-mat input[type="file"]').each(function() {
            var product_id = $(this).closest('.card').data('product-id');
            var file = this.files[0];
            if (file) {
                filePromises.push(readFileAsync(file, product_id, competitorMaterialsImages));
            }
        });

        var multipleImagesPromises = [];

        $('.multi-upload').each(function() {
            var imageFiles = $(this).find('.multiple_image_upload')[0].files;
            for (var i = 0; i < imageFiles.length; i++) {
                var file = imageFiles[i];
                multipleImagesPromises.push(readFileAsync(file, i, multipleImagesData));
            }
        });

        // Wait for all file reading promises to resolve

        Promise.all(filePromises.concat(multipleImagesPromises)).then(function() {
//        alert(JSON.stringify(multipleImagesData));
//        console.error("File reading failed:", JSON.stringify(multipleImagesData));
            // Now all files are read and we can send the AJAX request
            $.ajax({
                type: "POST",
                url: "/save_quantity",
                data: {
                    visit_id: visit_id,
                    quantities: JSON.stringify(quantities),
                    availability: JSON.stringify(availability),
                    company_material_comments: JSON.stringify(companyMaterialComments),
                    competitor_products_comments: JSON.stringify(competitorProductsComments),
                    competitor_materials_comments: JSON.stringify(competitorMaterialsComments),
                    company_material_images: JSON.stringify(companyMaterialImages),
                    competitor_products_images: JSON.stringify(competitorProductsImages),
                    competitor_materials_images: JSON.stringify(competitorMaterialsImages),
                    multiple_images_data: JSON.stringify(multipleImagesData),
                    feedback: feedback
                },
                success: function(response) {
                    console.log(response);
                }
            });
        }).catch(function(error) {
            console.error("File reading failed:", error);
        });
    },

    _getCurrentPosition: function (ev) {
        var visit_id = $(ev.currentTarget).data('visit-id');
        var action = $(ev.currentTarget).data('action');
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;

                $.ajax({
                    type: "GET",
                    url: "/update_latitude",
                    data: {
                        latitude: latitude,
                        longitude: longitude,
                        visit_id: visit_id,
                        action: action
                    },
                    success: function(response) {
                    if (response.success) {
                        debugger;
                        alert(response.message);
                        if (action === "checkin") {
                            window.location.reload();
                        } else if (action === "checkout") {
                            window.location.href = "/my/visits";
                        }
                    } else {
                        alert(response.message);
                    }
                }
                });

            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    },

    _onRequestReSchedule: function(ev) {
        var visitId = $(ev.currentTarget).data('visit-id');
        
        var confirmation = confirm("Are you sure you want to reschedule this visit?");
        if (confirmation) {
            $.ajax({
                type: "POST",
                url: "/update_status",
                data: {
                    visit_id: visitId,
                    status: 'reschedule',
                },
                success: function(response) {
                    console.log(response); // Show success or error message
                    window.location.href = "/my/visits";
                }
            });
        }
    },

    _onRequestCancel: function(ev) {
        var visitId = $(ev.currentTarget).data('visit-id');
        
        var confirmation = confirm("Are you sure you want to cancel this visit?");
        if (confirmation) {
            $.ajax({
                type: "POST",
                url: "/update_status",
                data: {
                    visit_id: visitId,
                    status: 'cancel',
                },
                success: function(response) {
                    console.log(response);
                     window.location.href = "/my/visits"; // Show success or error message
                }
            });
        }
    },

    _onRadioChange: function(ev) {
        var productId = ev.currentTarget.name.split('_').pop();

        // To get the id of the quantity input field
        var productdataId = $(ev.currentTarget).attr('data-product-id');
        
        console.log("product data Id:", productdataId);

        // To select the input field based on data-product-id
        var inputField = $('input[type="number"][data-product-id="' + productdataId + '"]');
        if (inputField.length) {
            if (ev.currentTarget.value === 'not_availability' || ev.currentTarget.value === 'out_of_stock' ) {
                inputField.hide();
            } else {
                inputField.show();
            }
        }
    }
});
