from odoo import models, fields, api
from datetime import datetime,timedelta


class SubStockLocation(models.Model):
    _name = 'sub.stock.location'

    location_id = fields.Many2one('stock.location', string="Location")
    main_location_id = fields.Many2one('stock.location', string="Main Location")

class StockLocation(models.Model):
    _inherit = 'stock.location'

    sub_location_ids = fields.One2many('stock.location', 'main_id', string="Sub Locations")
    main_id = fields.Many2one('stock.location', string="Main Location")