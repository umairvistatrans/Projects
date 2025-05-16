from odoo import models, fields

class InheritSaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def get_top_selling_products(self, limit=10):
        query = """
               SELECT 
                    sol.product_id,
                    SUM(sol.product_uom_qty) AS total_quantity 
                FROM 
                    sale_order_line AS sol
                JOIN 
                    product_product AS pp
                ON 
                    sol.product_id = pp.id
                JOIN 
                    product_template AS pt
                ON 
                    pp.product_tmpl_id = pt.id
                WHERE 
                    sol.state = 'sale' 
                    AND pt.detailed_type = 'product'
                GROUP BY 
                    sol.product_id 
                ORDER BY 
                    total_quantity DESC 
                LIMIT 
                    %s;
            """
        self.env.cr.execute(query, (limit,))
        result = self.env.cr.fetchall()

        product_ids = [product[0] for product in result]
        return self.env['product.product'].browse(product_ids)

