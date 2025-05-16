# -*- coding: utf-8 -*-
# from odoo import http


# class CustomFinancialReport(http.Controller):
#     @http.route('/custom_financial_report/custom_financial_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_financial_report/custom_financial_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_financial_report.listing', {
#             'root': '/custom_financial_report/custom_financial_report',
#             'objects': http.request.env['custom_financial_report.custom_financial_report'].search([]),
#         })

#     @http.route('/custom_financial_report/custom_financial_report/objects/<model("custom_financial_report.custom_financial_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_financial_report.object', {
#             'object': obj
#         })
