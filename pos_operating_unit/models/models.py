# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    # @api.model
    # def _default_operating_unit(self):
    #     user = self.env['res.users'].search([('id','=',self.user_id.id)])
    #     return user.default_operating_unit_id

    @api.model
    def create(self, values):
        res = super(PosSession, self).create(values)
        user = self.env['res.users'].search([('id','=',values['user_id'])])
        res.update({'operating_unit_id':user.default_operating_unit_id})

        return res




    operating_unit_id = fields.Many2one(
        'operating.unit', string='Branch',

        readonly=True,
        # default = _default_operating_unit,
        # default=lambda self:
        # self.env['res.users'].
        #     operating_unit_default_get(self._uid)
        )
class PosOrder(models.Model):
    _inherit = 'pos.order'

    operating_unit_id = fields.Many2one(
        'operating.unit', string='Branch',related = 'session_id.operating_unit_id'

        )

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    operating_unit_id = fields.Many2one(
        'operating.unit', string='Branch',

       related='order_id.operating_unit_id')

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    operating_unit_id = fields.Many2one(
        'operating.unit', string='Branch',

        related='pos_statement_id.operating_unit_id')

    @api.multi
    @api.onchange('operating_unit_id','journal_entry_ids')
    def ChangeOP(self):
        for record in self:
            if record.journal_entry_ids:
                for journal in record.journal_entry_ids:
                    journal.operating_unit_id = record.operating_unit_id

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        if vals.get('statement_line_id', False):
            move = self.env['account.bank.statement.line'].browse(vals['statement_line_id'])
            if move.operating_unit_id:
                vals['operating_unit_id'] = move.operating_unit_id.id
        else:
            user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            vals['operating_unit_id'] = user.default_operating_unit_id.id
        _super = super(AccountMove, self)
        return _super.create(vals)




