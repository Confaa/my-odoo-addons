# -*- coding: utf-8 -*-
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_percent_price_extras(self):
        """Recompute price_extra for all template attribute values that have
        a non-zero percentage, based on the current list_price.
        """
        PTAV = self.env["product.template.attribute.value"].sudo()
        for tmpl in self:
            ptavs = PTAV.search([
                ("product_tmpl_id", "=", tmpl.id),
                ("price_extra_percent", "!=", 0.0),
            ])
            ptavs._apply_percent_to_price_extra()

    def write(self, vals):
        res = super().write(vals)

        # If the template sale price changes, recompute all % extras
        if "list_price" in vals and not self.env.context.get("skip_percent_price_extra"):
            self._update_percent_price_extras()

        return res
