# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = "account.tax"

    cess = fields.Boolean(string='Cess' , default=False)
    igst = fields.Boolean(string='IGST',default=False)


class GstTaxData(models.TransientModel):
    _inherit = "gst.tax.data"


    def getGstTaxData(self, invoiceObj, invoiceLineObj, rateObjs, taxedAmount, invoiceType):
        taxedAmount = round(taxedAmount, 2)
        gstDict = {
            "rt": 0.0, "iamt": 0.0, "camt": 0.0, "samt": 0.0, "csamt": 0.0
        }
        if invoiceType == "export":
            gstDict = {
                "txval": 0.0, "rt": 0, "iamt": 0.0
            }
        if invoiceType in ['imps', 'impg']:
            gstDict = {
                "elg": "no", "txval": 0.0, "rt": 0, "iamt": 0.0, 'tx_i': 0.0, 'tx_cs': 0.0
            }
        if invoiceType == "b2cs":
            gstDict['sply_ty'] = 'INTRA'
            gstDict['typ'] = 'OE'
        if rateObjs:
            if invoiceObj.partner_id.country_id.code == 'IN':
                for rateObj in rateObjs:
                    if rateObj.amount_type == "group":
                        for childObj in rateObj.children_tax_ids:
                            if rateObj.cess:

                                if childObj.cess:
                                    gstDict['csamt'] = round(taxedAmount / childObj.cess_adjust_amount, 2)

                                else:
                                    gstDict['rt'] = childObj.amount*2
                                    gstDict['samt'] = round(taxedAmount/childObj.cess_adjust_amount, 2)
                                    gstDict['camt'] = round(taxedAmount / childObj.cess_adjust_amount, 2)

                            else:
                                gstDict['rt'] = childObj.amount * 2
                                gstDict['samt'] = round(taxedAmount / 2, 2)
                                gstDict['camt'] = round(taxedAmount / 2, 2)
                                break
                        break
                    else:
                        gstDict['rt'] = rateObj.amount
                        gstDict['iamt'] = round(taxedAmount, 2)
                    break
            elif invoiceType in ['imps', 'impg']:
                for rateObj in rateObjs:
                    gstDict['rt'] = rateObj.amount
                    gstDict['iamt'] = round(taxedAmount, 2)
                    break
        return gstDict


