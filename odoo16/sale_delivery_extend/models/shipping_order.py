# -*- coding: utf-8 -*-

from odoo import models, fields,api,_,exceptions
from datetime import datetime,date
import requests
import json
import re


class ShippingOrder(models.Model):
    _name = 'shipping.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = ''

    def get_default_company(self):
        return self.env.company.id

    name = fields.Char(string="Name", required=False,)
    shipping_company_id = fields.Many2one(comodel_name="res.partner", string="Shipping Company", required=False, )
    date = fields.Date(string="Date", required=False,)
    notes = fields.Text(string="Notes", required=False, )
    order_ids = fields.One2many(comodel_name="shipping.order.lines", inverse_name="shipping_order_id", string="", required=False, )

    state = fields.Selection(string="Status", selection=[('in_progress', 'In Progress'), ('completed', 'Completed'), ],compute='check_lines_states', required=False,store=True )
    related_po = fields.Many2one(comodel_name="purchase.order", string="Supplier PO", required=False, )
    related_bill = fields.Many2one(comodel_name="account.move", string="Vendor Bill", required=False, )
    related_payment = fields.Many2one(comodel_name="account.payment", string="Related Payment", required=False, )
    carrier_id = fields.Many2one(comodel_name="delivery.carrier", string="Delivery Method", required=False, )
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,default=get_default_company )
    show_create_po = fields.Boolean(compute='check_show_create_po')

    show_payment_created = fields.Boolean(compute='check_show_payment_created')

    @api.depends('show_create_po','order_ids')
    def check_show_create_po(self):
        filtered_lines = self.order_ids.filtered(lambda x:x.line_state in ['delivered'] and not x.in_po)
        if filtered_lines:
            self.show_create_po = True
        else:
            self.show_create_po = False


    @api.depends('show_payment_created', 'order_ids')
    def check_show_payment_created(self):
        filtered_lines = self.order_ids.filtered(lambda x: not x.payment_created)
        if filtered_lines:
            self.show_payment_created = True
        else:
            self.show_payment_created = False


    @api.model
    def create(self, vals):
        record_name = "/"

        vals.update({"name":str(self.env['ir.sequence'].next_by_code('shipping.order.sequence'))})
        return super(ShippingOrder, self).create(vals)



    @api.depends('order_ids','order_ids.line_state')
    def check_lines_states(self):
        self.state = 'in_progress'
        for rec in self.order_ids:
            if rec.line_state not in ['delivered','cancelled']:
                self.state = 'in_progress'
            else:
                self.state = 'completed'


    def create_shipping_bill(self):
        bill = self.env['account.move']
        customer_lines = self.order_ids.mapped('partner_id')
        shipping_order_lines= []
        for line in self.order_ids.filtered(lambda x:x.line_state =='delivered' and x.in_po == False):
            shipping_order_lines.append((0, 0, {
                'product_id': line.delivery_id.carrier_id.product_id.id,
                'name': "%s - %s - %s - %s - %s" % (
                                    line.so_id.name or '',
                                    line.partner_id.name or '',
                                    line.delivery_id.name or '',
                                    line.delivery_id.city_route_id.name or '',line.shipping_price or ''),
                'quantity': 1,
                'product_uom_id': line.delivery_id.carrier_id.product_id.uom_po_id.id,
                'price_unit': line.shipping_price,
                'display_type': False,
            }))
            line.in_po = True
        if shipping_order_lines:
            if not self.related_bill:
                bill_created = bill.sudo().create({
                    'partner_id':self.shipping_company_id.id,
                    'invoice_line_ids':shipping_order_lines,
                    'type':'in_invoice',
                })
                bill_created.action_post()
                self.related_bill = bill_created.id
            else:
                self.related_bill.update({'invoice_line_ids':shipping_order_lines})

    def create_cod_payment(self):
        payment = self.env['account.payment']
        for rec in self.order_ids:
            if not rec.payment_created:
                if rec.line_state == 'delivered':
                    total_amount = rec.total_order_price
                    if total_amount:
                        payment_created = payment.sudo().create({
                            'payment_type':'inbound',
                            'partner_id':rec.partner_id.id,
                            'partner_type':'customer',
                            'amount':total_amount,
                            'communication': str(rec.partner_id.name) +  str(' - ' ) + str(self.date) + str(' - ') + str(total_amount) + str(' - ') + str(self.related_bill.name),
                            'journal_id':self.carrier_id.journal_id.id,
                            'payment_method_id':self.env['account.payment.method'].search([('name','=','Manual')],limit=1).id,
                        })
                        if rec.so_id:
                            if not rec.so_id.invoice_ids:
                                invoice_lines = []
                                for line in rec.so_id.order_line:
                                    invoice_lines.append((0,0,line._prepare_invoice_line()))
                                invoice_vals = rec.so_id.sudo()._prepare_invoice()
                                invoice_vals.update({'invoice_line_ids':invoice_lines})
                                account_move = self.env['account.move'].sudo().create(invoice_vals)

                            for inv in rec.so_id.invoice_ids:
                                if inv.state != 'posted':
                                    inv.sudo().action_post()
                            payment_created.update({'invoice_ids':rec.so_id.invoice_ids.ids})
                            payment_created.post()
                            rec.related_payment = payment_created.id
                            rec.payment_created = True
                        elif rec.pos_order:
                            if rec.pos_order.account_move:
                                for inv in rec.pos_order.account_move:
                                    if inv.state != 'posted':
                                        inv.sudo().action_post()
                                payment_created.update({'invoice_ids': rec.pos_order.account_move.ids})
                            payment_created.post()
                            rec.related_payment = payment_created.id
                            rec.payment_created = True

                    shipping_price = rec.shipping_price
                    if shipping_price:
                        vend_payment_created = payment.sudo().create({
                            'payment_type': 'outbound',
                            'partner_id': self.shipping_company_id.id,
                            'partner_type': 'supplier',
                            'amount': shipping_price,
                            'communication': str(self.shipping_company_id.name) + str(' - ') + str(self.date) + str(' - ') + str(
                                total_amount) + str(' - ') + str(self.related_bill.name),
                            'journal_id': self.carrier_id.journal_id.id,
                            'payment_method_id': self.env['account.payment.method'].search([('name', '=', 'Manual')],
                                                                                           limit=1).id,
                        })

                        vend_payment_created.update({'invoice_ids':self.related_bill.ids})
                        vend_payment_created.post()

                        rec.related_payment_vend = vend_payment_created.id
                        rec.payment_created = True

    def close_button(self):
        for rec in self.order_ids.filtered(lambda x:x.line_state not in ['cancelled','delivered']):
            rec.line_state = 'cancelled'

