/** @odoo-module **/

import { Orderline, PosGlobalState} from 'point_of_sale.models';
import Registries from "point_of_sale.Registries";
import { Gui } from 'point_of_sale.Gui';
import core from 'web.core';

const _t = core._t;

const ProductOrderline = (Orderline) => class ProductOrderline extends Orderline {


        get_product_default_code () {
                    var default_code = this.product.default_code;
                    return default_code;
                }

        generateWrappedProductName() {
            const MAX_LENGTH = 24; // Adjust the maximum length as needed
            const wrapped = [];
            let name = this.product.pos_display_name;
            let currentLine = "";

            while (name.length > 0) {
                let spaceIndex = name.indexOf(" ");

                if (spaceIndex === -1) {
                    spaceIndex = name.length;
                }

                if (currentLine.length + spaceIndex > MAX_LENGTH) {
                    if (currentLine.length) {
                        wrapped.push(currentLine);
                    }
                    currentLine = "";
                }

                currentLine += name.slice(0, spaceIndex + 1);
                name = name.slice(spaceIndex + 1);
            }

            if (currentLine.length) {
                wrapped.push(currentLine);
            }

            console.log('/////', wrapped);
            return wrapped;
        }

}

Registries.Model.extend(Orderline, ProductOrderline);
//
//
//
//odoo.define('pos_custom.models', function (require) {
//    "use strict";
//
//    const models = require('point_of_sale.models');
//
//    models.loadFields('product.product', ['pos_display_name']);
//
//    models.Orderline = models.Orderline.extend({
//        generateWrappedProductName: function () {
//            const MAX_LENGTH = 24; // Adjust the maximum length as needed
//            const wrapped = [];
//            let name = this.product.pos_display_name;
//            let currentLine = "";
//
//            while (name.length > 0) {
//                let spaceIndex = name.indexOf(" ");
//
//                if (spaceIndex === -1) {
//                    spaceIndex = name.length;
//                }
//
//                if (currentLine.length + spaceIndex > MAX_LENGTH) {
//                    if (currentLine.length) {
//                        wrapped.push(currentLine);
//                    }
//                    currentLine = "";
//                }
//
//                currentLine += name.slice(0, spaceIndex + 1);
//                name = name.slice(spaceIndex + 1);
//            }
//
//            if (currentLine.length) {
//                wrapped.push(currentLine);
//            }
//
//            console.log('/////', wrapped);
//            return wrapped;
//        },
//    });
//});
