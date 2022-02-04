/* Copyright 2004-2010 OpenERP SA
 * Copyright 2017 RGB Consulting S.L. (https://www.rgbconsulting.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('kerala_flood_cess.partner', function (require){
"use strict"

//    var models = require('point_of_sale.models');
//    var screens = require('point_of_sale.screens');

//    var utils = require('web.utils');
//    var round_pr = utils.round_precision;
//
//    var core = require('web.core');
//    var QWeb = core.qweb;
//    var _t = core._t;

//    models.load_fields('res.partner',['kfc_plot','x_gstin','partner_type']);


    var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;
    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'res.partner'){
             model.fields.push('kfc_plot');
             model.fields.push('x_gstin');
             model.fields.push('partner_type');

         // other field you want to pull from the res.company table.

    }
}
    });