# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _get_first_pricelist(self):
        """Obtiene la primera lista de precios activa por secuencia."""
        return self.env['product.pricelist'].sudo().search([
            ('active', '=', True),
            '|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)
        ], order='sequence, id', limit=1)
    
    def _get_preferred_seller(self):
        """Obtiene el proveedor preferido (menor sequence, min_qty, id)."""
        self.ensure_one()
        sellers = self.seller_ids.sorted(lambda s: (s.sequence or 0, s.min_qty or 0.0, s.id))
        return sellers[0] if sellers else False
    
    def _recalc_category_from_supplier(self):
        """Sincroniza la categoría del producto con la del proveedor preferido."""
        self.ensure_one()
        sel = self._get_preferred_seller()
        
        if not sel:
            return False
        
        try:
            categ = sel.supplier_pricelist_categ_id
            if categ and self.categ_id.id != categ.id:
                self.categ_id = categ
                return True
        except:
            pass
        
        return False
    
    def _recalc_cost_from_supplier(self):
        """Recalcula el costo estándar desde el proveedor preferido."""
        self.ensure_one()
        sel = self._get_preferred_seller()
        
        if not sel:
            return False
        
        today = datetime.date.today()
        company = self.company_id or self.env.company
        company_currency = company.currency_id
        vendor_currency = sel.currency_id or company_currency
        vendor_price = sel.price or 0.0
        
        new_cost = vendor_currency._convert(
            vendor_price, 
            company_currency, 
            company, 
            today
        )
        
        if abs((self.standard_price or 0.0) - new_cost) > 0.0001:
            self.standard_price = new_cost
            return True
        
        return False
    
    def _recalc_sale_price_from_pricelist(self, pricelist):
        """Recalcula el precio de venta desde la lista de precios."""
        self.ensure_one()
        
        if not pricelist or not self.product_variant_ids:
            return False
        
        today = datetime.date.today()
        product = self.product_variant_ids[0]
        
        new_sale = pricelist._get_product_price(product, 1.0, date=today)
        
        if abs((self.list_price or 0.0) - new_sale) > 0.0001:
            self.list_price = new_sale
            return True
        
        return False
    
    def action_recalc_all_prices(self):
        """
        Acción de servidor: Recalcula categoría, costo y precio de venta
        desde el proveedor preferido y la primera lista de precios.
        """
        pricelist = self._get_first_pricelist()
        
        if not pricelist:
            raise UserError(_('No se encontró ninguna lista de precios activa.'))
        
        count_categ = 0
        count_cost = 0
        count_price = 0
        count_skip = 0
        
        for tmpl in self:
            sel = tmpl._get_preferred_seller()
            
            if not sel:
                count_skip += 1
                continue
            
            # 1) Categoría
            if tmpl._recalc_category_from_supplier():
                count_categ += 1
            
            # 2) Costo
            if tmpl._recalc_cost_from_supplier():
                count_cost += 1
            
            # 3) Precio de venta
            if tmpl._recalc_sale_price_from_pricelist(pricelist):
                count_price += 1
        
        # Mensaje de resultado
        message = _(
            '✅ Recálculo completado:\n\n'
            '• Categorías actualizadas: %(categ)s\n'
            '• Costos actualizados: %(cost)s\n'
            '• Precios de venta actualizados: %(price)s\n'
            '• Productos sin proveedor: %(skip)s\n\n'
            'Total procesados: %(total)s'
        ) % {
            'categ': count_categ,
            'cost': count_cost,
            'price': count_price,
            'skip': count_skip,
            'total': len(self)
        }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recálculo de Precios'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }