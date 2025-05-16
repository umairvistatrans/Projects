from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_rec_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )
