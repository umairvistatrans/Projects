# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseScript(http.Controller):
#     @http.route('/purchase_script/purchase_script', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_script/purchase_script/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_script.listing', {
#             'root': '/purchase_script/purchase_script',
#             'objects': http.request.env['purchase_script.purchase_script'].search([]),
#         })

#     @http.route('/purchase_script/purchase_script/objects/<model("purchase_script.purchase_script"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_script.object', {
#             'object': obj
#         })
