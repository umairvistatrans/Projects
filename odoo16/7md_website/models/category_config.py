# from odoo import fields, models
#
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     todays_deals_ids = fields.Many2many('product.product','website_todays_deals_rel', string="Today's Deals")
#     top_selling_ids = fields.Many2many('product.product','website_top_selling_rel', string="Top Selling")
#
#     def set_values(self):
#         super(ResConfigSettings, self).set_values()
#         # Ensure only IDs are serialized
#         todays_deals_str = ','.join(map(str, self.todays_deals_ids.ids))
#         top_selling_str = ','.join(map(str, self.top_selling_ids.ids))
#         self.env['ir.config_parameter'].sudo().set_param('7md_website.todays_deals_ids', todays_deals_str)
#         self.env['ir.config_parameter'].sudo().set_param('7md_website.top_selling_ids', top_selling_str)
#
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         todays_deals_str = self.env['ir.config_parameter'].sudo().get_param('7md_website.todays_deals_ids',default='')
#         top_selling_str = self.env['ir.config_parameter'].sudo().get_param('7md_website.top_selling_ids',default='')
#         # Filter out any entries that cannot be converted to integers
#         todays_dealsm2m_ids = [int(i) for i in todays_deals_str.split(',') if i.isdigit()]
#         top_sellingm2m_ids = [int(i) for i in top_selling_str.split(',') if i.isdigit()]
#         res['todays_deals_ids'] = [(6, 0, todays_dealsm2m_ids)]
#         res['top_selling_ids'] = [(6, 0, top_sellingm2m_ids)]
#         return res


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from collections import defaultdict


class OeNavbarConfig(models.Model):
    _name = 'navbar.category.config'

    name = fields.Char('Category Name', required=True, translate=True)
    icon = fields.Char('Icon')
    product_ids = fields.Many2many('product.product', 'website_product_rel', string="Products")
    product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='nav_category_config_product_category_rel',
        column1='nav_category_id',
        column2='product_category_id',
        string='Product Categories'
    )
    product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
            ('by_wishlist', 'By Wishlist'),
            ('top_selling', 'Top Selling'),
            ('top_trending', 'Top Trending')
        ], string="Product Selection Criteria", default='by_product')

    limit = fields.Integer("Limit", help="How many product want to show for this product type default 10 will show")
    check_type_compute = fields.Boolean("Check Product Type", compute="_check_compute_type")

    @api.depends("product_type")
    def _check_compute_type(self):
        for rec in self:
            rec.check_type_compute = True
            if rec.product_type in ['by_wishlist', 'top_selling', 'top_trending']:
                rec.product_ids = None
                rec.product_category_ids = None


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=1, set_qty=0, **kwargs):
        result = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty,
                                                     set_qty=set_qty, **kwargs)
        free_shipping_lines = self.order_line.filtered(lambda l: l.reward_id.reward_type == 'shipping')
        if free_shipping_lines:
            for free_shipping_line in free_shipping_lines:
                if self.amount_total < free_shipping_line.reward_id.required_points:
                    free_shipping_line.reward_id = False
                    free_shipping_line.unlink()
        return result

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    available_qty_wh = fields.Float(string='Available Quantity in WH', compute='_compute_available_qty_wh')

    @api.depends('stock_quant_ids')
    def _compute_available_qty_wh(self):
        warehouse = self.env['stock.warehouse'].search([('code', '=', 'WH')], limit=1)
        if warehouse:
            location = warehouse.lot_stock_id
            for product in self:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location.id)
                ])
                product.available_qty_wh = sum(quant.mapped('quantity'))
