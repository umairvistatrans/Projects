# -*- coding: utf-8 -*-

from odoo import fields, models
from datetime import datetime,timedelta

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ex_company_id = fields.Many2one('res.company', config_parameter='external_commerce_integration.company_id', string='Company',
                               copy=True)
    ex_website_url = fields.Char(config_parameter='external_commerce_integration.website_url', string='Website URL',
                               copy=True, default='http://134.209.155.165/public')
    ex_user_name = fields.Char(config_parameter='external_commerce_integration.ex_username', string='Login Email',
                               copy=True, default='nazila@innovationbox.ae')
    ex_password = fields.Char(config_parameter='external_commerce_integration.ex_password', string='Password',
                              copy=True, default='nazila@123')
    last_sync_date = fields.Char(config_parameter='external_commerce_integration.last_sync', string='Last Sync',
                              copy=True, default=lambda x:str(datetime.now().date() - timedelta(days=400)))
    last_sync_date_set = fields.Char(config_parameter='external_commerce_integration.last_sync_set', string='Last Sync Set',
                              copy=True, default=lambda x:str(datetime.now().date() - timedelta(days=400)))

    ex_location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        config_parameter='external_commerce_integration.location_id',
    )


# ResConfigSettings()
