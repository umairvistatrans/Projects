from odoo import models, fields
import xmlrpc.client
url_odoo13 = 'https://7md-ae.odoo.com'
db_odoo13 = '7md-ae-master-1152146'
username_odoo13 = 'test'
password_odoo13 = '123456'

common_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo13))
uid_odoo13 = common_odoo13.authenticate(db_odoo13, username_odoo13, password_odoo13, {})
models_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo13))
import logging
_logger = logging.getLogger(__name__)



class PurchaseWizard(models.TransientModel):
    _name = 'purchase.wizard'

    date = fields.Date(string='Date')

    # def perform_action(self):
    #     start_date_str = self.date.strftime('%Y-%m-%d 00:00:00')
    #     end_date_str = self.date.strftime('%Y-%m-%d 23:59:59')
    #     search_domain = [('date_order', '>=', start_date_str),
    #                      ('date_order', '<=', end_date_str)]
    #
    #     purchase_order_ids_odoo13 = models_odoo13.execute_kw(
    #         db_odoo13, uid_odoo13, password_odoo13,
    #         'purchase.order', 'search_read', [search_domain]
    #     )
    #     if len(purchase_order_ids_odoo13):
    #         for order in purchase_order_ids_odoo13:
    #             purchase_order = self.env['purchase.order'].search([('date_order', '=', order.get('date_order'))])
    #             if not purchase_order:
    #                 new_order_data = {
    #                     'partner_id': order.get('partner_id')[0] if order.get('partner_id') else False,
    #                     'date_approve': order.get('date_approve'),
    #                     'date_order': order.get('date_order'),
    #                     'create_date': order.get('create_date'),
    #                     'date_planned': order.get('date_planned'),
    #                     'name': order.get('name'),
    #                     'picking_type_id': order.get('picking_type_id')[0] if order.get('picking_type_id') else False,
    #                     'currency_id': order.get('currency_id')[0] if order.get('currency_id') else False,
    #                     'company_id': order.get('company_id')[0] if order.get('company_id') else False,
    #                     'state': order.get('state'),
    #                 }
    #                 purchase_order = self.env['purchase.order'].create(new_order_data)
    #                 _logger.info("order : %s ", order.get('id'))
    #                 order_lines = models_odoo13.execute_kw(
    #                     db_odoo13, uid_odoo13, password_odoo13,
    #                     'purchase.order.line', 'search_read', [[('order_id', '=', order.get('id'))]]
    #                 )
    #                 for order_line in order_lines:
    #                     if order_line.get('product_id'):
    #                         _logger.info("product : %s ", order_line.get('product_id'))
    #                         search_product_domain = [('id', '=', order_line.get('product_id')[0])]
    #                         product_id_odoo13 = models_odoo13.execute_kw(
    #                             db_odoo13, uid_odoo13, password_odoo13,
    #                             'product.product', 'search_read', [search_product_domain]
    #                         )
    #                         product_id = self.env['product.product'].search(
    #                             [('name', '=', product_id_odoo13[0].get('name')), ('default_code', '=', product_id_odoo13[0].get('default_code'))])
    #                         if not product_id:
    #                             vals = {
    #                                 "name": product_id_odoo13[0].get('name'),
    #                                 'default_code': product_id_odoo13[0].get('default_code'),
    #                                 "standard_price": product_id_odoo13[0].get('standard_price'),
    #                                 "list_price": product_id_odoo13[0].get('list_price'),
    #                             }
    #                             product_id = self.env['product.product'].create(vals)
    #                             _logger.info(order_line.get('taxes_id'))
    #                         new_order_line = self.env['purchase.order.line'].create({
    #                             'product_id': product_id.id,
    #                             'name': product_id.name,
    #                             'product_qty': order_line.get('product_qty'),
    #                             'price_unit': order_line.get('price_unit'),
    #                             'order_id': purchase_order.id,
    #                             'display_type': order_line.get('display_type'),
    #                             'taxes_id': order_line.get('taxes_id'),
    #                         })
    #                     elif not order_line.get('product_id') and order_line.get('display_type'):
    #                         new_order_line = self.env['purchase.order.line'].create({
    #                             'name': order_line.get('name'),
    #                             'product_qty': 0,
    #                             'order_id': purchase_order.id,
    #                             'display_type': order_line.get('display_type'),
    #                         })
    #                 stock_picking_ids = order.get('picking_ids', [])
    #                 for stock_picking_id in stock_picking_ids:
    #                     stock_picking_data = models_odoo13.execute_kw(
    #                         db_odoo13, uid_odoo13, password_odoo13,
    #                         'stock.picking', 'read', [stock_picking_id]
    #                     )
    #
    #                     new_stock_picking = purchase_order.picking_ids.create({
    #                         'partner_id': stock_picking_data[0].get('partner_id')[0] if stock_picking_data[0].get(
    #                             'partner_id') else False,
    #                         'picking_type_id': stock_picking_data[0].get('picking_type_id')[
    #                             0] if stock_picking_data[0].get('picking_type_id') else False,
    #                         'location_dest_id': stock_picking_data[0].get('location_dest_id')[
    #                             0] if stock_picking_data[0].get('location_dest_id') else False,
    #                         'location_id': stock_picking_data[0].get('location_id')[0] if stock_picking_data[0].get(
    #                             'location_id') else False,
    #                         'purchase_id': purchase_order.id,
    #                         'state': stock_picking_data[0].get('state'),
    #                         'scheduled_date': stock_picking_data[0].get('scheduled_date'),
    #                         'origin': stock_picking_data[0].get('origin'),
    #                         'date_done': stock_picking_data[0].get('date_done'),
    #                     })
    #                     # Create move lines in the stock picking
    #                     move_lines_data = models_odoo13.execute_kw(
    #                         db_odoo13, uid_odoo13, password_odoo13,
    #                         'stock.move', 'search_read', [[('picking_id', '=', stock_picking_id)]]
    #                     )
    #
    #                     for move_line_data in move_lines_data:
    #                         product_id = move_line_data.get('product_id')[0]
    #                         product_qty = move_line_data.get('product_uom_qty')
    #
    #                         # Find the corresponding purchase order line
    #                         purchase_order_line = purchase_order.order_line.filtered(
    #                             lambda line: line.product_id.id == product_id)
    #                         if purchase_order_line:
    #                             new_stock_picking.move_ids.create({
    #                                 'product_id': product_id,
    #                                 'name': move_line_data.get('name'),
    #                                 'product_uom_qty': product_qty,
    #                                 'quantity_done': product_qty if stock_picking_data[0].get('state') == 'done' else 0,
    #                                 'product_uom': move_line_data.get('product_uom')[0] if move_line_data.get(
    #                                     'product_uom') else False,
    #                                 'picking_id': new_stock_picking.id,
    #                                 'location_id': move_line_data.get('location_id')[0],
    #                                 'location_dest_id': move_line_data.get('location_dest_id')[0],
    #                                 'purchase_line_id': purchase_order_line.id,
    #                             })
    #                     if stock_picking_data[0].get('state') == 'done':
    #                         new_stock_picking.state = 'done'
    #                     else:
    #                         new_stock_picking.state = 'assigned'
    #                 all_pickings_done = all(picking.state == 'done' for picking in purchase_order.picking_ids)
    #                 if len(order.get('invoice_ids', [])) and all_pickings_done:
    #                     purchase_order.action_create_invoice()
    #                     for invoice_id in order.get('invoice_ids', []):
    #                         invoice_data = models_odoo13.execute_kw(
    #                             db_odoo13, uid_odoo13, password_odoo13,
    #                             'account.move', 'read', [invoice_id]
    #                         )
    #
    #                         existing_invoice = self.env['account.move'].search(
    #                             [('invoice_origin', '=', invoice_data[0].get('invoice_origin'))])
    #
    #                         if existing_invoice:
    #                             # Update the existing invoice status
    #                             existing_invoice.write({
    #                                 'state': invoice_data[0].get('state'),
    #                                 'invoice_date': invoice_data[0].get('invoice_date'),
    #                                 'invoice_date_due': invoice_data[0].get('invoice_date_due'),
    #                             })
    #
    #                 print("New Purchase Order created with ID:", purchase_order.id)
    #     return True
    def perform_action(self):
        start_date_str = self.date.strftime('%Y-%m-%d 00:00:00')
        end_date_str = self.date.strftime('%Y-%m-%d 23:59:59')
        all_config_ids = self.env['pos.config'].search([])
        for config in all_config_ids:
            all_orders = self.env['pos.order'].search([('config_id', '=', config.id),('payment_ids', '=', False), ('date_order', '>=', start_date_str), ('date_order', '<=', end_date_str)])
            for order in all_orders:
                search_domain = [('pos_order_id.name', '=', order.name)]
                pos_payment_ids_odoo13 = models_odoo13.execute_kw(
                    db_odoo13, uid_odoo13, password_odoo13,
                    'pos.payment', 'search_read', [search_domain]
                )
                if len(pos_payment_ids_odoo13):
                    for payment in pos_payment_ids_odoo13:
                        pos_payment = self.env['pos.payment'].search([('payment_date', '=', payment.get('payment_date'))])
                        payment_method = self.env['pos.payment.method'].search([('name', '=', payment.get('payment_method_id')[1])])
                        if not pos_payment:
                            session_id = order.session_id
                            # if payment.get('payment_method_id')[0] in config_id.payment_method_ids.ids:
                            new_payment_data = {
                                'payment_date': payment.get('payment_date'),
                                'create_date': payment.get('create_date'),
                                'amount': payment.get('amount'),
                                'card_type': payment.get('card_type'),
                                'name': payment.get('name'),
                                'pos_order_id': order.id,
                                'payment_method_id': payment_method.id,
                                'session_id': session_id.id,
                            }
                            print("conf name is :", config.name)
                            print("payment method is :", payment.get('payment_method_id')[1])
                            print("order  is :", payment.get('pos_order_id')[1])
                            print("session  is :", payment.get('session_id')[1])
                            pos_payment = self.env['pos.payment'].create(new_payment_data)
                            _logger.info("PAyment : %s ", payment.get('id'))
                        # order_lines = models_odoo13.execute_kw(
                        #     db_odoo13, uid_odoo13, password_odoo13,
                        #     'purchase.order.line', 'search_read', [[('order_id', '=', payment.get('id'))]]
                        # )
                        # for order_line in order_lines:
                        #     if order_line.get('product_id'):
                        #         _logger.info("product : %s ", order_line.get('product_id'))
                        #         search_product_domain = [('id', '=', order_line.get('product_id')[0])]
                        #         product_id_odoo13 = models_odoo13.execute_kw(
                        #             db_odoo13, uid_odoo13, password_odoo13,
                        #             'product.product', 'search_read', [search_product_domain]
                        #         )
                        #         product_id = self.env['product.product'].search(
                        #             [('name', '=', product_id_odoo13[0].get('name')), ('default_code', '=', product_id_odoo13[0].get('default_code'))])
                        #         if not product_id:
                        #             vals = {
                        #                 "name": product_id_odoo13[0].get('name'),
                        #                 'default_code': product_id_odoo13[0].get('default_code'),
                        #                 "standard_price": product_id_odoo13[0].get('standard_price'),
                        #                 "list_price": product_id_odoo13[0].get('list_price'),
                        #             }
                        #             product_id = self.env['product.product'].create(vals)
                        #             _logger.info(order_line.get('taxes_id'))
                        #         new_order_line = self.env['purchase.order.line'].create({
                        #             'product_id': product_id.id,
                        #             'name': product_id.name,
                        #             'product_qty': order_line.get('product_qty'),
                        #             'price_unit': order_line.get('price_unit'),
                        #             'order_id': purchase_order.id,
                        #             'display_type': order_line.get('display_type'),
                        #             'taxes_id': order_line.get('taxes_id'),
                        #         })
                        #     elif not order_line.get('product_id') and order_line.get('display_type'):
                        #         new_order_line = self.env['purchase.order.line'].create({
                        #             'name': order_line.get('name'),
                        #             'product_qty': 0,
                        #             'order_id': purchase_order.id,
                        #             'display_type': order_line.get('display_type'),
                        #         })
                        # stock_picking_ids = order.get('picking_ids', [])
                        # for stock_picking_id in stock_picking_ids:
                        #     stock_picking_data = models_odoo13.execute_kw(
                        #         db_odoo13, uid_odoo13, password_odoo13,
                        #         'stock.picking', 'read', [stock_picking_id]
                        #     )
                        #
                        #     new_stock_picking = purchase_order.picking_ids.create({
                        #         'partner_id': stock_picking_data[0].get('partner_id')[0] if stock_picking_data[0].get(
                        #             'partner_id') else False,
                        #         'picking_type_id': stock_picking_data[0].get('picking_type_id')[
                        #             0] if stock_picking_data[0].get('picking_type_id') else False,
                        #         'location_dest_id': stock_picking_data[0].get('location_dest_id')[
                        #             0] if stock_picking_data[0].get('location_dest_id') else False,
                        #         'location_id': stock_picking_data[0].get('location_id')[0] if stock_picking_data[0].get(
                        #             'location_id') else False,
                        #         'purchase_id': purchase_order.id,
                        #         'state': stock_picking_data[0].get('state'),
                        #         'scheduled_date': stock_picking_data[0].get('scheduled_date'),
                        #         'origin': stock_picking_data[0].get('origin'),
                        #         'date_done': stock_picking_data[0].get('date_done'),
                        #     })
                        #     # Create move lines in the stock picking
                        #     move_lines_data = models_odoo13.execute_kw(
                        #         db_odoo13, uid_odoo13, password_odoo13,
                        #         'stock.move', 'search_read', [[('picking_id', '=', stock_picking_id)]]
                        #     )
                        #
                        #     for move_line_data in move_lines_data:
                        #         product_id = move_line_data.get('product_id')[0]
                        #         product_qty = move_line_data.get('product_uom_qty')
                        #
                        #         # Find the corresponding purchase order line
                        #         purchase_order_line = purchase_order.order_line.filtered(
                        #             lambda line: line.product_id.id == product_id)
                        #         if purchase_order_line:
                        #             new_stock_picking.move_ids.create({
                        #                 'product_id': product_id,
                        #                 'name': move_line_data.get('name'),
                        #                 'product_uom_qty': product_qty,
                        #                 'quantity_done': product_qty if stock_picking_data[0].get('state') == 'done' else 0,
                        #                 'product_uom': move_line_data.get('product_uom')[0] if move_line_data.get(
                        #                     'product_uom') else False,
                        #                 'picking_id': new_stock_picking.id,
                        #                 'location_id': move_line_data.get('location_id')[0],
                        #                 'location_dest_id': move_line_data.get('location_dest_id')[0],
                        #                 'purchase_line_id': purchase_order_line.id,
                        #             })
                        #     if stock_picking_data[0].get('state') == 'done':
                        #         new_stock_picking.state = 'done'
                        #     else:
                        #         new_stock_picking.state = 'assigned'
                        # all_pickings_done = all(picking.state == 'done' for picking in purchase_order.picking_ids)
                        # if len(order.get('invoice_ids', [])) and all_pickings_done:
                        #     purchase_order.action_create_invoice()
                        #     for invoice_id in order.get('invoice_ids', []):
                        #         invoice_data = models_odoo13.execute_kw(
                        #             db_odoo13, uid_odoo13, password_odoo13,
                        #             'account.move', 'read', [invoice_id]
                        #         )
                        #
                        #         existing_invoice = self.env['account.move'].search(
                        #             [('invoice_origin', '=', invoice_data[0].get('invoice_origin'))])
                        #
                        #         if existing_invoice:
                        #             # Update the existing invoice status
                        #             existing_invoice.write({
                        #                 'state': invoice_data[0].get('state'),
                        #                 'invoice_date': invoice_data[0].get('invoice_date'),
                        #                 'invoice_date_due': invoice_data[0].get('invoice_date_due'),
                        #             })

                            print("New payment created with ID:", pos_payment.id)
        return True
