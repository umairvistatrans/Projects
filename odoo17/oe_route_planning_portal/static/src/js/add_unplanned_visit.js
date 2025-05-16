$(document).ready(function() {
    // Open modal on button click
    $('#openModalButton').on('click', function() {
        $('#exampleModalCenter').modal('show');
    });
    $('#closeModalButton').on('click', function() {
        location.reload();
        $('#exampleModalCenter').modal('hide');
    });

$('#partner_id').change(function() {
            var partnerId = $(this).val();
            if (partnerId) {
                $.ajax({
                    url: '/get_routes_by_partner/' + partnerId,
                    type: 'POST',
                    success: function(response) {
                    const data = JSON.parse(response);
                        var routeSelect = $('#route_id');
                        routeSelect.empty();  // Clear existing options
                        if (data.routes) {
                            $.each(data.routes, function(index, route) {
                                routeSelect.append(new Option(route.name, route.id));
                            });

                            if (data.default_route_id) {
                                routeSelect.val(data.default_route_id);  // Set default route
                            }
                        }
                    },
                    error: function(data) {
                        alert(data);
                    }
                });
            }
        });

    // Function to get the current date in YYYY-MM-DD format
    function getCurrentDate() {
        const today = new Date();
        const year = today.getFullYear();
        let month = today.getMonth() + 1;
        let day = today.getDate();

        // Add leading zero if month/day is a single digit
        month = month < 10 ? '0' + month : month;
        day = day < 10 ? '0' + day : day;

        return `${year}-${month}-${day}`;
    }

    // Set the current date in the input field on page load
    const currentDate = getCurrentDate();
    $('#current_date').val(currentDate);

    // Handle form submission
    $('#submitFormBtn').on('click', function() {
    const partnerId = $('#partner_id').val();
    const routeId = $('#route_id').val();
    const currentDate = $('#current_date').val();

    if (routeId === '' || partnerId === '' || currentDate === '') {
//        alert('Please fill in all required fields.');
        $('#message').html('<div class="alert alert-danger" role="alert">Please fill in all required fields.</div>');
        if (routeId === '') $('#route_id').addClass('alert-danger');
        if (partnerId === '') $('#partner_id').addClass('alert-danger');
        if (currentDate === '') $('#current_date').addClass('alert-danger');
        return;
    }

    $.ajax({
        url: '/unplanned_visit/submit_form',
        type: 'POST',
        data: {
            partner_id: partnerId,
            current_date: currentDate,
            route_id: routeId
        },
        success: function(response) {
            // Parse JSON response
            const result = JSON.parse(response);
            if (result.success) {
            $('#submitFormBtn').prop('disabled', true);
                $('#message').html('<div class="alert alert-success" role="alert">' + result.message + '</div>');
//                $('#modalForm')[0].reset(); // Reset form

                // Refresh the page after 3 seconds (3000 milliseconds)
                setTimeout(function() {
                    location.reload();
                }, 3000);
            } else {
                $('#message').html('<div class="alert alert-danger" role="alert">' + result.message + '</div>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            $('#message').html('<div class="alert alert-danger" role="alert">Error: ' + error + '</div>');
        }
    });
});




});
