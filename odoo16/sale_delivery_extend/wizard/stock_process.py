# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import datetime,date


class StockImmProcess(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    # def check_create_purchase(self):
    #     for rec in self.pick_ids:
    #         if rec.carrier_id and rec.carrier_id.delivery_pay_type != 'normal':
    #             if rec.carrier_id.partner_id.id:
    #                 carrier_period_id = self.env['delivery.carrier.address'].search([
    #                     ('carrier_id', '=', rec.carrier_id.id),
    #                     ('to_country_id', '=', rec.partner_id.country_id.id),
    #                     ('to_state_id', '=', rec.partner_id.state_id.id),
    #                     ('country_id', '=', rec.to_country_id.id),
    #                     ('state_id', '=', rec.to_state_id.id)], limit=1, order='id desc')
    #                 if carrier_period_id:
    #                     price = carrier_period_id.value
    #                 else:
    #                     raise UserError(_("No Vendor Price found for the current from and to destinations\n"
    #                                       "Please Check the Customer Address and Vendor Prices"))
    #                 last_po = self.env['purchase.order'].sudo().search([
    #                     ('partner_id', '=', rec.carrier_id.partner_id.id),
    #                     ('state', '=', 'draft')], limit=1, order='id desc')
    #                 if last_po:
    #                     if (last_po.create_date - datetime.now()).days <= rec.carrier_id.vendor_days:
    #                         last_po.write({'order_line': [
    #                             (0, 0, {
    #                                 'name': "%s \n %s\n %s - %s \n %s - %s" % (
    #                                     rec.name,
    #                                     rec.partner_id.name,
    #                                     carrier_period_id.country_id.name,
    #                                     carrier_period_id.state_id.name,
    #                                     rec.partner_id.country_id.name,
    #                                     rec.partner_id.state_id.name),
    #                                 'product_id': rec.carrier_id.product_id.id,
    #                                 'product_qty': 1,
    #                                 'product_uom': rec.carrier_id.product_id.uom_po_id.id,
    #                                 'price_unit': price,
    #                                 'date_planned': fields.Datetime.now(),
    #                             })]})
    #                         rec.write({'carrier_po_id': last_po.id})
    #                     else:
    #                         purchase_order = self.env['purchase.order'].create({
    #                             'partner_id': rec.carrier_id.partner_id.id,
    #                             'order_line': [
    #                                 (0, 0, {
    #                                     'name': "%s \n %s\n %s - %s \n %s - %s" % (
    #                                         rec.name,
    #                                         rec.partner_id.name,
    #                                         carrier_period_id.country_id.name,
    #                                         carrier_period_id.state_id.name,
    #                                         rec.partner_id.country_id.name,
    #                                         rec.partner_id.state_id.name),
    #                                     'product_id': rec.carrier_id.product_id.id,
    #                                     'product_qty': 1,
    #                                     'product_uom': rec.carrier_id.product_id.uom_po_id.id,
    #                                     'price_unit': price,
    #                                     'date_planned': fields.Datetime.now(),
    #                                 })]
    #                         })
    #                         rec.write({'carrier_po_id': purchase_order.id})
    #                 else:
    #                     purchase_order = self.env['purchase.order'].create({
    #                         'partner_id': rec.carrier_id.partner_id.id,
    #                         'order_line': [
    #                             (0, 0, {
    #                                 'name': "%s \n %s\n %s - %s \n %s - %s" % (
    #                                     rec.name,
    #                                     rec.partner_id.name,
    #                                     carrier_period_id.country_id.name,
    #                                     carrier_period_id.state_id.name,
    #                                     rec.partner_id.country_id.name,
    #                                     rec.partner_id.state_id.name),
    #                                 'product_id': rec.carrier_id.product_id.id,
    #                                 'product_qty': 1,
    #                                 'product_uom': rec.carrier_id.product_id.uom_po_id.id,
    #                                 'price_unit': price,
    #                                 'date_planned': fields.Datetime.now(),
    #                             })]
    #                     })
    #                     rec.write({'carrier_po_id': purchase_order.id})
    #
    #             else:
    #                 raise UserError(_("You can't uses this carrier without assign vendor"))
    #     return True


    # def process(self):
    #     res = super(StockImmProcess, self).process()
    #     # self.check_create_purchase()
    #     return res

    # def process(self):
    #     res = super(StockImmProcess, self).process()
    #     for pick in self.pick_ids:
    #         if pick.carrier_id and pick.carrier_id.delivery_pay_type != 'normal':
    #             price = 0.0
    #             shipping_order_id = self.env['shipping.order']
    #             for rec in pick.carrier_id.delivery_period_ids:
    #                 if pick.city_route_id.id == rec.to_state_id.id:
    #                     price = rec.value
    #             so_id = self.env['sale.order'].search([('name', '=', pick.origin)], limit=1)
    #             shipping_order_lines = []
    #             shipping_order_lines.append((0,0,{
    #                 'so_id':so_id.id,
    #                 'partner_id':so_id.partner_id.id,
    #                 'customer_mob_no':so_id.partner_id.mobile,
    #                 'customer_email':so_id.partner_id.email,
    #                 'delivery_id':pick.id,
    #                 'delivery_state':pick.state,
    #                 'route_id': pick.city_route_id.id,
    #                 'shipping_price': price,
    #                 'total_order_price': so_id.amount_total,
    #                 'payment_method_desc': so_id.payment_method_desc,
    #                 'cash_receiving_state': 'not_collected' if so_id.payment_method_desc == 'Cash On Delivery' else 'prepaid',
    #                 'notes': pick.shipping_notes,
    #             }))
    #             shipping_order_filtered = self.env['shipping.order'].search([('shipping_company_id','=',pick.carrier_id.partner_id.id),('date','=',date.today())],limit=1)
    #             if shipping_order_filtered:
    #                 shipping_order_filtered.update({'order_ids':shipping_order_lines,'carrier_id':pick.carrier_id.id,})
    #                 pick.shipping_order_id = shipping_order_filtered.id
    #             else:
    #                 ship_order_created = shipping_order_id.create({
    #                     'shipping_company_id':pick.carrier_id.partner_id.id,
    #                     'date':date.today(),
    #                     'order_ids':shipping_order_lines,
    #                     'carrier_id':pick.carrier_id.id,
    #                 })
    #                 pick.shipping_order_id = ship_order_created.id
    #     return res


