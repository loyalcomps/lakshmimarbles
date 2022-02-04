#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import wizard
import models
from odoo import api, SUPERUSER_ID

def pre_init_check(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ir_module_obj = env['ir.module.module'].search([("name","=","l10n_in_gst"),("state","=","installed")])
    if ir_module_obj:raise Warning('The l10n_in_gst module is already present inside your Odoo addons. Kindly contact our support team "https://webkul.uvdesk.com/en/customer/create-ticket/" to get the compatible module')
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='10.0':raise Warning('Module support Odoo series 10.0 found {}.'.format(server_serie))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
