from odoo import api, fields, models, _


class Lead(models.Model):
    _inherit = "crm.lead"


    web_store_id = fields.Many2one('oe.store.location', string="7md Store")

