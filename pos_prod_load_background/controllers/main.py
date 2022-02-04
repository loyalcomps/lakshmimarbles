# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import simplejson

from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class DataSet(http.Controller):

    @http.route('/web/dataset/load_products', type='http', auth="user")
    def load_products(self, **kw):
        domain = str(kw.get('domain'))
        domain = domain.replace('true', 'True')
        domain = domain.replace('false', 'False')
        domain = eval(domain)
        temp = int(kw.get('product_limit')) - 1000
        domain += [('id','<=',kw.get('product_limit')),('id','>=',temp)]

        ctx1 = str(kw.get('context'))
        ctx1 = ctx1.replace('true', 'True')
        ctx1 = ctx1.replace('false', 'False')
        ctx1 = eval(ctx1)
        records = []
        fields = eval(kw.get('fields'))
        cr, uid, context = request.cr, request.uid, request.context
        Model = kw.get('model')
        context = dict(context)
        context.update(ctx1)
        try:
            records = request.env[Model].with_context(context).search_read(domain, fields, limit=1000)
        except Exception, e:
            _logger.error('Error .... %s',e)
        return simplejson.dumps(records)

    @http.route('/web/dataset/load_customers', type='http', auth="user")
    def load_customers(self, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        records = []
        fields = [];
        domain = [('customer', '=', True)];
        Model = kw.get('model')
        try:
            records = request.env[Model].search_read(domain)
        except Exception, e:
            print "\n Error......", e
        return simplejson.dumps(records)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
