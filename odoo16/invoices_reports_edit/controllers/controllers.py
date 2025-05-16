# -*- coding: utf-8 -*-
from odoo import http

# class InvoicesReportsEdit(http.Controller):
#     @http.route('/invoices_reports_edit/invoices_reports_edit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoices_reports_edit/invoices_reports_edit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoices_reports_edit.listing', {
#             'root': '/invoices_reports_edit/invoices_reports_edit',
#             'objects': http.request.env['invoices_reports_edit.invoices_reports_edit'].search([]),
#         })

#     @http.route('/invoices_reports_edit/invoices_reports_edit/objects/<model("invoices_reports_edit.invoices_reports_edit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoices_reports_edit.object', {
#             'object': obj
#         })