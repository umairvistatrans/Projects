/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from 'sale.VariantMixin';
import wSaleUtils from "website_sale.utils";

const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
const ajax = require('web.ajax');
import {WebsiteSale} from 'website_sale.website_sale';

export const WebsitePreorder = publicWidget.Widget.extend(VariantMixin, cartHandlerMixin, {

    selector: '.oe_website_sale',
    events: Object.assign({}, VariantMixin.events || {}, {
        'click #preorder_to_cart, .add_cart_preorder': '_onClickPreorder',
        'change form .js_product input[name="add_qty"]': 'onChangeAddQuantity',
        'click input[name="add_qty"]': 'onClickAddQuantity',
        'change .oe_cart input.js_quantity[data-product-id]': '_onChangeCartQuantity',
        'click .oe_cart input.js_quantity[data-product-id]': '_onClickCartQuantity',
        'click #add_to_cart_custom': '_onClickAddTocart',
    }),

    init: function () {
        this._super.apply(this, arguments);
    },

    start: async function () {
        this._super.apply(this, arguments);
        const product_id = $('input[name="product_template_id"]').val() || false;
        debugger
        await ajax.jsonRpc('/product/qty/check', 'call', {
            'product_id': product_id,
        }).then(function (data) {
            debugger
            if (data[1] == 'preorder') {
                $('#add_to_cart_custom').addClass('d-none');
                $('#preorder_to_cart').removeClass('d-none');
                $('#preorder-tab').removeClass('d-none');
                $('.pre_order_policy').removeClass('d-none');
                $('.form-control.quantity').val(data[0]).trigger("change");

            } else if (data[1] == 'in_stock') {
                $('#add_to_cart_custom').removeClass('d-none');
                $('#preorder_to_cart').addClass('d-none');
                $('.pre_order_policy').addClass('d-none');
                $('.form-control.quantity').val(data[0]).trigger("change");
            }
            else if (data[1] != 'preorder' && data[1] != 'in_stock'){
                $('.wsale_cart').removeClass('d-none');
            }
        });
    },

    _onClickPreorder: function (ev) {
        debugger
        let $parent;
        if ($(ev.currentTarget).closest('.oe_optional_products_modal').length > 0) {
            $parent = $(ev.currentTarget).closest('.oe_optional_products_modal');
        } else if ($(ev.currentTarget).closest('form').length > 0) {
            $parent = $(ev.currentTarget).closest('form');
        } else {
            $parent = $(ev.currentTarget).closest('.o_product_configurator');
        }

        const qty = $parent.find('.form-control').val();
        const $button = document.getElementById("add_to_cart");

        ajax.jsonRpc('/preorder/check', 'call', {
            'qty': qty,
            'product_id': this._getProductId($parent),
        }).then(function (data) {
            if (data == true) {
                $button.click();
            } else {
                $('.add_cart_preorder').popover({
                    content: data,
                    title: 'Warning',
                    placement: 'top',
                });
                $('.add_cart_preorder').popover('show');
            }
        });
    },

    _onChangeCartQuantity: function (ev) {
        const $input = $(ev.currentTarget);
        if ($input.data('update_change')) {
            return;
        }

        let value = parseInt($input.val() || 0, 10);
        if (isNaN(value)) {
            value = 1;
        }
        const productIDs = [parseInt($input.data('product-id'), 10)];

        ajax.jsonRpc('/preorder/qty', 'call', {
            'product_id': productIDs[0],
        }).then(function (data) {
            if (data != 0) {
                if (data[0] > value) {
                    $input.val(data[0]).trigger("change");
                }
                if (value > data[1]) {
                    $('.js_quantity.form-control.quantity').popover({
                        content: "You are trying to add more than available quantity for this product",
                        title: 'Warning',
                        placement: 'top',
                    });
                    $('.js_quantity.form-control.quantity').popover('show');
                    $input.val(data[1]).trigger("change");
                    setInterval(function () {
                        $('.js_quantity.form-control.quantity').popover('hide');
                    }, 500);
                }
            }
        });
    },

    onClickAddQuantity: function (ev) {
        ev.preventDefault();
        $('.form-control.quantity').popover('hide');
    },

    _onClickCartQuantity: function (ev) {
        ev.preventDefault();
        $('.js_quantity.form-control.quantity').popover('hide');
    },

    onChangeAddQuantity: function (ev) {
        let $parent;
        if ($(ev.currentTarget).closest('.oe_optional_products_modal').length > 0) {
            $parent = $(ev.currentTarget).closest('.oe_optional_products_modal');
        } else if ($(ev.currentTarget).closest('form').length > 0) {
            $parent = $(ev.currentTarget).closest('form');
        } else {
            $parent = $(ev.currentTarget).closest('.o_product_configurator');
        }

        this.triggerVariantChange($parent);

        const $link = $(ev.currentTarget);
        const $input = $link.closest('.input-group').find("input");
        const input_quant = $parent.find('.form-control').val();
        const value = parseInt(input_quant);

        $('.form-control.quantity').popover({
            content: "You are trying to add more than available quantity for this product",
            title: 'Warning',
            placement: 'top',
        });

        ajax.jsonRpc('/preorder/qty', 'call', {
            'product_id': this._getProductId($parent),
        }).then(function (data) {
            if (data != 0) {
                if (data[0] > value) {
                    $input.val(data[0]).trigger("change");
                } else if (data[1] < value) {
                    $('.form-control.quantity').popover({
                        content: "You are trying to add more than available quantity for this product",
                        title: 'Warning',
                        placement: 'top',
                    });
                    $('.form-control.quantity').popover('show');
                    $input.val(data[1]).trigger("change");
                    setInterval(function () {
                        $('.form-control.quantity').popover('hide');
                    }, 5000);
                }
            }
        });
    },

    _onClickAddTocart: function (ev) {
        ev.preventDefault();
        let $parent;
        if ($(ev.currentTarget).closest('.oe_optional_products_modal').length > 0) {
            $parent = $(ev.currentTarget).closest('.oe_optional_products_modal');
        } else if ($(ev.currentTarget).closest('form').length > 0) {
            $parent = $(ev.currentTarget).closest('form');
        } else {
            $parent = $(ev.currentTarget).closest('.o_product_configurator');
        }

        const $button = document.getElementById("add_to_cart");

        ajax.jsonRpc('/order/check', 'call', {"product_id": this._getProductId($parent)}).then(function (data) {
            if (data == 0) {
                $button.click();
            } else {
                $('.add_to_cart_custom').popover({
                    content: data,
                    title: 'Warning',
                    placement: 'top',
                });
                $('.add_to_cart_custom').popover('show');
            }
        });
    },
});

publicWidget.registry.websiteSaleCart.include({

    init: function () {
        this._super.apply(this, arguments);
        // this.orm = this.bindService("orm");
    },

_onClickDeleteProduct: function (ev) {
    ev.preventDefault();
    const $target = $(ev.currentTarget);
    const line_id = $target.closest('tr').find('.js_quantity').data('line-id');

    if (line_id) {
        this._rpc({
            model: 'sale.order.line',
            method: 'unlink',
            args: [[line_id]],
        }).then(() => {
            const $cartProductsTable = $('#cart_products');
            const $row = $target.closest('tr');

            $row.remove();

            if ($cartProductsTable.find('tbody tr').length === 0) {
                $('.oe_cart').siblings('#o_cart_summary').removeClass('d-xl-block');
                $('.oe_cart').html('<div class="alert alert-info">' + _t('Your cart is empty!') + '</div>');
            }
        }).catch(err => {
            console.error("Failed to unlink sale order line:", err);
        });
    } else {
        console.error("Line ID is not found");
    }
},
});

publicWidget.registry.WebsitePreorder = WebsitePreorder;
