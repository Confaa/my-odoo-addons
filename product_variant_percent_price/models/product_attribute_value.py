# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    default_extra_price_percent = fields.Float(
        string="Extra (%)",
        digits="Product Price",
        help=(
            "Default percentage to apply over the product template Sale Price "
            "when this attribute value is used in variants."
        ),
    )

    def _propagate_percent_to_templates(self):
        """Propagate the default percent to all existing template lines that
        reference this attribute value.
        """
        PTAV = self.env["product.template.attribute.value"].sudo()
        for av in self:
            ptavs = PTAV.search([("product_attribute_value_id", "=", av.id)])
            if ptavs:
                # PTAV write recomputes price_extra as needed
                ptavs.write({"price_extra_percent": av.default_extra_price_percent or 0.0})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._propagate_percent_to_templates()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "default_extra_price_percent" in vals:
            self._propagate_percent_to_templates()
        return res
