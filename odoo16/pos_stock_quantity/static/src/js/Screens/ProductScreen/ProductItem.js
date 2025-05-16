/** @odoo-module **/

import ProductItem from "point_of_sale.ProductItem";
import Registries from "point_of_sale.Registries";
import {format} from "web.field_utils";
import utils from "web.utils";

const POSStockProductItem = (ProductItem) =>
    class POSStockProductItem extends ProductItem {
        format_quantity(quantity) {
            const unit = this.env.pos.units_by_id[this.props.product.uom_id[0]];
            var formattedQuantity = `${quantity}`;
            if (unit) {
                if (unit.rounding) {
                    var decimals = this.env.pos.dp["Product Unit of Measure"];
                    formattedQuantity = format.float(quantity, {
                        digits: [69, decimals],
                    });
                } else {
                    formattedQuantity = utils.round_precision(quantity, 1).toFixed(0);
                }
            }
            return `${formattedQuantity}`;
        }
        get get_stock_qty() {
            if (this.props.product.default_code == "9698"){
            debugger;
            console.log("hello")
            }
//            return this.format_quantity(this.props.product.qty_available);
            return this.format_quantity(this.props.product.free_qty);
        }
    };

Registries.Component.extend(ProductItem, POSStockProductItem);
