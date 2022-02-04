from odoo import models, fields, api


class Payment_saction(models.Model):
    _inherit='account.payment'

    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    pos_counter_ids = fields.Many2one('pos.session', string="Session",store=True, domain="[('state','=','opened'),('user_id','=',user_id)]")

class Payment_soinvoice(models.Model):
    _inherit='account.invoice'

    pos_config_ids = fields.Many2one('pos.config', string="Counter",store=True)
