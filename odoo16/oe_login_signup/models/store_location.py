from odoo import fields, models, api, _


class OeStoreLocation(models.Model):
    _name = 'oe.store.location'
    _description = 'Stores Location'
    _inherit = 'mail.thread'

    name = fields.Char('Store Name', required=True)
    url_name = fields.Char('URL Name', compute="_get_url_name", store="True")
    phone_number = fields.Char('Phone Number')
    longitude = fields.Float('Longitude')
    latitude = fields.Float('Latitude')

    @api.depends('name')
    @api.onchange('name')
    def _get_url_name(self):
        for rec in self:
            rec.url_name = False
            if rec.name:
                lower_case_name = rec.name.lower()
                rec.url_name = lower_case_name.replace(" ", "_")
