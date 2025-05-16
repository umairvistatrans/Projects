/** @odoo-module **/

import { PosGlobalState } from 'point_of_sale.models';
import Registries from "point_of_sale.Registries";
const { useService } = require("@web/core/utils/hooks");
import { Gui } from 'point_of_sale.Gui';
import core from 'web.core';

const _t = core._t;

const PosStockAvailabilityLocationGlobalState = (PosGlobalState) => class PosStockAvailabilityLocationGlobalState extends PosGlobalState {
    async get_product_availability_by_location(code) {
        const info = await this.env.services.rpc({
            model: 'product.product',
            method: 'oe_get_product_availability_by_location',
            args: [[], code]
        }, {
            timeout: 3000,
            shadow: true,
        });
        if (info.hasOwnProperty('error')) {
            Gui.showPopup('ErrorPopup', {
                title: _t('Not Found'),
                body: _t(info['error']['message'])
            });
            return;
        }
        if (info && info.length){
            Gui.showPopup('ProductAvailabilityPopupWidget', {
                info: info || [],
                title: _t('Product Availability By Location'),
            });
        }
    }
}
Registries.Model.extend(PosGlobalState, PosStockAvailabilityLocationGlobalState);
