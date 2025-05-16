from odoo import models, fields
import xmlrpc.client
from odoo.tests import Form, tagged


url_odoo13 = 'https://7md-ae.odoo.com'
db_odoo13 = '7md-ae-master-1152146'
username_odoo13 = 'test'
password_odoo13 = '123456'

common_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo13))
uid_odoo13 = common_odoo13.authenticate(db_odoo13, username_odoo13, password_odoo13, {})

models_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo13))


class SalesWizard(models.TransientModel):
    _name = 'sales.wizard'

    date = fields.Date(string='Date')

    def perform_action(self):
        start_date_str = self.date.strftime('%Y-%m-%d 00:00:00')
        end_date_str = self.date.strftime('%Y-%m-%d 23:59:59')
        search_domain = [('date_order', '>=', start_date_str),
                         ('date_order', '<=', end_date_str)]

        sale_order_ids_odoo13 = models_odoo13.execute_kw(
            db_odoo13, uid_odoo13, password_odoo13,
            'sale.order', 'search_read', [search_domain]
        )

        if len(sale_order_ids_odoo13):
            for order in sale_order_ids_odoo13:
                sale_order = self.env['sale.order'].search([('date_order', '=', order.get('date_order'))])
                if not sale_order:
                    search_partner_domain = [('id', '=', order.get('partner_id')[0])]
                    partner_id_odoo13 = models_odoo13.execute_kw(
                        db_odoo13, uid_odoo13, password_odoo13,
                        'res.partner', 'search_read', [search_partner_domain]
                    )
                    partner_id = self.env['res.partner'].search(
                        [('name', '=', partner_id_odoo13[0].get('name')), ('phone', '=', partner_id_odoo13[0].get('phone')), ('email', '=', partner_id_odoo13[0].get('email')),
                         ('ref_customer_id', '=', partner_id_odoo13[0].get('ref_customer_id'))])
                    if len(partner_id) > 1:
                        partner = partner_id[0]
                    else:
                        partner = partner_id
                    if not partner_id:
                        partner_vals = {'name': partner_id_odoo13[0].get('name'),
                                        'phone': partner_id_odoo13[0].get('phone'),
                                        'email': partner_id_odoo13[0].get('email'),
                                        'ref_customer_id': partner_id_odoo13[0].get('ref_customer_id')
                                        }
                        partner = self.env['res.partner'].create(partner_vals)
                    new_order_data = {
                        'partner_id': partner.id,
                        'date_order': order.get('date_order'),
                        'create_date': order.get('create_date'),
                        'external_id': order.get('external_id'),
                        'state': order.get('state'),
                        'name': order.get('name'),
                        'currency_id': order.get('currency_id')[0] if order.get('currency_id') else False,
                        'company_id': order.get('company_id')[0] if order.get('company_id') else False,
                    }
                    sale_order = self.env['sale.order'].create(new_order_data)
                    order_lines = models_odoo13.execute_kw(
                        db_odoo13, uid_odoo13, password_odoo13,
                        'sale.order.line', 'search_read', [[('order_id', '=', order.get('id'))]]
                    )

                    for line in order_lines:
                        search_product_domain = [('id', '=', line.get('product_id')[0])]
                        product_id_odoo13 = models_odoo13.execute_kw(
                            db_odoo13, uid_odoo13, password_odoo13,
                            'product.product', 'search_read', [search_product_domain]
                        )
                        if product_id_odoo13:
                            product_id = self.env['product.product'].search(
                                [('name', '=', product_id_odoo13[0].get('name')),
                                 ('default_code', '=', product_id_odoo13[0].get('default_code'))])
                            if not product_id:
                                vals = {
                                    "name": product_id_odoo13[0].get('name'),
                                    'default_code': product_id_odoo13[0].get('default_code'),
                                    "standard_price": product_id_odoo13[0].get('standard_price'),
                                    "list_price": product_id_odoo13[0].get('list_price'),
                                    # "detailed_type": product_id_odoo13[0].get('detailed_type'),
                                }
                                product_id = self.env['product.product'].create(vals)

                            new_order_line = self.env['sale.order.line'].create({
                                'product_id': product_id.id,
                                'name': line.get('name'),
                                'product_qty': line.get('product_qty'),
                                'price_unit': line.get('price_unit'),
                                'qty_delivered': line.get('qty_delivered'),
                                'qty_invoiced': line.get('qty_invoiced'),
                                'discount': line.get('discount'),
                                'product_uom_qty': line.get('product_uom_qty'),
                                'order_id': sale_order.id,
                            })

                    stock_picking_ids = order.get('picking_ids', [])
                    if sale_order.state == 'sale' and not sale_order.picking_ids and len(stock_picking_ids):
                        for stock_picking_id in stock_picking_ids:
                            stock_picking_data = models_odoo13.execute_kw(
                                db_odoo13, uid_odoo13, password_odoo13,
                                'stock.picking', 'read', [stock_picking_id]
                            )

                            new_stock_picking = sale_order.picking_ids.create({
                                'partner_id': sale_order.partner_id.id,
                                'picking_type_id': stock_picking_data[0].get('picking_type_id')[
                                    0] if stock_picking_data[0].get('picking_type_id') else False,
                                'location_dest_id': stock_picking_data[0].get('location_dest_id')[
                                    0] if stock_picking_data[0].get('location_dest_id') else False,
                                'location_id': stock_picking_data[0].get('location_id')[0] if stock_picking_data[0].get(
                                    'location_id') else False,
                                'sale_id': sale_order.id,
                                'scheduled_date': stock_picking_data[0].get('scheduled_date'),
                                'origin': stock_picking_data[0].get('origin'),
                                'date_done': stock_picking_data[0].get('date_done'),
                            })
                            # Create move lines in the stock picking
                            move_lines_data = models_odoo13.execute_kw(
                                db_odoo13, uid_odoo13, password_odoo13,
                                'stock.move', 'search_read', [[('picking_id', '=', stock_picking_id)]]
                            )

                            for move_line_data in move_lines_data:
                                product_id = move_line_data.get('product_id')[0]
                                product_qty = move_line_data.get('product_uom_qty')

                                # Find the corresponding sale order line
                                sale_order_line = sale_order.order_line.filtered(
                                    lambda line: line.product_id.id == product_id)

                                if sale_order_line:
                                    new_stock_move = new_stock_picking.move_ids.create({
                                        'product_id': product_id,
                                        'name': move_line_data.get('name'),
                                        # 'state': 'done' if stock_picking_data[0].get('state') == 'done' else 'draft',
                                        'product_uom_qty': product_qty,
                                        'quantity_done': product_qty if stock_picking_data[0].get('state') == 'done' else 0,
                                        'product_uom': move_line_data.get('product_uom')[0] if move_line_data.get(
                                            'product_uom') else False,
                                        'picking_id': new_stock_picking.id,
                                        'location_id': move_line_data.get('location_id')[0],
                                        'location_dest_id': move_line_data.get('location_dest_id')[0],
                                        'sale_line_id': sale_order_line.id,
                                    })
                                    print(f"stock_picking: {new_stock_picking.name},Product: {new_stock_move.product_id.name}, State: {new_stock_move.state}, Quantity Done: {new_stock_move.quantity_done}, stock move id: {new_stock_move.id}")
                            if stock_picking_data[0].get('state') == 'done':
                                new_stock_picking.state = 'done'
                            else:
                                new_stock_picking.state = 'assigned'
                    else:
                        for stock_picking_id in stock_picking_ids:
                            stock_picking_data = models_odoo13.execute_kw(
                                db_odoo13, uid_odoo13, password_odoo13,
                                'stock.picking', 'read', [stock_picking_id]
                            )

                            # Find the existing delivery order in Odoo 14 based on 'origin'
                            existing_delivery_order = sale_order.picking_ids.filtered(
                                lambda p: p.origin == stock_picking_data[0].get('origin'))

                            if existing_delivery_order:
                                # Update the existing delivery order
                                existing_delivery_order.write({
                                    'scheduled_date': stock_picking_data[0].get('scheduled_date'),
                                    'date_done': stock_picking_data[0].get('date_done'),
                                })
                                # Update the state of the delivery order
                                if stock_picking_data[0].get('state') == 'done':
                                    for line in existing_delivery_order.move_ids:
                                        line.quantity_done = line.product_uom_qty
                                    existing_delivery_order.state = 'done'
                                else:
                                    existing_delivery_order.state = 'assigned'

                    if len(order.get('invoice_ids', [])) and sale_order.state == 'sale':
                        invoice_wiz = self.env['sale.advance.payment.inv'].with_context(active_model="sale.order",
                                                                                        active_ids=sale_order.ids).create(
                            {
                                'advance_payment_method': 'delivered',
                            })
                        invoice_wiz._create_invoices(sale_order)
                        for invoice_id in order.get('invoice_ids', []):
                            invoice_data = models_odoo13.execute_kw(
                                db_odoo13, uid_odoo13, password_odoo13,
                                'account.move', 'read', [invoice_id]
                            )

                            existing_invoice = self.env['account.move'].search(
                                [('invoice_origin', '=', invoice_data[0].get('invoice_origin'))])

                            if existing_invoice:
                                # Update the existing invoice status
                                existing_invoice.write({
                                    'state': invoice_data[0].get('state'),
                                    'invoice_date': invoice_data[0].get('invoice_date'),
                                    'invoice_date_due': invoice_data[0].get('invoice_date_due'),
                                })

                    print("New sale Order created with ID:", sale_order.name)
        return True
