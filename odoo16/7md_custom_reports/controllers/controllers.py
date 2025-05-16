# -*- coding: utf-8 -*-
from odoo import http

# class 7mdCustomReports(http.Controller):
#     @http.route('/7md_custom_reports/7md_custom_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/7md_custom_reports/7md_custom_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('7md_custom_reports.listing', {
#             'root': '/7md_custom_reports/7md_custom_reports',
#             'objects': http.request.env['7md_custom_reports.7md_custom_reports'].search([]),
#         })

#     @http.route('/7md_custom_reports/7md_custom_reports/objects/<model("7md_custom_reports.7md_custom_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('7md_custom_reports.object', {
#             'object': obj
#         })