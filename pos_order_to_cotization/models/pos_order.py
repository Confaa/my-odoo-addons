# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Orden de Venta',
        readonly=True,
        copy=False,
        help='Orden de venta generada desde esta orden de POS'
    )
    
    def _create_order_picking(self):
        """Override para detectar pagos con cuenta de cliente"""
        res = super(PosOrder, self)._create_order_picking()
        
        # Verificar si hay pagos con método "Cuenta del cliente"
        for payment in self.payment_ids:
            if payment.payment_method_id:
                # Verificar si es pay_later (Cuenta del cliente)
                if payment.payment_method_id.type == 'pay_later':
                    if self.partner_id and not self.sale_order_id:
                        self._create_sale_order_from_pos()
                    break
        
        return res
    
    def _create_sale_order_from_pos(self):
        """Crea una orden de venta desde la orden de POS"""
        self.ensure_one()
        
        # Si ya existe, no crear otra
        if self.sale_order_id:
            return self.sale_order_id
        
        # Requiere un cliente
        if not self.partner_id:
            return False
        
        # Preparar valores para la orden de venta
        sale_vals = {
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'date_order': self.date_order,
            'company_id': self.company_id.id,
            'note': 'Generado desde POS: %s' % self.name,
        }
        
        # Agregar usuario si existe
        if self.user_id:
            sale_vals['user_id'] = self.user_id.id
        
        # Agregar pricelist si existe
        if self.pricelist_id:
            sale_vals['pricelist_id'] = self.pricelist_id.id
        elif self.partner_id.property_product_pricelist:
            sale_vals['pricelist_id'] = self.partner_id.property_product_pricelist.id
        
        # Crear la orden de venta
        sale_order = self.env['sale.order'].create(sale_vals)
        
        # Crear las líneas de la orden de venta
        for line in self.lines:
            sale_line_vals = {
                'order_id': sale_order.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            
            # Agregar impuestos si existen
            if line.tax_ids:
                sale_line_vals['tax_ids'] = [(6, 0, line.tax_ids.ids)]
            
            self.env['sale.order.line'].create(sale_line_vals)
        
        # Vincular la orden de venta con la orden de POS
        self.sale_order_id = sale_order.id
        sale_order.pos_order_id = self.id
        
        return sale_order