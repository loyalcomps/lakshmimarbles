from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime
from odoo import models,fields,api,_


class Grandsale_detail(models.AbstractModel):
    _name = 'report.grand_sale_detail_xls.grand_sale_detail_pdf'


    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        pos_config_ids = data['form']['pos_config_ids']
        counter_only = data['form']['counter_only']
        sl = 0
        query = '''
        
          SELECT  	
		sum(dd.qty) as qty,sum(dd.unit) as unit,sum(dd.gstsgst) as gstsgst,
		sum(round(((dd.taxable*dd.gstsgst)/100),2)) as lcgstsgst,max(dd.pname) as pname,
		sum(round(((dd.taxable*dd.igst)/100),2)) as ligst,sum(round(((dd.taxable*dd.cess)/100),2)) as lcess,
		
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxamount ELSE 0 END ),0)  as taxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxable ELSE 0 END ),0)  as untaxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.total ELSE 0 END ),0)  as totalamount

	 from
		(
		select max(table1.cgstsgst) as gstsgst,max(table1.igst) as igst,
		max(table1.cess) as cess,table1.posid as posid,
		max(table1.qty) as qty,max(table1.unit) as unit,
		max(table1.pname) as pname,


		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))),2) as total,
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * max(COALESCE(table1.amount,'0')/(100+COALESCE(table1.amount,'0'))),2) as taxamount, 
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * 100 / max(100+COALESCE(table1.amount,'0')),2)  as taxable  

		
	from (

        select  
		((CASE WHEN (actax.igst) = false and actax.cess = false then  (actax.amount) ELSE 0 END)) as cgstsgst,
		((CASE WHEN actax.igst = true and actax.cess = false then  (actax.amount) ELSE 0 END)) as igst,
		((CASE WHEN actax.igst = false and actax.cess = true then  (actax.amount) ELSE 0 END)) as cess,
		
		(pol.id) as posid,
		(pol.product_id) as product,
		((pol.qty)) as qty,  
		(pol.price_unit) as unit,
		(pol.discount) as discount,
		(pt.name) as pname,
		COALESCE(actax.amount,'0') as amount
	from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                left join product_product as pp on(pp.id=pol.product_id)
                left join product_template as pt on (pt.id=pp.product_tmpl_id)
                left join account_bank_statement_line as acs on(acs.pos_statement_id = po.id)
                LEFT JOIN account_bank_statement st ON (st.id=acs.statement_id)
                    LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                    LEFT JOIN pos_session session ON (session.id=po.session_id) 
                left join account_tax_pos_order_line_rel as act on (act.pos_order_line_id =pol.id)
                left join account_tax as actax on (actax.id =act.account_tax_id)
                
	where
	acs.amount>0 and pol.qty>0 and
                po.state in  ('done', 'paid','invoiced')
		and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and session.config_id=%s
		and pol.company_id= %s AND COALESCE(actax.cess ,'f') = 'f'
	group by   actax.cess,actax.igst,pol.price_unit,pol.qty,pol.discount,pol.id,actax.amount,pt.name,pol.product_id,session.config_id) as table1
	group by table1.posid
                 ) as dd  group by dd.posid

                        '''
        self.env.cr.execute(query, (
                     date_start, date_end,pos_config_ids,company_id,
                                    ))
        for row in self.env.cr.dictfetchall():
            sl += 1


            res = {
                'sl_no': sl,
                 'qty': row['qty'] if row['qty'] else 0,
                'unit': row['unit'] if row['unit'] else 0,
                'pname': row['pname'] if row['pname'] else 0,
                # 'gstsgst': row['gstsgst'] if row['gstsgst'] else 0,
                'taxamount': row['taxamount'] if row['taxamount'] else 0,
                'untaxamount': row['untaxamount'] if row['untaxamount'] else 0,
                'totalamount': row['totalamount'] if row['totalamount'] else 0,
            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_linesone(self, data):

            lines = []

            date_start = data['form']['date_start']
            date_end = data['form']['date_end']
            company_id = data['form']['branch_ids']
            pos_config_ids = data['form']['pos_config_ids']
            counter_only = data['form']['counter_only']
            sl = 0
            query = '''

             SELECT  	
		sum(dd.qty) as qty,sum(dd.unit) as unit,sum(dd.gstsgst) as gstsgst,
		sum(round(((dd.taxable*dd.gstsgst)/100),2)) as lcgstsgst,max(dd.pname) as pname,
		sum(round(((dd.taxable*dd.igst)/100),2)) as ligst,sum(round(((dd.taxable*dd.cess)/100),2)) as lcess,
		
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxamount ELSE 0 END ),0)  as taxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxable ELSE 0 END ),0)  as untaxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.total ELSE 0 END ),0)  as totalamount

	 from
		(
		select max(table1.cgstsgst) as gstsgst,max(table1.igst) as igst,
		max(table1.cess) as cess,table1.posid as posid,
		max(table1.qty) as qty,max(table1.unit) as unit,
		max(table1.pname) as pname,


		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))),2) as total,
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * max(COALESCE(table1.amount,'0')/(100+COALESCE(table1.amount,'0'))),2) as taxamount, 
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * 100 / max(100+COALESCE(table1.amount,'0')),2)  as taxable  

		
	from (

        select  
		((CASE WHEN (actax.igst) = false and actax.cess = false then  (actax.amount) ELSE 0 END)) as cgstsgst,
		((CASE WHEN actax.igst = true and actax.cess = false then  (actax.amount) ELSE 0 END)) as igst,
		((CASE WHEN actax.igst = false and actax.cess = true then  (actax.amount) ELSE 0 END)) as cess,
		
		(pol.id) as posid,
		(pol.product_id) as product,
		((pol.qty)) as qty,  
		(pol.price_unit) as unit,
		(pol.discount) as discount,
		(pt.name) as pname,
		COALESCE(actax.amount,'0') as amount
	from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                left join product_product as pp on(pp.id=pol.product_id)
                left join product_template as pt on (pt.id=pp.product_tmpl_id)
                left join account_bank_statement_line as acs on(acs.pos_statement_id = po.id)
                LEFT JOIN account_bank_statement st ON (st.id=acs.statement_id)
                    LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                    LEFT JOIN pos_session session ON (session.id=po.session_id) 
                left join account_tax_pos_order_line_rel as act on (act.pos_order_line_id =pol.id)
                left join account_tax as actax on (actax.id =act.account_tax_id)
                
	where
	acs.amount<0 and pol.qty<0 and
                po.state in  ('done', 'paid','invoiced')
		and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and session.config_id=%s
		and pol.company_id= %s AND COALESCE(actax.cess ,'f') = 'f'
	group by   actax.cess,actax.igst,pol.price_unit,pol.qty,pol.discount,pol.id,actax.amount,pt.name,pol.product_id,session.config_id) as table1
	group by table1.posid
                 ) as dd  group by dd.posid



                            '''
            self.env.cr.execute(query, (
                date_start, date_end,pos_config_ids, company_id,
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1

                res = {
                    'sl_no': sl,
                    'qty': row['qty'] if row['qty'] else 0,
                    'unit': row['unit'] if row['unit'] else 0,
                    'pname':row['pname'] if row['pname'] else 0,
                    # 'gstsgst': row['gstsgst'] if row['gstsgst'] else 0,
                    'taxamount': row['taxamount'] if row['taxamount'] else 0,
                    'untaxamount': row['untaxamount'] if row['untaxamount'] else 0,
                    'totalamount': row['totalamount'] if row['totalamount'] else 0,
                }

                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_grater(self, data, config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0


        query = '''


   SELECT  	
		sum(dd.qty) as qty,sum(dd.unit) as unit,sum(dd.gstsgst) as gstsgst,
		sum(round(((dd.taxable*dd.gstsgst)/100),2)) as lcgstsgst,max(dd.pname) as pname,
		sum(round(((dd.taxable*dd.igst)/100),2)) as ligst,sum(round(((dd.taxable*dd.cess)/100),2)) as lcess,
		
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxamount ELSE 0 END ),0)  as taxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxable ELSE 0 END ),0)  as untaxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.total ELSE 0 END ),0)  as totalamount

	 from
		(
		select max(table1.cgstsgst) as gstsgst,max(table1.igst) as igst,
		max(table1.cess) as cess,table1.posid as posid,
		max(table1.qty) as qty,max(table1.unit) as unit,
		max(table1.pname) as pname,


		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))),2) as total,
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * max(COALESCE(table1.amount,'0')/(100+COALESCE(table1.amount,'0'))),2) as taxamount, 
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * 100 / max(100+COALESCE(table1.amount,'0')),2)  as taxable  

		
	from (

        select  
		((CASE WHEN (actax.igst) = false and actax.cess = false then  (actax.amount) ELSE 0 END)) as cgstsgst,
		((CASE WHEN actax.igst = true and actax.cess = false then  (actax.amount) ELSE 0 END)) as igst,
		((CASE WHEN actax.igst = false and actax.cess = true then  (actax.amount) ELSE 0 END)) as cess,
		
		(pol.id) as posid,
		(pol.product_id) as product,
		((pol.qty)) as qty,  
		(pol.price_unit) as unit,
		(pol.discount) as discount,
		(pt.name) as pname,
		COALESCE(actax.amount,'0') as amount
	from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                left join product_product as pp on(pp.id=pol.product_id)
                left join product_template as pt on (pt.id=pp.product_tmpl_id)
                left join account_bank_statement_line as acs on(acs.pos_statement_id = po.id)
                LEFT JOIN account_bank_statement st ON (st.id=acs.statement_id)
                    LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                    LEFT JOIN pos_session session ON (session.id=po.session_id) 
                left join account_tax_pos_order_line_rel as act on (act.pos_order_line_id =pol.id)
                left join account_tax as actax on (actax.id =act.account_tax_id)
                
	where
	acs.amount>0 and pol.qty>0 and
                po.state in  ('done', 'paid','invoiced')
		and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and session.config_id = %s
		and pol.company_id= %s AND COALESCE(actax.cess ,'f') = 'f'
	group by   actax.cess,actax.igst,pol.price_unit,pol.qty,pol.discount,pol.id,actax.amount,pt.name,pol.product_id,session.config_id) as table1
	group by table1.posid
                 ) as dd


                               '''
        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {
                'sl_no': sl,
                'qty': row['qty'] if row['qty'] else 0,
                'unit': row['unit'] if row['unit'] else 0,
                'pname': row['pname'] if row['pname'] else 0,
                # 'gstsgst': row['gstsgst'] if row['gstsgst'] else 0,
                'taxamount': row['taxamount'] if row['taxamount'] else 0,
                'untaxamount': row['untaxamount'] if row['untaxamount'] else 0,
                'totalamount': row['totalamount'] if row['totalamount'] else 0,
            }

            # lines.append(res)

            if res:
                return res
            else:
                return []

    def get_lower(self, data, config_id):

            lines = []

            date_start = data['form']['date_start']
            date_end = data['form']['date_end']
            company_id = data['form']['branch_ids']
            counter_only = data['form']['counter_only']
            pos_config_ids = data['form']['pos_config_ids']

            sl = 0

            query = '''


     SELECT  	
		sum(dd.qty) as qty,sum(dd.unit) as unit,sum(dd.gstsgst) as gstsgst,
		sum(round(((dd.taxable*dd.gstsgst)/100),2)) as lcgstsgst,max(dd.pname) as pname,
		sum(round(((dd.taxable*dd.igst)/100),2)) as ligst,sum(round(((dd.taxable*dd.cess)/100),2)) as lcess,
		
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxamount ELSE 0 END ),0)  as taxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.taxable ELSE 0 END ),0)  as untaxamount,
		COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.total ELSE 0 END ),0)  as totalamount

	 from
		(
		select max(table1.cgstsgst) as gstsgst,max(table1.igst) as igst,
		max(table1.cess) as cess,table1.posid as posid,
		max(table1.qty) as qty,max(table1.unit) as unit,
		max(table1.pname) as pname,


		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))),2) as total,
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * max(COALESCE(table1.amount,'0')/(100+COALESCE(table1.amount,'0'))),2) as taxamount, 
		round(sum((table1.qty)  * ( table1.unit * (1 - (table1.discount) / 100.0))) * 100 / max(100+COALESCE(table1.amount,'0')),2)  as taxable  

		
	from (

        select  
		((CASE WHEN (actax.igst) = false and actax.cess = false then  (actax.amount) ELSE 0 END)) as cgstsgst,
		((CASE WHEN actax.igst = true and actax.cess = false then  (actax.amount) ELSE 0 END)) as igst,
		((CASE WHEN actax.igst = false and actax.cess = true then  (actax.amount) ELSE 0 END)) as cess,
		
		(pol.id) as posid,
		(pol.product_id) as product,
		((pol.qty)) as qty,  
		(pol.price_unit) as unit,
		(pol.discount) as discount,
		(pt.name) as pname,
		COALESCE(actax.amount,'0') as amount
	from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                left join product_product as pp on(pp.id=pol.product_id)
                left join product_template as pt on (pt.id=pp.product_tmpl_id)
                left join account_bank_statement_line as acs on(acs.pos_statement_id = po.id)
                LEFT JOIN account_bank_statement st ON (st.id=acs.statement_id)
                    LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                    LEFT JOIN pos_session session ON (session.id=po.session_id) 
                left join account_tax_pos_order_line_rel as act on (act.pos_order_line_id =pol.id)
                left join account_tax as actax on (actax.id =act.account_tax_id)
                
	where
	acs.amount<0 and pol.qty<0 and
                po.state in  ('done', 'paid','invoiced')
		and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and session.config_id = %s
		and pol.company_id= %s AND COALESCE(actax.cess ,'f') = 'f'
	group by   actax.cess,actax.igst,pol.price_unit,pol.qty,pol.discount,pol.id,actax.amount,pt.name,pol.product_id,session.config_id) as table1
	group by table1.posid
                 ) as dd



                                   '''
            self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
            for row in self.env.cr.dictfetchall():
                sl += 1

                res = {

                    'sl_no': sl,
                    'qty': row['qty'] if row['qty'] else 0,
                    'unit': row['unit'] if row['unit'] else 0,
                    'pname': row['pname'] if row['pname'] else 0,
                    # 'gstsgst': row['gstsgst'] if row['gstsgst'] else 0,
                    'taxamount': row['taxamount'] if row['taxamount'] else 0,
                    'untaxamount': row['untaxamount'] if row['untaxamount'] else 0,
                    'totalamount': row['totalamount'] if row['totalamount'] else 0,
                }

                # lines.append(res)

                if res:
                    return res
                else:
                    return []
                # else:
                #     res = {
                #
                #     'sl_no': 0,
                #     'qty': 0,
                #     'unit':  0,
                #     'pname':  0,
                #     # 'gstsgst': row['gstsgst'] if row['gstsgst'] else 0,
                #     'taxamount': 0,
                #     'untaxamount': 0,
                #     'totalamount': 0,
                # }
                #
                #     return res
    def get_config(self, data):
        lines = []
        configs = {}
        config = self.env['pos.config'].browse(data['form']['pos_config_ids'])
        for pfg in config:
            configs[pfg.id] = pfg.name

        lines.append(configs)

        if lines:
            return lines
        else:
            return []


    @api.model
    def render_html(self, docids, data=None, ):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        get_lines = self.get_lines(data)
        get_linesone = self.get_linesone(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        config = self.env['pos.config'].browse(pos_config_ids)

        get_low = []
        get_high = []


        if counter_only and pos_config_ids:
            for pfg in config:
                get_low.append(self.get_lower(data, pfg.id))
                get_high.append(self.get_grater(data, pfg.id))



        docargs = {

            'counter_only': counter_only,
            'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,

            'pos_config_ids': pos_config_ids,
            'config': config,
            'valueone': get_low if get_low else 0,
            'valuetwo': get_high if get_high else 0,

            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),

            'data': data['form'],
            'get_lines': get_lines,
            'get_linesone':get_linesone,
        }

        return self.env['report'].render('grand_sale_detail_xls.grand_sale_detail_pdf', docargs)
