# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import xlrd
from datetime import datetime
from dateutil import parser
from odoo.tests import Form, tagged
import pytz

utc = pytz.utc
import logging

_logger = logging.getLogger(__name__)


class ExcelReport(models.Model):
    _name = 'excel.report'

    xls_file = fields.Binary('file')
    report_for = fields.Selection(
        [('payment', 'Pos Payment')])

    def import_xls(self):
        main_list = []
        wb = xlrd.open_workbook(file_contents=base64.b64decode(self.xls_file))
        if self.report_for == "payment":
            for sheet in wb.sheets():
                for row in range(1, sheet.nrows):
                    list = []
                    for col in range(sheet.ncols):
                        if col == 0:  # Convert date from serial number to datetime
                            date_value = xlrd.xldate_as_datetime(sheet.cell(row, col).value, wb.datemode)
                            list.append(date_value)
                        else:
                            list.append(sheet.cell(row, col).value)
                    main_list.append(list)
            i = 0
            for inner_list in main_list:
                try:
                    date = inner_list[0]
                    payment_method = self.env['pos.payment.method'].search(
                        [('name', '=', inner_list[3])], limit=1)
                    config_id = self.env['pos.config'].search([('id', '=', inner_list[1])])
                    partner_id = self.env['res.partner'].search([('id', '=', int(inner_list[5]))])
                    order_id = self.env['pos.order'].search([('config_id', '=', config_id.id),('name', '=', inner_list[2])])

                    pos_payment = self.env['pos.payment'].search([('payment_date', '=', date)])
                    if order_id and not order_id.payment_ids:
                        new_payment_data = {
                            'payment_date': date,
                            'create_date': date,
                            'amount': inner_list[4],
                            'pos_order_id': order_id.id,
                            'payment_method_id': payment_method.id,
                            'partner_id': partner_id.id,
                            'session_id': order_id.session_id.id,
                        }
                        print("conf name is :", config_id.name)
                        print("payment method is :", pos_payment.name)
                        print("order  is :", order_id.name)
                        print("session  is :", order_id.session_id.name)
                        pos_payment = self.env['pos.payment'].create(new_payment_data)
                        _logger.info("PAyment : %s ", pos_payment.id)
                        i += 1
                        if (int(i % 10) == 0):
                            print("Record created_________________" + str(i) + "\n")
                except(Exception) as error:
                    print('Error occur at %s and error is %s' % (str(inner_list[2]), error))












        elif self.report_for == "invoice":
            for sheet in wb.sheets():
                for row in range(1, sheet.nrows):
                    list = []
                    for col in range(sheet.ncols):
                        list.append(sheet.cell(row, col).value)
                    main_list.append(list)
            i = 0
            for inner_list in main_list:
                try:
                    sale_order = self.env['sale.order'].search([('name', '=', str(inner_list[0]).split('.')[0])])
                    if sale_order and sale_order.state == 'draft':
                        sale_order.action_confirm()
                        context = {
                            "active_model": 'sale.order',
                            "active_ids": sale_order.id,
                        }
                        payment = self.env['sale.advance.payment.inv'].create({
                            'advance_payment_method': 'delivered',
                        })
                        action_invoice = payment.with_context(context).create_invoices()

                        invoices = self.env['account.move'].search([('invoice_origin', '=', sale_order.name)])
                        if invoices:
                            for invo in invoices:
                                # invo.invoice_line_ids.unlink()

                                invo.write({
                                    "name": str(inner_list[1]).split('.')[0],
                                })
                                # if inner_list[2]:
                                #     varient_sku = self.env['product.product'].search([('default_code', '=', inner_list[2])], limit=1)
                                #     if not varient_sku:
                                #         pass
                                #     if varient_sku:
                                #         for i in invo.invoice_line_ids:
                                #             invoice_line = i.write({
                                #                 "name": varient_sku.name,
                                #                 "product_id": varient_sku.id,
                                #                 "quantity": float(inner_list[7]),
                                #                 "product_uom_id": varient_sku.uom_id.id,
                                #                 "price_unit": varient_sku.list_price,
                                #                 'move_id': invo.id,
                                #                 'discount': 0 if inner_list[9] == '' else float(inner_list[9]),
                                #             })
                                #
                                #
                                #     else:
                                #         shipment = self.env['product.product'].search([('name', '=', "shippment")])
                                #         for i in invo.invoice_line_ids:
                                #             invoice_line = i.write({
                                #                 "name": "shippment",
                                #                 "product_id": shipment.id,
                                #                 "product_uom_id": shipment.uom_id.id,
                                #                 "price_unit": shipment.list_price,
                                #                 'move_id': invo.id,
                                #                 'discount': 0 if inner_list[9] == '' else float(inner_list[9]),
                                #
                                #             })

                        i += 1
                        if (int(i % 500) == 0):
                            print("Record created_________________" + str(i) + "\n")

                    # if sale_order and sale_order.state == 'sale':
                    #     context = {
                    #         "active_model": 'sale.order',
                    #         "active_ids": sale_order.id,
                    #     }
                    #     payment = self.env['sale.advance.payment.inv'].create({
                    #         'advance_payment_method': 'delivered',
                    #     })
                    #     action_invoice = payment.with_context(context).create_invoices()
                    #
                    #     invoices = self.env['account.move'].search([('invoice_origin', '=', sale_order.name)])
                    #     if invoices:
                    #         for invo in invoices:
                    #
                    #             # invo.invoice_line_ids.unlink()
                    #
                    #             invo.write({
                    #                 "name": str(inner_list[1]).split('.')[0],
                    #             })
                    #             if inner_list[2]:
                    #                 varient_sku = self.env['product.product'].search(
                    #                     [('default_code', '=', inner_list[2])], limit=1)
                    #                 if not varient_sku:
                    #                     pass
                    #                 # if varient_sku:
                    #                 #     for i in invo.invoice_line_ids:
                    #                 #         invoice_line = i.write({
                    #                 #             "name": varient_sku.name,
                    #                 #             "product_id": varient_sku.id,
                    #                 #             "quantity": float(inner_list[7]),
                    #                 #             "product_uom_id": varient_sku.uom_id.id,
                    #                 #             "price_unit": varient_sku.list_price,
                    #                 #             'move_id': invo.id,
                    #                 #             'discount': 0 if inner_list[9] == '' else float(inner_list[9]),
                    #                 #         })
                    #
                    #
                    #                 else:
                    #                     shipment = self.env['product.product'].search([('name', '=', "shippment")])
                    #                     # for i in invo.invoice_line_ids:
                    #                     #     invoice_line = i.write({
                    #                     #         "name": "shippment",
                    #                     #         "product_id": shipment.id,
                    #                     #         "product_uom_id": shipment.uom_id.id,
                    #                     #         "price_unit": shipment.list_price,
                    #                     #         'move_id': invo.id,
                    #                     #         'discount': 0 if inner_list[9] == '' else float(inner_list[9]),
                    #                     #
                    #                     #     })
                    #
                    #     i += 1
                    #     if (int(i % 500) == 0):
                    #         print("Record created_________________" + str(i) + "\n")

                    i += 1
                    if (int(i % 500) == 0):
                        print("Record created_________________" + str(i) + "\n")

                except(Exception) as error:
                    print('Error occur at %s' % (str(inner_list[0])))

    def create_variants_by_attribute(self, p_template_id, attribute_id, attribute_value):
        att_id = False
        all_atts = []

        for att_value in attribute_id.value_ids:
            if att_value.name == attribute_value:
                att_id = att_value
                break

        if not att_id:
            att_id = self.env['product.attribute.value'].create({
                'name': attribute_value,
                'attribute_id': attribute_id.id,
            })

        all_atts.append(att_id.id)

        if p_template_id.attribute_line_ids:
            for att_line in p_template_id.attribute_line_ids:
                if att_line.attribute_id == attribute_id:
                    all_atts = all_atts + att_line.value_ids.ids
                    att_line.update({
                        'value_ids': [(6, 0, all_atts)],
                    })
                    return

        else:
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': p_template_id.id,
                'attribute_id': attribute_id.id,
                'value_ids': [(6, 0, all_atts)],
            })
            return

        self.env['product.template.attribute.line'].create({
            'product_tmpl_id': p_template_id.id,
            'attribute_id': attribute_id.id,
            'value_ids': [(6, 0, all_atts)],
        })
