# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    pos_order_id = fields.Many2one(
        'pos.order',
        string='Orden de POS',
        readonly=True,
        copy=False,
        help='Orden de POS que generó esta orden de venta'
    )