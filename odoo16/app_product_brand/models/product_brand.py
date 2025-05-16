from odoo import api, fields, models, _


class ProductBrand(models.Model):
    _name = 'product.brand'
    
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Brand"
    _order = 'sequence, name'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File', attachment=True)
    product_ids = fields.One2many(
        'product.template',
        'product_brand_rec_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )
    sequence = fields.Integer('Sequence', help="Determine the display order", default=10)

    @api.depends('product_ids')
    def _compute_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)

