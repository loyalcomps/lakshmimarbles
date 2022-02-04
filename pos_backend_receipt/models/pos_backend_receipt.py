# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    ip_address = fields.Char(string='IP address')


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def get_user_ip_address(self):
        ip_address = False
        if self._uid:
            ip_address = self.env['res.users'].browse(
                                  self._uid).ip_address or False
        return ip_address

    @api.model
    def get_all_orders_data(self, ids):
        dict_booking_appointment = {}
        booking_obj = self.env['pos.booking']
        for booking in booking_obj.browse([ids]):
            if booking.customer_id:
                booking_line_list = []
                for booking_line in booking.service_lines:
                    line_dict = {
                         'product_name': booking_line.product_id.name or '',
                         'quantity': booking_line.qty or 0.0,
                         'price': booking_line.price_unit or 0.0,
                         'discount': booking_line.discount or 0.0,
                         'price_subtotal': booking_line.price_subtotal or 0.0,
                         'price_subtotal_incl':
                         booking_line.price_subtotal_incl or 0.0
                    }
                    booking_line_list.append(line_dict)

                customer_details = {
                    'customer_name': booking.customer_id.name or '',
                    'phone': booking.customer_id.phone or '',
                    'street': booking.customer_id.street or '',
                    'street2': booking.customer_id.street2 or '',
                    'city': booking.customer_id.city or '',
                    'zip': booking.customer_id.zip or ''
                }
                dict_booking_appointment.update({
                    'booking_number': booking.booking_no,
                    'customer_details': customer_details,
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                    'booking_lines': booking_line_list
                })
        return [dict_booking_appointment, self.get_user_ip_address()]
