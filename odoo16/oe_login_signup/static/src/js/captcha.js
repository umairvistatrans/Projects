odoo.define('oe_login_signup.captcha', function(require) {
                'use strict';

                var core = require('web.core');
                var sAnimation = require('website.content.snippets.animation');

                sAnimation.registry.formSubmitAnimation = sAnimation.Class.extend({
                    selector: 'form',
                    start: function () {
                        this._super.apply(this, arguments);
                        var $form = $(this.selector);
                        $form.on('submit', function(event) {
                            var recaptcha = $("#g-recaptcha-response").val();
                            if (recaptcha === "") {
                                event.preventDefault();
                                document.getElementById('err').innerHTML = "Please verify Captcha";
                            }
                        });
                    },
                });

                window.verifyRecaptchaCallback = function(response) {
                    $('#recaptcha_verified').val(response); // Set some value to indicate verification
                };

                window.expiredRecaptchaCallback = function() {
                    $('#recaptcha_verified').val(''); // Reset on expiration
                };
            });