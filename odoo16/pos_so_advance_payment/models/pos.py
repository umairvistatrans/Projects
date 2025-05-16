# -*- coding: utf-8 -*-
import time
from datetime import datetime,date
from odoo import fields, models, api, _
from functools import partial



class account_move(models.Model):
    _inherit = "account.move"

    cashier = fields.Many2one('hr.employee', string="Cashier")

class sale_orderLine(models.Model):
    _inherit = 'sale.order.line'
    note = fields.Char()
    eWalletGiftCardProgramId = fields.Many2one('loyalty.card')
    customer_note = fields.Char()


class sale_order(models.Model):
    _inherit = 'sale.order'

    pos_payment_method = fields.Many2one('pos.payment.method')
    pos_sales_person_id = fields.Many2one("hr.employee", string="Cashier")

    def _order_line_fields(self, line):
        if line and 'tax_ids' not in line[2]:
            product = self.env['product.product'].browse(line[2]['product_id'])
            line[2]['tax_ids'] = [(6, 0, [x.id for x in product.taxes_id])]
        line[2]['product_uom_qty'] = line[2].get('qty')
        line[2]['tax_id'] = line[2].get('tax_ids')
        line[2]['product_packaging_id'] = line[2].get('pack_lot_ids')
        line[2]['name'] = line[2].get('description') if line[2].get('description') else self.env['product.product'].browse(line[2]['product_id']).display_name
        if 'price_automatically_set' in line[2].keys():
            del line[2]['price_automatically_set']
        if 'qty' in line[2].keys():
            del line[2]['qty']
            del line[2]['price_subtotal_incl']
            del line[2]['tax_ids']
            if "pack_lot_ids" in line[2]:
                del line[2]['pack_lot_ids']
            if 'description' in line[2]:
                del line[2]['description']
            del line[2]['full_product_name']
            if "price_extra" in line[2]:
                del line[2]['price_extra']
            del line[2]['price_manually_set']
        return line

    @api.model
    def _order_fields(self, ui_order):
        partner = self.env['res.partner']
        process_line = self._order_line_fields
        shipping_id = False
        if ui_order.get('partner_shiping_id'):
            shipping_id = int(ui_order.get('partner_shiping_id'))
            partner.browse(shipping_id).write(
                {
                'street': ui_order.get('street'),
                 'street2': ui_order.get('street2'),
                 'city': ui_order.get('city'),
                 'phone': ui_order.get('phone'),
                 'mobile': ui_order.get('mobile')})
        else:
            shipping_id = partner.create({
                'name': ui_order.get('c_name'),
                'street': ui_order.get('street'),
                'street2': ui_order.get('street2'),
                'city': ui_order.get('city'),
                'parent_id': ui_order.get('parent_id'),
                'phone': ui_order.get('phone'),
                'mobile': ui_order.get('mobile'),
                'type': 'delivery',
            }).id
        return {
            'user_id': ui_order['user_id'],
            'order_line': [process_line(l) for l in ui_order['lines']] if
            ui_order['lines'] else False,
            'partner_id': ui_order['partner_id'] or False,
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'partner_shipping_id': shipping_id,
            'note': ui_order['note']
        }

    # @api.multi
    def register_down_payment_inv(self, register_down_payment_inv_rec,
                                  journal_id):
        account_payment = self.env['account.payment']
        fields = ['amount', 'journal_id', 'payment_date', 'partner_type',
                  'partner_id', 'payment_type', 'invoice_ids',
                  'payment_method_id']
        payment_dict = account_payment.with_context(default_invoice_ids=[
            (4, register_down_payment_inv_rec.id, None)]).default_get(fields)
        
        payment_id = account_payment.create({
            'amount': payment_dict.get('amount') or False,
            'journal_id': journal_id,
            'payment_date': payment_dict.get('payment_date') or False,
            'partner_type': payment_dict.get('partner_type') or False,
            'partner_id': payment_dict.get('partner_id') or False,
            'payment_type': payment_dict.get('payment_type') or False,
            'invoice_ids': payment_dict.get('invoice_ids') or False,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id,
        })
        payment_id.post()

    @api.model
    def create_new_quotation(self, quotation, attachment_data):
        quotation_obj = self.create(self._order_fields(quotation))
        if attachment_data:
            for attachment in attachment_data:
                attachment_record = self.env['ir.attachment'].create({
                    'name': attachment.get('name'),
                    'datas': attachment.get('data'),
                    'res_model': 'sale.order',
                    'res_id': quotation_obj.id,
                })
                quotation_obj.message_ids.attachment_ids |= attachment_record
        quotation_obj.pos_payment_method = quotation.get('payment_journal')
        quotation_obj.pos_sales_person_id = quotation.get('employee_id')
        session_id = self.env['pos.session'].browse(
            quotation['pos_session_id'])
        adv_payment_product = False
        if session_id.config_id.pos_sale_order_state == 'sale_order':
            quotation_obj.action_confirm()
            if quotation.get('advance_pay') and \
                    float(quotation.get('advance_pay')) > 0:
                adv_payment = self.env['sale.advance.payment.inv']
                sale_line_obj = self.env['sale.order.line']
                amount = float(quotation.get('advance_pay'))
                adv_payment_rec = adv_payment.create(
                    {'advance_payment_method': 'fixed',
                     'amount': amount,
                     'fixed_amount': amount})

                adv_payment_rec.sale_order_ids = quotation_obj
                down_payment_inv_rec = adv_payment_rec._create_invoices(quotation_obj)

                adv_payment_product = adv_payment_rec.product_id
                down_payment_inv_rec.journal_id = quotation.get('pos_invoice_journal_id')
                down_payment_inv_rec.cashier = quotation.get('employee_id')
                down_payment_inv_rec.narration = quotation.get('note')
                down_payment_inv_rec.action_post()
                payment = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=down_payment_inv_rec.ids).create({
                    'payment_date': date.today()
                    })._create_payments()
            else:
                adv_payment = self.env['sale.advance.payment.inv']
                adv_payment_rec = adv_payment.create(
                    {'advance_payment_method': 'delivered'})

                adv_payment_rec.sale_order_ids = quotation_obj
                inv_rec = adv_payment_rec._create_invoices(quotation_obj)
                inv_rec.cashier = quotation.get('employee_id')
                inv_rec.narration = quotation.get('note')
                inv_rec.journal_id = quotation.get('pos_invoice_journal_id')
                inv_rec.action_post()
        for invoice in quotation_obj.invoice_ids:
            invoice.narration = quotation.get('note')

        return quotation_obj.name


class pos_config(models.Model):
    _inherit = 'pos.config'

    allow_create_sale_order = fields.Boolean("Enable Creating SO from POS")
    pos_sale_order_state = fields.Selection([('draft', 'Quotation'),
                                             ('sale_order', 'Confirm')], default='draft',string='Default SO State')
    allow_advance_payment = fields.Boolean("Advance Payment")
    sale_payment_method_ids = fields.Many2many('pos.payment.method', 'pos_config_sale_payment_rel', 'config_id',
                                               'method_id')

    @api.onchange('pos_sale_order_state', 'allow_create_sale_order')
    def _onchange_so_state(self):
        if not self.allow_create_sale_order:
            self.allow_advance_payment = False
        if self.pos_sale_order_state == 'draft':
            self.allow_advance_payment = False
