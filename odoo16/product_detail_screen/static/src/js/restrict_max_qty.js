odoo.define('restrict_max_qty', function(require) {
    'use strict';

    $(document).on('change', 'input[name="add_qty"]', function(ev) {
        var $input = $(this);
        var $maxQtyInput = $(this).closest('form').find('input.p_free_qty');
        var max_qty = parseInt($maxQtyInput.val(), 10);
        var qty = parseInt($input.val(), 10);
        if (qty > max_qty) {
            $input.val(max_qty);
        }
        else if(max_qty == 'NaN') {
        $input.val(1);
        }
    });
        $(document).on('change', 'input.js_quantity', function(ev) {

        var $input = $(this);
        var $maxQtyInput = $(document).find('input[name="cart_free_qty"]').eq($input.index('.js_quantity'));;
        var max_qty = parseInt($maxQtyInput.val(), 10);
        var qty = parseInt($input.val(), 10);
        if (qty > max_qty) {
            $input.val(max_qty);
        }
        else if(max_qty == 'NaN') {
        $input.val(1);
        }
    });

});