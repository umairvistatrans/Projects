from odoo import models, fields, api
from datetime import datetime,timedelta


class ResCompany(models.Model):
    _inherit = 'res.company'

    ex_website_url = fields.Char(string='Website URL', copy=True, default='http://134.209.155.165/public')
    ex_user_name = fields.Char(string='Login Email', copy=True, default='nazila@innovationbox.ae')
    ex_password = fields.Char(string='Password', copy=True, default='nazila@123')
    last_sync_date = fields.Char(string='Last Sync', copy=True,
                                 default=lambda x: str(datetime.now().date() - timedelta(days=400)))
    last_sync_date_set = fields.Char(string='Last Sync Set', copy=True,
                                     default=lambda x: str(datetime.now().date() - timedelta(days=400)))
    ex_location_id = fields.Many2one('stock.location', string='Stock Location',)
    is_ex_active = fields.Boolean(string="Active")
