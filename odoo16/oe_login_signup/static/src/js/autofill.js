odoo.define('oe_login_signup.autofill', function (require) {
    "use strict";

    $(document).ready(function () {
        // Example function to save credentials
        function saveCredentials(username, password) {
            if ($('#remember_me').is(':checked')) { // Check if "Remember Me" is checked
                localStorage.setItem('odooUsername', username);
                localStorage.setItem('odooPassword', password);
                localStorage.setItem('rememberMe', 'true');
            }
        }

        // Example function to load credentials
        function loadCredentials() {
            const rememberMe = localStorage.getItem('rememberMe');
            if (rememberMe === 'true') {
                const username = localStorage.getItem('odooUsername');
                const password = localStorage.getItem('odooPassword');
                if (username && password) {
                    $('#login').val(username);
                    $('#password').val(password);
                    $('#remember_me').prop('checked', true); // Automatically check the "Remember Me" box
                }
            }
        }

        // You would call loadCredentials somewhere here to fill the form when the page loads
        loadCredentials();

        // Assuming you have a form with an ID of 'login_form'
        $('.oe_login_form').on('submit', function(e) {
            var username = $('#login').val();
            var password = $('#password').val();
            if ($('#remember_me').is(':checked')){
            saveCredentials(username, password);
            }
        });
    });
});