class ShippingOrderLines(models.Model):
    _name = 'shipping.order.lines'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']


    external_ref = fields.Char(string='Reference',compute='compute_external_ref',store=True)

    @api.depends('delivery_id','delivery_id.external_id','delivery_id.invoice_no')
    def compute_external_ref(self):
        for rec in self:
            if rec.delivery_id.external_id:
                rec.external_ref = rec.delivery_id.external_id
            else:
                rec.external_ref = rec.delivery_id.invoice_no

    shipping_order_id = fields.Many2one(comodel_name="shipping.order", string="", required=False, )
    so_id = fields.Many2one(comodel_name="sale.order", string="Order No", required=False, )
    pos_order = fields.Many2one(comodel_name="pos.order", string="Pos No", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Cust.Name", required=False, )
    customer_mob_no = fields.Char(string="Cust.Mobile No", required=False, )
    customer_email = fields.Char(string="Cust.Email", required=False, )
    delivery_id = fields.Many2one(comodel_name="stock.picking", string="Delivery No", required=False, )
    delivery_state = fields.Char(string="Delivery Status", required=False, )
    route_id = fields.Many2one(comodel_name="res.country.state", string="Route", required=False, )
    shipping_price = fields.Float(string="Shipping Price",  required=False, )
    total_order_price = fields.Float(string="Total Order Price",  required=False, )
    payment_method_desc = fields.Char(string="Payment Method", required=False, )
    notes = fields.Text(string="Notes", required=False, )

    cash_receiving_state = fields.Selection(string="COD Payment", selection=[('collected', 'Collected'),('prepaid','Pre paid'), ('not_collected', 'Not Collected'), ], required=False,default="not_collected" )
    line_state = fields.Selection(string="Status", selection=[('order_received', 'Order Received'),('on_the_way','On The Way'),('arrived','Arrived'),('delivered','Delivered'),('rescheduled','Cancel & Rescheduled'),('cancelled','Cancelled & Returned')], required=False, )
    in_po = fields.Boolean(string="",  )
    rescheduled_date = fields.Date(string="Rescheduled Date", required=False,)
    related_payment = fields.Many2one(comodel_name="account.payment", string="Cust Payment", required=False, )
    related_payment_vend = fields.Many2one(comodel_name="account.payment", string="Vend Payment", required=False, )
    payment_created = fields.Boolean(string="",  )
    @api.onchange('delivery_id')
    @api.constrains('delivery_id')
    def _onchange_delivery_id(self):
        for rec in self:
            if rec.delivery_id.ship_price:
                self.shipping_price = rec.delivery_id.ship_price
    def rescheduled_date_button(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reschedule.shipping.line',
            'view_mode': 'form',
            'target': 'new',
            'context':{'default_shipping_line_id':self.id}
        }

    def cash_receiving_button(self):
        for rec in self:
            if rec.pos_order:
                if rec.pos_order.account_move:
                    bank_journal = self.env['account.journal'].search([('type','=','bank')],limit=1)

                    payment = self.env['account.payment'].create({'payment_type': 'inbound',
                                                                  'partner_type': 'customer',
                                                                  'partner_id': rec.pos_order.account_move.partner_id.id,
                                                                  'journal_id': bank_journal.id,
                                                                  'amount': rec.pos_order.account_move.amount_total,
                                                                  'payment_method_id': self.env.ref(
                                                                      'account.account_payment_method_manual_in').id})
                    payment.post()

                    aml2 = rec.pos_order.account_move.line_ids.filtered(lambda x:x.account_id.internal_type in ("receivable") )
                    aml3 = payment.move_line_ids.filtered(lambda x:x.account_id.internal_type in ("receivable") )
                    aml4 = aml3 + aml2
                    if len(aml4) > 1:
                        aml4.reconcile()
                        payment.write({'state': 'reconciled'})
            rec.cash_receiving_state = 'collected'
            # email_to = rec.customer_email
            # email_to_not = rec.partner_id.id
            # result = self.message_post(
            #     body='Your shipping order delivery ' + str(
            #         rec.delivery_id.name) + ' is in state ( ' + str(rec.line_state) + ' ) ' +' click here to open: <a target=_BLANK href="/web?#id=' + str(
            #         rec.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
            #         rec.shipping_order_id.name) + '</a>',
            #     subtype_xmlid='mail.mt_comment',
            #     partner_ids=[email_to_not])
            #
            # email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
            # ctx = self._context.copy()
            # ctx.update({'name': rec.partner_id.name})
            # # reminder_mail_template.with_context(ctx).send_mail(user)
            # if email_template_id:
            #     email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _('Your shipping order delivery: ') + str(rec.delivery_id.name) + _('is in state') + _(str(rec.line_state))})

    def order_received(self):
        for rec in self:
            rec.line_state ='order_received'
            email_to = rec.customer_email
            email_to_not = rec.partner_id.id

            if email_to_not:
                msg = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( Order Received ) ' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        rec.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
                        rec.shipping_order_id.name) + '</a>'
                result = self.message_post(
                    body= msg,
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[email_to_not])
                self.send_message_on_whatsapp(msg, email_to_not)

            if email_to:
                email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
                ctx = self._context.copy()
                ctx.update({'name': rec.partner_id.name})
                # reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _(
                        'Your shipping order delivery: ') + str(rec.delivery_id.name) + _('is in state ( Order Received )')})


    def on_the_way(self):
        for rec in self:
            rec.line_state ='on_the_way'
            email_to = rec.customer_email
            email_to_not = rec.partner_id.id

            if email_to_not:
                msg = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( On The Way ) ' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        rec.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
                        rec.shipping_order_id.name) + '</a>'
                msg_whatsapp = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( On The Way )'
                result = self.message_post(
                    body= msg,
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[email_to_not])
                rec.send_message_on_whatsapp(msg_whatsapp, email_to_not)
            if email_to:
                email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
                ctx = self._context.copy()
                ctx.update({'name': rec.partner_id.name})
                # reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _(
                        'Your shipping order delivery: ') + str(rec.delivery_id.name) + _(
                        'is in state ( On The Way )')})

    def arrived(self):
        for rec in self:
            rec.line_state ='arrived'
            email_to = rec.customer_email
            email_to_not = rec.partner_id.id

            if email_to_not:
                msg = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( Arrived ) ' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        rec.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
                        rec.shipping_order_id.name) + '</a>'
                msg_whatsapp = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( Arrived ) '
                result = self.message_post(
                    body= msg,
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[email_to_not])

                rec.send_message_on_whatsapp(msg_whatsapp, email_to_not)
            if email_to:
                email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
                ctx = self._context.copy()
                ctx.update({'name': rec.partner_id.name})
                # reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _(
                        'Your shipping order delivery: ') + str(rec.delivery_id.name) + _(
                        'is in state ( Arrived )')})

    def delivered(self):
        for line in self:
            line.line_state ='delivered'
            email_to = line.customer_email
            email_to_not = line.partner_id.id

            if email_to_not:
                msg = 'Your shipping order delivery ' + str(
                        line.delivery_id.name) + ' is in state ( Delivered ) ' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        line.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
                        line.shipping_order_id.name) + '</a>'
                msg_whatsapp = 'Your shipping order delivery ' + str(
                        line.delivery_id.name) + ' is in state ( Delivered ) '
                result = self.message_post(
                    body= msg,
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[email_to_not])
                line.send_message_on_whatsapp(msg_whatsapp, email_to_not)
            if email_to:
                email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
                ctx = self._context.copy()
                ctx.update({'name': line.partner_id.name})
                # reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _(
                        'Your shipping order delivery: ') + str(line.delivery_id.name) + _(
                        'is in state ( Delivered )')})

            if not line.in_po and line.shipping_order_id.related_bill:
                shipping_order_lines = []
                shipping_order_lines.append((0, 0, {
                    'product_id': line.delivery_id.carrier_id.product_id.id,
                    'name': "%s - %s - %s - %s - %s" % (
                        line.so_id.name,
                        line.partner_id.name,
                        line.delivery_id.name,
                        line.delivery_id.city_route_id.name, line.shipping_price),
                    'product_qty': 1,
                    'product_uom': line.delivery_id.carrier_id.product_id.uom_po_id.id,
                    'price_unit': line.shipping_price,
                    'date_planned': fields.Datetime.now(),
                }))
                line.shipping_order_id.related_po.update({'order_line':shipping_order_lines})
                line.in_po = True


    def cancelled(self):
        for rec in self:

            if rec.in_po:
                raise exceptions.ValidationError('You can not cancel shipping line created on purchase order')
            rec.line_state ='cancelled'
            email_to = rec.customer_email
            email_to_not = rec.partner_id.id
            if email_to_not:
                msg = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( Cancelled ) ' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                        rec.shipping_order_id.id) + '&view_type=form&model=shipping.order&action=" style="font-weight: bold">' + str(
                        rec.shipping_order_id.name) + '</a>'
                msg_whatsapp = 'Your shipping order delivery ' + str(
                        rec.delivery_id.name) + ' is in state ( Cancelled ) '
                result = self.message_post(
                    body= msg,
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[email_to_not])
                rec.send_message_on_whatsapp(msg_whatsapp, email_to_not)
            if email_to:
                email_template_id = self.env.ref('sale_delivery_extend.email_template_shipping_order')
                ctx = self._context.copy()
                ctx.update({'name': rec.partner_id.name})
                # reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.shipping_order_id.id, email_values={'email_to': email_to, 'subject': _(
                        'Your shipping order delivery: ') + str(rec.delivery_id.name) + _(
                        'is in state ( Cancelled )')})

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def convert_to_html(self, message):
        for data in re.findall(r'\*.*?\*', message):
            message = message.replace(data, "<strong>" + data.strip('*') + "</strong>")
        return message

    def send_message_on_whatsapp(self, msg, partner_id):
        Param = self.env['res.config.settings'].sudo().get_values()
        res_partner_id = self.env['res.partner'].search([('id', '=', partner_id)])
        res_user_id = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_partner_id.mobile:
            if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                msg = msg
                whatsapp_msg_number = res_partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                    '+' + str(res_partner_id.country_id.phone_code), "")
                phone_exists_url = Param.get('whatsapp_endpoint') + '/checkPhone?token=' + Param.get(
                    'whatsapp_token') + '&phone=' + str(
                    res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                phone_exists_response = requests.get(phone_exists_url)
                json_response_phone_exists = json.loads(phone_exists_response.text)

                if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                        json_response_phone_exists['result'] == 'exists':
                    # if self.project_id.name:
                    #     msg += "*" + _("Project") + ":* "+self.project_id.name
                    # if self.name:
                    #     msg += "\n*" + _("Task name") + ":* "+self.name
                    # if self.date_deadline:
                    #     msg+= "\n*" + _("Deadline") + ":* "+str(self.date_deadline)
                    # if self.description:
                    #     if len(self.description) > 11:
                    #         msg += "\n*" + _("Description") + ":* "+self.cleanhtml(self.description)
                    msg = _("Hello") + " " + res_partner_id.name + ", " + msg
                    # if res_user_id.has_group('pragmatic_odoo_whatsapp_integration.group_project_enable_signature'):
                    #     user_signature = self.cleanhtml(res_user_id.signature)
                    #     msg += "\n\n" + user_signature
                    url = Param.get('whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    tmp_dict = {"phone": "+" + str(
                        res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code, "body": msg}
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        print("Send Message successfully")
                        response_dict = response.json()
                        # self.whatsapp_msg_id = response_dict.get('id')
                        # mail_message_obj = self.env['mail.message']
                        # comment = "fa fa-whatsapp"
                        # body_html = tools.append_content_to_html('<div class = "%s"></div>' % tools.ustr(comment), msg)
                        # body_msg = self.convert_to_html(body_html)
                        # if self.env['ir.config_parameter'].sudo().get_param('pragmatic_odoo_whatsapp_integration.group_project_display_chatter_message'):
                        #     mail_message_id = mail_message_obj.sudo().create({
                        #         'res_id': self.id,
                        #         'model': 'project.task',
                        #         'body': body_msg,
                        #     })
                else:
                    raise Warning('Please add valid whatsapp number for %s ' % res_partner_id.name)


class ReschedulShiipingLine(models.Model):
    _name = 'reschedule.shipping.line'

    date = fields.Date(string="Reschedule Date", required=True, )
    shipping_line_id = fields.Many2one(comodel_name="shipping.order.lines", string="", required=False, )

    def action_confirm(self):
        shipping_order = self.env['shipping.order']
        active_id = self.env.context.get('active_id')
        shipping_orders = self.shipping_line_id.shipping_order_id
        if shipping_orders:
            # shipping_orders = shipping_order.browse(active_id)
            ship_order_line = []
            if shipping_orders:
                for rec in shipping_orders.order_ids.filtered(lambda x:x.id == self.shipping_line_id.id):
                    rec.rescheduled_date = self.date
                    ship_order_line.append((0,0,{
                        'so_id':rec.so_id.id,
                        'pos_order':rec.pos_order.id,
                        'partner_id':rec.partner_id.id,
                        'customer_mob_no':rec.customer_mob_no,
                        'customer_email':rec.customer_email,
                        'delivery_id':rec.delivery_id.id,
                        'delivery_state':rec.delivery_state,
                        'route_id':rec.route_id.id,
                        'shipping_price':rec.shipping_price,
                        'total_order_price':rec.total_order_price,
                        'payment_method_desc':rec.payment_method_desc,
                        'notes':rec.notes,
                        # 'cash_receiving_state':rec.cash_receiving_state,
                    }))

                shipping_order_created_before = shipping_order.search([('date','=',self.date),('shipping_company_id','=',shipping_orders.shipping_company_id.id),('state','!=','completed')])
                if shipping_order_created_before:
                    for rec in shipping_order_created_before:
                        rec.update({'order_ids':ship_order_line})
                else:
                    shipping_order.create({
                        'shipping_company_id':shipping_orders.shipping_company_id.id,
                        'date':self.date,
                        'carrier_id':shipping_orders.carrier_id.id,
                        'notes':shipping_orders.notes,
                        'order_ids':ship_order_line,
                    })






