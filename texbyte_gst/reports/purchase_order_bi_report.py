# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
from vobject.base import readOne

class PurchaseAnalysisReport(models.Model):
    _name = "texbyte_gst.purchase.order.bi.report"
    _description = "Purchase Order"
    _auto = False
    _order = "date_order"

    name = fields.Char('Order Reference', readonly=True)
    date_order = fields.Datetime('Date Order', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    create_uid = fields.Many2one('res.users', 'Responsible', readonly=True)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Bills Received'),
        ], string='Billing Status', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    amount_untaxed = fields.Float('Untaxed Amount', readonly=True)
    qty_invoiced = fields.Float('Billed Qty', readonly=True)
    qty_received = fields.Float('Received Qty', readonly=True)
    amount_tax = fields.Float('Taxes', readonly=True)
    amount_total = fields.Float('Total', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    product_qty = fields.Float('Quantity', readonly=True)
    product_uom = fields.Many2one('product.uom', 'Product Unit of Measure', readonly=True)
    price_unit = fields.Float('Unit Price', readonly=True)

    def _select(self):
        #SELECT l.name             as name,
        #       m.description      as stage_description,
        #          l.employee_id      as employee_id,
        select_str = """
            SELECT  min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.price_unit) as price_unit,
                    sum(l.product_qty / u.factor * u2.factor) as product_qty,
                    sum(l.qty_received / u.factor * u2.factor) as qty_received,
                    sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                    count(*) as nbr,
                    o.name as name,
                    o.date_order as date_order,
                    o.state as state,
                    o.invoice_status as invoice_status,
                    sum(o.amount_tax) as amount_tax,
                    sum(o.amount_total) as amount_total,
                    sum(o.amount_untaxed) as amount_untaxed,
                    o.partner_id as partner_id,
                    o.create_uid as create_uid,
                    o.company_id as company_id,
                    t.categ_id as categ_id,
                    p.product_tmpl_id,
                    partner.country_id as country_id
        """ 
        return select_str

    def _from(self):
        from_str = """
                purchase_order_line l
                    join purchase_order o on (l.order_id=o.id)
                    join res_partner partner on o.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
        """
        return from_str

    def _group_by(self):
        #GROUP BY l.name,
        #          l.perfitems,
        #          m.description,
        #          l.employee_id,
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    o.name,
                    o.date_order,
                    o.partner_id,
                    o.create_uid,
                    o.state,
                    o.invoice_status,
                    o.company_id,
                    p.product_tmpl_id,
                    partner.country_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = 'stmdocs_admin_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
