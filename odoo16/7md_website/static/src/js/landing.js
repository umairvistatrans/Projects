odoo.define(
    '7md_website.landing', function (require) {
        'use strict';
        let myCarousel = document.querySelectorAll('#featureContainer .carousel .carousel-item');
        myCarousel.forEach((el) => {
            const minPerSlide = 4
            let next = el.nextElementSibling
            for (var i = 1; i < minPerSlide; i++) {
                if (!next) {
                    // wrap carousel by using first child
                    next = myCarousel[0]
                }
                let cloneChild = next.cloneNode(true)
                el.appendChild(cloneChild.children[0])
                next = next.nextElementSibling
            }
        })

        let bestSellerCarousel = document.querySelectorAll('#bestSellerCarousel .carousel .carousel-item');
        bestSellerCarousel.forEach((el) => {
            const minPerSlide = 4
            let next = el.nextElementSibling
            for (var i = 1; i < minPerSlide; i++) {
                if (!next) {
                    // wrap carousel by using first child
                    next = bestSellerCarousel[0]
                }
                let cloneChild = next.cloneNode(true)
                el.appendChild(cloneChild.children[0])
                next = next.nextElementSibling
            }
        })

        // Category Slider
        $(document).ready(function (categorySlider) {

            var slideCount = $('#category-types-slider ul li').length;
            var slideWidth = $('#category-types-slider ul li').width();
            var slideHeight = $('#category-types-slider ul li').height();
            var sliderUlWidth = slideCount * slideWidth;

            $('#category-types-slider').css({ width: slideWidth, height: slideHeight });

            $('#category-types-slider ul').css({ width: sliderUlWidth, marginLeft: - slideWidth });

            $('#category-types-slider ul li:last-child').prependTo('#category-types-slider ul');


            function moveLeft() {
                $('#category-types-slider ul').animate({
                    left: + slideWidth
                }, 200, function () {
                    $('#category-types-slider ul li:last-child').prependTo('#category-types-slider ul');
                    $('#category-types-slider ul').css('left', '');
                });
            };

            function moveRight() {
                $('#category-types-slider ul').animate({
                    left: - slideWidth
                }, 200, function () {
                    $('#category-types-slider ul li:first-child').appendTo('#category-types-slider ul');
                    $('#category-types-slider ul').css('left', '');
                });
            };


            $('.category-arrow-prev').click(function () {
                moveLeft();
            });

            $('.category-arrow-next').click(function () {
                moveRight();
            });


            setTimeout(moveLeft(), 1000); /* works only on load for the first slider...research later*/
        });

        // Light slider js
        $(document).ready(function () {
            // Multi product slider
            $('#lightslider-multi-product').lightSlider({
                item: 5,
                loop: true,
                controls: false,
                slideMove: 1,
                easing: 'cubic-bezier(0.25, 0, 0.25, 1)',
                speed: 300,
                responsive: [
                    {
                        breakpoint: 800,
                        settings: {
                            item: 3,
                            slideMove: 1,
                            slideMargin: 6,
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            item: 2,
                            slideMove: 1
                        }
                    }
                ]
            });
            // New Offer Slider
            $('#lightslider-new-offer').lightSlider({
                item: 4,
                loop: true,
                controls: false,
                pager: false,
                slideMove: 1,
                easing: 'cubic-bezier(0.25, 0, 0.25, 1)',
                speed: 300,
                responsive: [
                    {
                        breakpoint: 800,
                        settings: {
                            item: 3,
                            slideMove: 1,
                            slideMargin: 6,
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            item: 2,
                            slideMove: 1
                        }
                    }
                ]
            });
            // Best Selling Slider
            $('#lightslider-best-selling').lightSlider({
                item: 4,
                loop: true,
                controls: false,
                pager: false,
                slideMove: 1,
                easing: 'cubic-bezier(0.25, 0, 0.25, 1)',
                speed: 300,
                responsive: [
                    {
                        breakpoint: 800,
                        settings: {
                            item: 3,
                            slideMove: 1,
                            slideMargin: 6,
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            item: 2,
                            slideMove: 1
                        }
                    }
                ]
            });
        });


        $(document).ready(function () {
            // Listen for click on any button within the nav-link class
            $('body').on('click', '.nav-link', function (e) {
                // Prevent default action if necessary
                // e.preventDefault();
                $('.nav-link').removeClass('active');
                $(this).addClass('active');
                var targetId = $(this).data('bs-target');
                $('.tab-content').children().removeClass('show active');
                // Show only the targeted content
                $(targetId).addClass('show active');
            });
        });
$(document).ready(function() {
    // Function to detect changes in the span elements
    function observeValueChanges() {
        // Select the spans using the class o_wsale_delivery_badge_price
        const sourceSpans = document.querySelectorAll('.o_wsale_delivery_badge_price .oe_currency_value');
        const targetSpan = document.querySelector('[data-oe-field="amount_delivery"] .oe_currency_value');

        // Ensure there are source spans and a target span
        if (sourceSpans.length === 0 || !targetSpan) {
            return;
        }

        // Function to update the target span value
        function updateTargetValue() {
            let totalValue = 0;
            sourceSpans.forEach(span => {
                const value = parseFloat(span.textContent.trim());
                if (!isNaN(value)) { // Ensure the value is a valid number
                    totalValue += value;
                }
            });

            // Update the target span with the new value (example: sum of all values)
            const targetValue = totalValue.toFixed(2); // Sum of all values
            targetSpan.textContent = targetValue;
        }

        // Create a new MutationObserver instance
        const observer = new MutationObserver(updateTargetValue);

        // Configuration of the observer
        const config = { characterData: true, subtree: true };

        // Start observing the source span elements
        sourceSpans.forEach(span => {
            observer.observe(span, config);
        });

        // Initial update
        updateTargetValue();
    }

    // Run the function on page load with a slight delay to ensure DOM is fully loaded
    setTimeout(observeValueChanges, 1000);
});







        $('.create-account-btn').click(function () {
            localStorage.removeItem('odooUsername');
            localStorage.removeItem('odooPassword');
        });

        const passwordField = document.getElementById("password");
        const togglePassword = document.querySelector(".password-toggle-icon i");

        togglePassword.addEventListener("click", function () {
            if (passwordField.type === "password") {
                passwordField.type = "text";
                togglePassword.classList.remove("fa-eye-slash");
                togglePassword.classList.add("fa-eye");
            } else {
                passwordField.type = "password";
                togglePassword.classList.remove("fa-eye");
                togglePassword.classList.add("fa-eye-slash");
            }
        });



    });
