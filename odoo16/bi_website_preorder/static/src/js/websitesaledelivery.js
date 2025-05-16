
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale_delivery";
import { renderToElement } from "@web/core/utils/render";

const WebsiteSaleDeliveryWidget = publicWidget.registry.websiteSaleDelivery;

// temporary for OnNoResultReturned bug
import {registry} from "@web/core/registry";
import {UncaughtCorsError} from "@web/core/errors/error_service";
const errorHandlerRegistry = registry.category("error_handlers");

WebsiteSaleDeliveryWidget.include({

    /**
    * Loads Mondial Relay the first time, else show it.
    *
    * @override
    */
    _handleCarrierUpdateResult: async function (carrierInput) {
        const result = await this.rpc('/shop/update_carrier', {
        'carrier_id': carrierInput.value,
        })
        this.result = result;
        this._handleCarrierUpdateResultBadge(result);
        if (carrierInput.checked) {
            var amountDelivery = document.querySelector('#order_delivery .monetary_field');
            var amountUntaxed = document.querySelector('#order_total_untaxed .monetary_field');
            var amountTax = document.querySelector('#order_total_taxes .monetary_field');
            var amountTotal = document.querySelectorAll('#order_total .monetary_field, #amount_total_summary.monetary_field');
        if (!amountDelivery == null){
            amountDelivery.innerHTML = result.new_amount_delivery;
        }
        amountUntaxed.innerHTML = result.new_amount_untaxed;
        amountTax.innerHTML = result.new_amount_tax;
        amountTotal.forEach(total => total.innerHTML = result.new_amount_total);
        if (result.new_amount_total_raw !== undefined) {
            this._updateShippingCost(result.new_amount_total_raw);
        }
        this._updateShippingCost(result.new_amount_delivery);
        }
        this._enableButton(result.status);
        let currentId = result.carrier_id
        const showLocations = document.querySelectorAll(".o_show_pickup_locations");

        for (const showLoc of showLocations) {
            const currentCarrierId = showLoc.closest("li").getElementsByTagName("input")[0].value;
            if (currentCarrierId == currentId) {
            this._specificDropperDisplay(showLoc);
            break;
            }
        }

    },
});