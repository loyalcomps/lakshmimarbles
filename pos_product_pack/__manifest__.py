# -*- coding: utf-8 -*-
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
{
  "name"                 :  "POS Product Pack",
  "summary"              :  "POS Product pack allow us to sale products in pack.",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Product-Pack.html",
  "description"          :  """https://webkul.com/blog/point-of-sale-product-pack""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_product_pack&version=10.0",
  "depends"              :  [
                             'point_of_sale',
                             'wk_product_pack',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/pos_product_pack.xml',
                            ],
  "qweb"                 :  ['static/src/xml/pos_product_pack.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  27,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}