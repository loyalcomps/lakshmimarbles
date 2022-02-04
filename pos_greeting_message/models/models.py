# -*- coding: utf-8 -*-

from odoo import models, fields, api


class posSetting(models.TransientModel):
    _inherit = 'pos.config.settings'

    greetings_id = fields.Boolean(default=False)

    @api.model
    def get_default_gift_amount(self,fields):
        greetings_id = self.env["ir.config_parameter"].get_param("pos_greeting_message.greetings_id")
        return {'greetings_id': greetings_id}

    @api.multi
    def set_gift_amount(self):
        self.env["ir.config_parameter"].set_param("pos_greeting_message.greetings_id", self.greetings_id)
        posConf = self.env["pos.config"].search([])
        for pos in posConf:
            pos.update({'greetings_bool': self.greetings_id})







        # @api.one
    # def set_age_values(self):
    #     conf = self.env['ir.config_parameter']
    #     conf.set_param('pos_greeting_message.greetings_id')

    #

    # @api.multi
    # def set_greetingmessage(self):
    #     ir_values_obj =  self.env["ir.config_parameter"]
    #
    #     ir_values_obj.sudo().set_param('pos.config.settings', 'greetings_id',self.greetings_id)

class posconfig(models.Model):
    _inherit = 'pos.config'

    greetings_active_char = fields.Text(string="Greeting Message",)




    # def get_greeting_active(self):
    #     # debt_limit = self.env["ir.config_parameter"].get_param("pos_debt_notebook.debt_limit", default=0)
    #     ir_values = self.env["ir.config_parameter"]
    #     for i in self:
    #         i.greetings_active = ir_values.get_param('pos.config.settings', 'greetings_bool')

    @api.model
    def get_default_age_values(self):
        conf = self.env['ir.config_parameter']
        return {
            'greetings_bool': (conf.get_param('pos_greeting_message.greetings_id')),
        }

    #

    greetings_bool = fields.Boolean(string="Greeting",default=get_default_age_values)






