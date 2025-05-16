$(document).ready(function() {
    $('#search_brand').on('input', function() {
        var searchValue = $(this).val();

        // Check if the search value length is 3 or more, or if the input is empty
        if(searchValue.length >= 3 || searchValue.length === 0) {
            $.ajax({
                url: "/brand_search",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {search_brand: searchValue},
                }),
                success: function(response) {
                    var brands = response.result;
                    var $resultsContainer = $(".search_result_div").first(); // Targeting the results container
                    $resultsContainer.empty(); // Clear current results

                    // Iterate through the brands and append each to the results container
                    $.each(brands, function(index, brand) {
                        var brandLogo = "data:image/jpeg;base64," + brand.logo || "data:image/png;base64," + brand.logo; // Fallback logo
                        if (brand.logo == false){
                        var brandLogo = "/oe_login_signup/static/description/assets/brand-svgrepo-com.svg"
                        }
                        var brandElement = `
                            <div data-brand_name="${brand.name}" class="col-lg-2 col-md-3 brand_box">
                                <a href="/shop/brand/${brand.id}" class="brand-image">
                                    <img src="${brandLogo}" alt="brand image"/>
                                </a>
                            </div>
                        `;
                        $resultsContainer.append(brandElement);
                    });
                }
            });
        }
    });
});
