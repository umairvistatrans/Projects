# -*- coding: utf-8 -*-
from odoo import models, fields,api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # def _prepare_procurement_values(self, group_id=False):
    #     res = super(SaleOrderLine, self)._prepare_procurement_values()
    #     res.update({'city_route_id':self.order_id.shipping_city_id.id})
    #     return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_city_id = fields.Many2one(comodel_name="res.country.state", string="Shipping City", required=False, )


    fully_address = fields.Char(string="Fully address", required=False,compute='get_fully_address' )

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self.picking_ids:
            rec.city_route_id = self.shipping_city_id.id
            # rec.fully_address = self.fully_address
        return res

    @api.depends()
    def get_fully_address(self):
        for rec in self:
            rec.fully_address =str( ' , '.join([rec.shipping_first_name or '', rec.shipping_last_name or '', rec.shipping_address_2 or '',rec.shipping_city or '',rec.shipping_state or '',rec.shipping_zip or '',rec.shipping_country or '']))

    @api.onchange('partner_id')
    def get_shipping_city(self):
        if self.partner_id.state_id:
            self.shipping_city_id = self.partner_id.state_id.id
        else:
            self.shipping_city_id = False




# SaleOrder()
