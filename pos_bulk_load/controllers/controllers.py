# -*- coding: utf-8 -*
from odoo.http import request
from odoo.addons.bus.controllers.main import BusController
from odoo import api, http, SUPERUSER_ID
from odoo.addons.web.controllers.main import ensure_db, Home, Session, WebClient
import json
import logging
import base64

_logger = logging.getLogger(__name__)

# class web_login(Home):
    # @http.route()
    # def web_login(self, *args, **kw):
    #     ensure_db()
    #     response = super(web_login, self).web_login(*args, **kw)
    #     if request.session.uid:
    #         user = request.env['res.users'].browse(request.session.uid)
    #         pos_config = user.pos_config_id
    #         if pos_config:
    #             return http.local_redirect('/pos/web/')
    #     return response

#
class pos_bus(BusController):
    def _poll(self, dbname, channels, last, options):
        channels = list(channels)
        # channels.append((request.db, 'account.invoice', request.uid))
        # channels.append((request.db, 'pos.order', request.uid))
        # channels.append((request.db, 'pos.order.line', request.uid))
        channels.append((request.db, 'pos.sync.data', request.uid))
        # channels.append((request.db, 'pos.stock.update', request.uid))
        channels.append((request.db, 'pos.bus', request.uid))
        return super(pos_bus, self)._poll(dbname, channels, last, options)

    # @http.route('/pos/update_order/status', type="json", auth="public")
    # def bus_update_sale_order(self, status, order_name):
    #     sales = request.env["sale.order"].sudo().search([('name', '=', order_name)])
    #     sales.write({'sync_status': status})
    #     return 1

    @http.route('/pos/sync', type="json", auth="public")
    def send(self, bus_id, messages):
        for message in messages:
            _logger.info('{syncing} %s' % message['value']['action'])
            user_send = request.env['res.users'].sudo().browse(message['user_send_id'])
            sessions = request.env['pos.session'].sudo().search([
                ('state', '=', 'opened'),
                ('user_id', '!=', user_send.id)
            ])
            send = 0
            if message['value']['action'] == 'paid_order':
                request.env['pos.bus.log'].search([
                    ('order_uid', '=', message['value']['order_uid']),
                    ('action', '=', 'unlink_order')
                ]).write({
                    'state': 'done',
                    'action': 'paid_order'

                })
            if message['value']['action'] == 'unlink_order':
                request.env['pos.bus.log'].search([
                    ('order_uid', '=', message['value']['order_uid'])
                ]).write({
                    'state': 'done'
                })
                request.env['pos.bus.log'].create({
                    'user_id': message['user_send_id'],
                    'action': message['value']['action'],
                    'order_uid': message['value']['order_uid'],
                    'log': base64.encodestring(json.dumps(message).encode('utf-8')),
                    'bus_id': bus_id,
                    'state': 'done'
                })
            if message['value']['action'] not in ['unlink_order', 'paid_order']:
                request.env['pos.bus.log'].create({
                    'user_id': message['user_send_id'],
                    'action': message['value']['action'],
                    'order_uid': message['value']['order_uid'],
                    'log': base64.encodestring(json.dumps(message).encode('utf-8')),
                    'bus_id': bus_id,
                })
            for session in sessions:
                if session.config_id.bus_id and session.config_id.bus_id.id == message['value'][
                    'bus_id'] and user_send.id != session.user_id.id:
                    _logger.info('{0}'.format('{syncing} from %s to %s') % (user_send.login, session.user_id.login))
                    send += 1
                    request.env['bus.bus'].sendmany(
                        [[(request.env.cr.dbname, 'pos.bus', session.user_id.id), json.dumps(message)]])
            if send == 0:
                _logger.info('Empty clients online for sync')
        return json.dumps({
            'status': 'OK',
            'code': 200
        })
