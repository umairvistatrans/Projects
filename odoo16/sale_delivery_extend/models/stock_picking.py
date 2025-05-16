# -*- coding: utf-8 -*-

from odoo import models, fields,api,exceptions
from datetime import datetime,date

class PosOrders(models.Model):
    _inherit = 'pos.order'

    def create_picking(self):
        res = super(PosOrders, self).create_picking()
        for order in self:
            order.picking_id.city_route_id = order.picking_id.partner_id.state_id.id
        return res



class SetDeliveryMethod(models.TransientModel):
    _name = 'set.delivery.method'

    def _default_get_company(self):
        return self.env.company.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,default=_default_get_company )

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="Fill this field if you plan to invoice the shipping based on picking.")
    city_route_id = fields.Many2one(comodel_name="res.country.state", string='To State')


    def set_delivery_methods(self):
        pickings = self.env["stock.picking"].browse(self.env.context.get("active_ids"))
        for pick in pickings:
            if not pick.carrier_id:
                pick.sudo().carrier_id = self.carrier_id.id
            if not pick.city_route_id:
                pick.sudo().city_route_id = self.city_route_id.id

    def set_delivery_method_and_create_shipping_order(self):
        pickings = self.env["stock.picking"].browse(self.env.context.get("active_ids"))
        for pick in pickings:
            if not pick.carrier_id:
                pick.sudo().carrier_id = self.carrier_id.id
            if not pick.city_route_id:
                pick.sudo().city_route_id = self.city_route_id.id
            pick.sudo().create_shipping_order()

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    ship_price = fields.Float('Ship Price',compute='compute_ship_price',inverse="_set_ship_price",store=True)
    def _set_ship_price(self):
        pass
        # _logger.info("Overtime Changed")
    @api.depends('move_ids_without_package','move_ids_without_package.product_id')
    def compute_ship_price(self):
        heavy = 0
        light = 0
        for rec in self:
            for move in rec.move_ids_without_package:
                if move.product_id.price_type == 'h':
                    heavy = move.product_id.price_val
                else:
                    light = move.product_id.price_val
            rec.ship_price = heavy if heavy else light

    def _default_get_city_route_id(self):
        return self.partner_id.state_id.id

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="Fill this field if you plan to invoice the shipping based on picking.")
    carrier_po_id = fields.Many2one(comodel_name='purchase.order', string='Linked Carrier PO')
    to_country_id = fields.Many2one(comodel_name='res.country', string='From Country', )
    to_state_id = fields.Many2one(comodel_name="res.country.state", string='From State', ondelete='restrict',
                                  domain="[('country_id', '=?', to_country_id)]")
    type_code=fields.Selection(related='picking_type_id.code',store=True, )
    delivery_pay_type = fields.Selection(related='carrier_id.delivery_pay_type', store=True, string='Delivery Handle')

    city_route_id = fields.Many2one(comodel_name="res.country.state", string='To State',default=_default_get_city_route_id)
    shipping_order_id = fields.Many2one(comodel_name="shipping.order", string="Shipping Order", required=False, )
    shipping_notes = fields.Text(string="Shipping Notes", required=False, )
    fullly_address = fields.Char(string="Fully Address", required=False, )
    shipping_state = fields.Selection(string="Shipping Status", selection=[('assigned', 'Assigned'), ('not_assigned', 'Not Assigned'), ], required=False,compute='check_shippng_state',store=True )
    invoice_no = fields.Char(string="Pos/Sales Invoice Number", required=False,compute='get_invoice_no' )
    woo_source_doc = fields.Char(string='Woo Origin Ref', compute='_get_woo_ref', search='_value_search')

    def _get_woo_ref(self):
        for rec in self:
            if rec.origin:
                sale_id = self.env['sale.order'].sudo().search([('name', '=', rec.origin)], limit=1)
                if sale_id:
                    rec.woo_source_doc = sale_id.woo_order_id
                else:
                    rec.woo_source_doc = ''
            else:
                rec.woo_source_doc = ''

    @api.depends('invoice_no')
    def get_invoice_no(self):
        for rec in self:
            rec.invoice_no = ''
            # pos_order = self.env['pos.order'].search([('picking_id','=',rec.id)],limit=1)
            sales_order = self.env['sale.order'].search([('name','=',rec.origin)],limit=1)
            # if pos_order:
            #     rec.invoice_no = pos_order.account_move.name
            if sales_order:
                rec.invoice_no = ' , '.join(sales_order.invoice_ids.mapped('name'))

    def create_shipping_order_wizard(self):
        return {
            'name': 'Create Shipping Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'set.delivery.method',
            'target': 'new',
            'context': {'default_carrier_id':self.carrier_id.id,'default_city_route_id':self.city_route_id.id}
        }


    def create_shipping_order(self):
        # for pick in self:
        if not self.carrier_id:
            raise exceptions.ValidationError("You can't create shipping order before select Delivery Method in this Delivery %s" %self.name)
        if not self.city_route_id:
            raise exceptions.ValidationError("You can't create shipping order before set To State in this Delivery %s" %self.name)
        if self.state != 'done':
            raise exceptions.ValidationError("You can't create shipping order in state %s in this Delivery %s" %self.state %self.name)
        if self.carrier_id and self.carrier_id.delivery_pay_type != 'normal':
            price = 0.0
            shipping_order_id = self.env['shipping.order']
            for rec in self.carrier_id.delivery_period_ids:
                if self.city_route_id.id == rec.to_state_id.id:
                    price = rec.value
            so_id = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
            pos_order = self.env['pos.order'].search([('picking_id','=',self.id)],limit=1)
            if pos_order and self.ship_price:
                price = self.ship_price
            p_method = ''
            crs = 'prepaid'
            if pos_order:
                pm = pos_order.payment_ids.filtered(lambda x:x.payment_method_id.is_cod)
                if pm:
                    p_method = 'Cash On Delivery'
                # if self.invoice_no:
                #     crs = 'not_collected'
            shipping_order_lines = []
            shipping_order_lines.append((0,0,{
                'so_id':so_id.id,
                'pos_order':pos_order.id,
                'partner_id':so_id.partner_id.id if so_id else pos_order.partner_id.id or self.partner_id.id,
                'customer_mob_no':so_id.partner_id.mobile if so_id else pos_order.partner_id.mobile or self.partner_id.mobile,
                'customer_email':so_id.partner_id.email if so_id else pos_order.partner_id.email or self.partner_id.email,
                'delivery_id':self.id,
                'delivery_state':self.state,
                'route_id': self.city_route_id.id,
                'shipping_price': price,
                'total_order_price': so_id.amount_total if so_id else pos_order.amount_total or 0.0,
                'payment_method_desc': so_id.payment_method_desc if so_id else p_method,
                'cash_receiving_state': 'not_collected' if so_id.payment_method_desc == 'Cash On Delivery' else crs,
                'notes': self.shipping_notes,
            }))
            shipping_order_filtered = self.env['shipping.order'].search([('shipping_company_id','=',self.carrier_id.partner_id.id),('date','=',date.today()),('related_bill','=',False)],limit=1)
            if shipping_order_filtered:
                shipping_order_filtered.update({'order_ids':shipping_order_lines,'carrier_id':self.carrier_id.id,})
                self.shipping_order_id = shipping_order_filtered.id
            else:
                ship_order_created = shipping_order_id.create({
                    'shipping_company_id':self.carrier_id.partner_id.id,
                    'date':date.today(),
                    'order_ids':shipping_order_lines,
                    'carrier_id':self.carrier_id.id,
                })
                self.shipping_order_id = ship_order_created.id


    @api.depends('shipping_order_id')
    def check_shippng_state(self):
        for rec in self:
            if rec.carrier_id:
                rec.shipping_state = 'assigned'
            else:
                rec.shipping_state = 'not_assigned'


    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        res.update({
            'to_country_id': self.env.ref('base.ae').id,
            'to_state_id': self.env.ref('base.state_ae_az').id,
            # 'city_route_id': self.partner_id.state_id.id,
        })
        return res





# StockPicking()
