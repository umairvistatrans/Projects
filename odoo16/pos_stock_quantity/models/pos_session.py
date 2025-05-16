from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _process_pos_ui_product_product(self, products):
        config = self.config_id
        if config.show_qty_available or config.show_qty_available_res:
            product_obj = self.env["product.product"]
            for product_info in products:
                if config.location_only:
                    product = product_obj.browse(product_info["id"]).with_context(location=config.location_id.id)
                else:
                    product = product_obj.browse(product_info["id"])
                product_info["qty_available"] = product.qty_available
                product_info["free_qty"] = product.free_qty
                product_info['type'] = product.type
        return super()._process_pos_ui_product_product(products)
