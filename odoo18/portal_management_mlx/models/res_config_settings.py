# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    supplier_link_password = fields.Char("Supplier Link Password", config_parameter='portal_management_mlx.supplier_link_password')
    supplier_link_url = fields.Char("Supplier Link URL", config_parameter='portal_management_mlx.supplier_link_url')

    def set_values(self):
        """Override set_values to store the setting in ir.config_parameter."""
        super(ResConfigSettings, self).set_values()
        # Store the setting value in ir.config_parameter for all fields
        params = {
            'portal_management_mlx.supplier_link_password': self.supplier_link_password,
        }
        for key, value in params.items():
            self.env['ir.config_parameter'].sudo().set_param(key, value)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
        supplier_form_url = base_url + '/requests/supplier'
        self.env['ir.config_parameter'].sudo().set_param('portal_management_mlx.supplier_link_url', supplier_form_url)

        if 'portal_management_mlx.supplier_link_password' in params:
            view = self.sudo().env.ref('portal_management_mlx.submit_supplier')
            view.visibility_password = self.supplier_link_password

    @api.model
    def get_values(self):
        """Override get_values to retrieve the setting from ir.config_parameter."""
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        # Retrieve the setting values from ir.config_parameter
        res.update({
            'supplier_link_password': ConfigParameter.get_param(
                'portal_management_mlx.supplier_link_password', default=''),
            'supplier_link_url': ConfigParameter.get_param(
                'portal_management_mlx.supplier_link_url', default=''),
        })
        return res
