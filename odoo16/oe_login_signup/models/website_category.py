from odoo import models, fields, api, _

class WebsiteCategory(models.Model):
    _inherit = 'product.public.category'

    icon = fields.Char(default='list')


