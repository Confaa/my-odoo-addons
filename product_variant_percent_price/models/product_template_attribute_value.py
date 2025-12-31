# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    price_extra_percent = fields.Float(
        string="Extra (%)",
        digits="Product Price",
        help=(
            "If set, the variant extra will be computed as a percentage of the "
            "product template Sale Price (list_price). Example: 10 = +10%."
        ),
    )

    def _percent_to_extra(self):
        """If price_extra_percent is set, compute price_extra:
        price_extra = template.list_price * (percent/100)
        """
        for ptav in self:
            tmpl = ptav.product_tmpl_id
            if not tmpl:
                continue

            percent = ptav.price_extra_percent or 0.0
            if not percent:
                # If it is 0, do not override price_extra to allow fixed-amount mode.
                continue

            base = tmpl.list_price or 0.0
            new_extra = base * (percent / 100.0)

            if abs((ptav.price_extra or 0.0) - new_extra) > 0.000001:
                ptav.with_context(skip_percent_price_extra=True).write({"price_extra": new_extra})

    def _extra_to_percent(self):
        """If price_extra is set, compute price_extra_percent:
        percent = (price_extra / template.list_price) * 100
        """
        for ptav in self:
            tmpl = ptav.product_tmpl_id
            if not tmpl:
                continue

            base = tmpl.list_price or 0.0
            extra = ptav.price_extra or 0.0

            if not base:
                # Avoid division by zero; keep percent at 0
                new_percent = 0.0
            else:
                new_percent = (extra / base) * 100.0

            if abs((ptav.price_extra_percent or 0.0) - new_percent) > 0.000001:
                ptav.with_context(skip_percent_price_extra=True).write({"price_extra_percent": new_percent})

    @api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)

    # Bidirectional sync at create time depending on what the user provided.
    # If both are provided, percent wins.
    for ptav, vals in zip(records, vals_list):
        # If percent not provided but attribute value has a default percent, copy it.
        if not vals.get("price_extra_percent") and vals.get("product_attribute_value_id"):
            av = self.env["product.attribute.value"].browse(vals.get("product_attribute_value_id"))
            if av and av.default_extra_price_percent:
                ptav.with_context(skip_percent_price_extra=True).write(
                    {"price_extra_percent": av.default_extra_price_percent}
                )

        if ptav.price_extra_percent:
            ptav._percent_to_extra()
        elif "price_extra" in vals and vals.get("price_extra") not in (None, False):
            ptav._extra_to_percent()

    return records

    def write(self, vals):
        res = super().write(vals)

        # Prevent recursive loop when we write fields ourselves.
        if self.env.context.get("skip_percent_price_extra"):
            return res

        # If both are changed in the same write, percent wins.
        if "price_extra_percent" in vals:
            self._percent_to_extra()
        elif "price_extra" in vals:
            self._extra_to_percent()

        return res
