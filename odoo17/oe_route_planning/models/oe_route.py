# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class OERouteMaster(models.Model):
    _name = "oe.route.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Route Master'
    _rec_name = "code"

    name = fields.Char(string='Name', tracking=True, required=True)
    code = fields.Char(string='Code', readonly=True, tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    zip = fields.Char(change_default=True, tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', 
                                domain="[('country_id', '=?', country_id)]", tracking=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code'] = self.env['ir.sequence'].next_by_code('oe.route.master.sequence') or '/'
        return super(OERouteMaster, self).create(vals_list)
