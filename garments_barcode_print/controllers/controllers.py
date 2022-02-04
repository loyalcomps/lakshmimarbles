# -*- coding: utf-8 -*-
from odoo import http

# class GarmentBarcodeSettings(http.Controller):
#     @http.route('/garment_barcode_settings/garment_barcode_settings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/garment_barcode_settings/garment_barcode_settings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('garment_barcode_settings.listing', {
#             'root': '/garment_barcode_settings/garment_barcode_settings',
#             'objects': http.request.env['garment_barcode_settings.garment_barcode_settings'].search([]),
#         })

#     @http.route('/garment_barcode_settings/garment_barcode_settings/objects/<model("garment_barcode_settings.garment_barcode_settings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('garment_barcode_settings.object', {
#             'object': obj
#         })