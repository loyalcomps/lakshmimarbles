from odoo import models, fields, api, _
import os.path

import base64


class ProductPrices(models.TransientModel):
    _name = 'product.price'

    # name = fields.Many2one('product.template', string="Product")
    product_id = fields.Many2one('product.product', string="Product")
    sale_price = fields.Integer(string="Sale Price")
    is_export = fields.Boolean(string='Export')
    to_weight = fields.Boolean(related='product_id.to_weight',string='To Weigh With Scale',
                               help="Check if the product should be weighted using the hardware scale integration")
    # cost_price = fields.Integer(string="Cost Price", required=True)

    @api.multi
    def change_product_price(self):
        prod_obj = self.env['product.product'].browse(self.product_id.id)
        # prod_value = {'list_price': self.sale_price, 'standard_price': self.cost_price}
        prod_value = {'list_price': self.sale_price}
        obj = prod_obj.write(prod_value)
        return obj

    @api.onchange('product_id')
    def get_price(self):
        prod_obj = self.env['product.product'].browse(self.product_id.id)
        self.sale_price = prod_obj.list_price
        # self.cost_price = prod_obj.standard_price

    @api.multi
    def text_export(self):
        prod_obj = self.env['product.product'].search([('to_weight', '=', True)])
        file_pro = ''
        if prod_obj:
            for pro in prod_obj:
                no = '2' if pro.is_piece else '1'

                file_pro += str(pro.plu) + ',' + str(pro.barcode) + ',' + str(pro.name) + ',' + str(pro.lst_price) + ',' + str(no) + '\r\n'


        filename = '10,1001,Apple,250.00,1'

        filename += '\r\n'

        filename = filename + '4,1002,Orange,50.00,1'

        filename += '\r\n'

        filename = filename + '3,1003,grape,50.00,1'

        filename += '\r\n'

        filename = filename + '7,1013,Carrot,60.00,1'


        values = {

            'name': "Name of text file.txt",

            'datas_fname': 'plu.txt',

            'res_model': 'ir.ui.view',

            'res_id': False,

            'type': 'binary',

            'public': True,

            # 'datas': filename.encode('utf8').encode('base64'),
            #'datas': base64.b64encode(filename),
            'datas': base64.b64encode(file_pro),

        }

        # Using your data create as attachment.

        attachment_id = self.env['ir.attachment'].sudo().create(values)

        # Prepare your download URL download_url = '/web/content/' + str(attachment_id.id) + '?download=True'


        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        # download_url = '/web/content/' + str(file) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url.freeze')

        # Return so it will download in your system return {
        return {

            "type": "ir.actions.act_url",

            "url": str(base_url) + str(download_url),

            "target": "new",

        }

    @api.multi
    def text_export_essai(self):
        prod_obj = self.env['product.product'].search([('to_weight', '=', True)])
        file_pro = ''
        if prod_obj:
            for pro in prod_obj:
                no = '1' if pro.is_piece else '2'
                product_code = 'W' + no + str(pro.barcode)

                file_pro += str(pro.plu) + ',' + str(product_code) + ',' + str(pro.name) + ',' + str(
                    pro.lst_price) + ','+ str(no)+'\r\n'

        filename = '10,1001,Apple,250.00,1'

        filename += '\r\n'

        filename = filename + '4,1002,Orange,50.00,1'

        filename += '\r\n'

        filename = filename + '3,1003,grape,50.00,1'

        filename += '\r\n'

        filename = filename + '7,1013,Carrot,60.00,1'

        values = {

            'name': "Name of text file.txt",

            'datas_fname': 'plu.txt',

            'res_model': 'ir.ui.view',

            'res_id': False,

            'type': 'binary',

            'public': True,

            # 'datas': filename.encode('utf8').encode('base64'),
            # 'datas': base64.b64encode(filename),
            'datas': base64.b64encode(file_pro),

        }

        # Using your data create as attachment.

        attachment_id = self.env['ir.attachment'].sudo().create(values)

        # Prepare your download URL download_url = '/web/content/' + str(attachment_id.id) + '?download=True'

        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        # download_url = '/web/content/' + str(file) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url.freeze')

        # Return so it will download in your system return {
        return {

            "type": "ir.actions.act_url",

            "url": str(base_url) + str(download_url),

            "target": "new",

        }

    @api.multi
    def text_export_new(self):
        prod_obj = self.env['product.product'].search([('to_weight', '=', True)])
        file_pro = ''
        if prod_obj:
            for pro in prod_obj:
                no = '2' if pro.is_piece else '1'

                file_pro += str(pro.plu) + ',' + str(pro.barcode) + ',' + str(pro.name) + ',' + str(
                    pro.lst_price) + ',' + str(no) + '\r\n'

        filename = '10,1001,Apple,250.00,1'

        filename += '\r\n'

        filename = filename + '4,1002,Orange,50.00,1'

        filename += '\r\n'

        filename = filename + '3,1003,grape,50.00,1'

        filename += '\r\n'

        filename = filename + '7,1013,Carrot,60.00,1'

        values = {

            'name': "Name of text file.txt",

            'datas_fname': 'plu.txt',

            'res_model': 'ir.ui.view',

            'res_id': False,

            'type': 'binary',

            'public': True,

            # 'datas': filename.encode('utf8').encode('base64'),
            # 'datas': base64.b64encode(filename),
            'datas': base64.b64encode(file_pro),

        }

        # Using your data create as attachment.

        attachment_id = self.env['ir.attachment'].sudo().create(values)

        # Prepare your download URL download_url = '/web/content/' + str(attachment_id.id) + '?download=True'

        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        # download_url = '/web/content/' + str(file) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url.freeze')

        # Return so it will download in your system return {
        return {

            "type": "ir.actions.act_url",

            "url": str(base_url) + str(download_url),

            "target": "new",

        }

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    plu = fields.Char(string='PLU',related='product_variant_ids.plu')
    is_piece = fields.Boolean(string='Is Piece',related='product_variant_ids.is_piece')



    @api.model
    def create(self, vals):
        product_template_id = super(ProductTemplate, self).create(vals)
        related_vals = {}
        if vals.get('plu'):
            related_vals['plu'] = vals['plu']

        if related_vals:
            product_template_id.write(related_vals)

        return product_template_id


class ProductProduct(models.Model):
    _inherit = 'product.product'

    plu = fields.Char(string='PLU')
    is_piece = fields.Boolean(string='Piece',default=False)

    _sql_constraints = [
        ('plu_uniq', 'unique(plu)', _("A plu can only be assigned to one product !")),
    ]