class GstHsnData(models.TransientModel):
    _inherit = "gst.hsn.data"

    def getHSNData(self, invoiceObj, count, hsnDict={}, hsnDataDict={}):
        mainData = []
        jsonData = []
        currency = invoiceObj.currency_id or None
        ctx = dict(self._context or {})
        for invoiceLineObj in invoiceObj.invoice_line_ids:
            # price = invoiceLineObj.price_subtotal/invoiceLineObj.quantity
            if invoiceLineObj.quantity > 0:
                price = invoiceLineObj.price_unit * (1 - (invoiceLineObj.discount or 0.0) / 100.0) - (
                            invoiceLineObj.discount_amount / invoiceLineObj.quantity)
            else:
                price = invoiceLineObj.price_unit * (1 - (invoiceLineObj.discount or 0.0) / 100.0)
            # price = invoiceLineObj.price_unit * (1 - (invoiceLineObj.discount or 0.0) / 100.0) - (invoiceLineObj.discount_amount/invoiceLineObj.quantity)
            taxedAmount,cgst,sgst,igst,cess = 0.0, 0.0, 0.0, 0.0,0.0
            rateObjs = invoiceLineObj.invoice_line_tax_ids
            if rateObjs:
                taxData = self.env['gst.tax.data'].getTaxedAmount(rateObjs, price, currency, invoiceLineObj, invoiceObj)
                rateAmount = taxData[1]
                taxedAmount = taxData[0]
                if currency.name != 'INR':
                    taxedAmount = taxedAmount * currency.rate
                taxedAmount = round(taxedAmount, 2)
                if invoiceObj.partner_id.country_id.code == 'IN':
                    for rateObj in rateObjs:
                        if rateObj.amount_type == "group":
                            if rateObj.cess:
                                for childObj in rateObj.children_tax_ids:
                                    if childObj.cess:
                                        cess = round(taxedAmount / childObj.cess_adjust_amount, 2)
                                    else:
                                        cgst, sgst = round(taxedAmount / childObj.cess_adjust_amount, 2), round(taxedAmount / childObj.cess_adjust_amount, 2)
                            else:
                                cgst,sgst = round(taxedAmount/2, 2),round(taxedAmount/2, 2)
                        else:
                            igst = round(taxedAmount, 2)
            invUntaxedAmount = round(invoiceLineObj.price_subtotal, 2)
            if currency.name != 'INR':
                invUntaxedAmount = round(invoiceLineObj.price_subtotal * currency.rate, 2)
            productObj = invoiceLineObj.product_id
            hsnVal = productObj.hsn or 'False'
            hsnName = productObj.name or 'name'
            uqc = 'OTH'
            if productObj.uom_id:
                uom = productObj.uom_id.id
                uqcObj = self.env['uom.mapping'].search([('uom', '=', uom)])
                if uqcObj:
                    uqc = uqcObj[0].name.code
            invQty = invoiceLineObj.quantity
            invAmountTotal = invUntaxedAmount + taxedAmount
            if hsnDataDict.get(hsnVal):
                if hsnDataDict.get(hsnVal).get(hsnName):
                    if hsnDataDict.get(hsnVal).get(hsnName).get('qty'):
                        invQty = hsnDataDict.get(hsnVal).get(hsnName).get('qty') + invQty
                        hsnDataDict.get(hsnVal).get(hsnName)['qty'] = invQty
                    else:
                        hsnDataDict.get(hsnVal).get(hsnName)['qty'] = invQty
                    if hsnDataDict.get(hsnVal).get(hsnName).get('val'):
                        invAmountTotal = round(hsnDataDict.get(hsnVal).get(hsnName).get('val') + invAmountTotal, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['val'] = invAmountTotal
                    else:
                        invAmountTotal = round(invAmountTotal, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['val'] = invAmountTotal
                    if hsnDataDict.get(hsnVal).get(hsnName).get('txval'):
                        invUntaxedAmount = round(hsnDataDict.get(hsnVal).get(hsnName).get('txval') + invUntaxedAmount, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['txval'] = invUntaxedAmount
                    else:
                        invUntaxedAmount = round(invUntaxedAmount, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['txval'] = invUntaxedAmount
                    if hsnDataDict.get(hsnVal).get(hsnName).get('iamt'):
                        igst = round(hsnDataDict.get(hsnVal).get(hsnName).get('iamt') + igst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['iamt'] = igst
                    else:
                        igst = round(igst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['iamt'] = igst
                    if hsnDataDict.get(hsnVal).get(hsnName).get('camt'):
                        cgst = round(hsnDataDict.get(hsnVal).get(hsnName).get('camt') + cgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['camt'] = cgst
                    else:
                        cgst = round(cgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['camt'] = cgst
                    if hsnDataDict.get(hsnVal).get(hsnName).get('samt'):
                        sgst = round(hsnDataDict.get(hsnVal).get(hsnName).get('samt') + sgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['samt'] = sgst
                    else:
                        sgst = round(sgst, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['samt'] = sgst
                    if hsnDataDict.get(hsnVal).get(hsnName).get('csamt'):
                        cess = round(hsnDataDict.get(hsnVal).get(hsnName).get('csamt') + cess, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['csamt'] = cess
                    else:
                        cess = round(cess, 2)
                        hsnDataDict.get(hsnVal).get(hsnName)['csamt'] = cess
                else:
                    count = count + 1
                    hsnDataDict.get(hsnVal)[hsnName] = {
                                                        'num':count,
                                                        'hsn_sc':hsnVal,
                                                        'desc':hsnName,
                                                        'uqc':uqc,
                                                        'qty':invQty,
                                                        'val':invAmountTotal,
                                                        'txval':invUntaxedAmount,
                                                        'iamt':igst,
                                                        'camt':cgst,
                                                        'samt':sgst,
                                                        'csamt':cess
                                                    }
            else:
                count = count + 1
                hsnDataDict[hsnVal] = {hsnName:{
                                                'num':count,
                                                'hsn_sc':hsnVal,
                                                'desc':hsnName,
                                                'uqc':uqc,
                                                'qty':invQty,
                                                'val':invAmountTotal,
                                                'txval':invUntaxedAmount,
                                                'iamt':igst,
                                                'camt':cgst,
                                                'samt':sgst,
                                                'csamt':cess
                                            }}
            hsnData = [
                productObj.hsn, productObj.name, uqc, invQty,
                invAmountTotal, invUntaxedAmount, igst, cgst, sgst, cess
            ]
            if hsnDict.get(hsnVal):
                hsnDict.get(hsnVal)[hsnName] = hsnData
            else:
                hsnDict[hsnVal] = {hsnName:hsnData}
            mainData.append(hsnData)
        return [mainData, jsonData, hsnDict, hsnDataDict]