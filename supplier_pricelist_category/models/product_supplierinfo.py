# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    supplier_pricelist_categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Categoría (para lista de precios)",
        help=(
            "Categoría que se aplicará al producto cuando este proveedor sea el proveedor preferido "
            "(el primero por secuencia). La lista de precios puede usar esta categoría para calcular "
            "el precio final."
        ),
        index=True,
    )

    # -------------------------
    # Helpers
    # -------------------------

    def _get_template(self):
        self.ensure_one()
        if self.product_tmpl_id:
            return self.product_tmpl_id
        if self.product_id and self.product_id.product_tmpl_id:
            return self.product_id.product_tmpl_id
        return False

    @api.model
    def _get_preferred_seller(self, tmpl):
        sellers = tmpl.seller_ids.sorted(lambda s: (s.sequence or 0, s.min_qty or 0.0, s.id))
        return sellers[:1] and sellers[0] or False

    @api.model
    def _sync_templates_from_preferred_vendor(self, templates):
        """Sincroniza categ_id de cada template con la categoría del proveedor preferido."""
        if not templates:
            return

        # Evitar loops si un write vuelve a disparar algo desde otro lado
        if self.env.context.get("skip_supplier_pricelist_category_sync"):
            return

        for tmpl in templates:
            preferred = self._get_preferred_seller(tmpl)
            if not preferred:
                continue

            cat = preferred.supplier_pricelist_categ_id
            if not cat:
                # Si el proveedor preferido no tiene categoría, no pisamos la del producto.
                # Podés cambiar esto si querés forzar a "vaciar" la categoría.
                continue

            if tmpl.categ_id.id != cat.id:
                tmpl.with_context(skip_supplier_pricelist_category_sync=True).write({"categ_id": cat.id})

    # -------------------------
    # Overrides
    # -------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # Default útil: si no informan categoría en supplierinfo, se propone la del producto (si existe)
        for vals in vals_list:
            if not vals.get("supplier_pricelist_categ_id"):
                tmpl_id = vals.get("product_tmpl_id")
                prod_id = vals.get("product_id")
                tmpl = False
                if tmpl_id:
                    tmpl = self.env["product.template"].browse(tmpl_id)
                elif prod_id:
                    prod = self.env["product.product"].browse(prod_id)
                    tmpl = prod.product_tmpl_id
                if tmpl and tmpl.categ_id:
                    vals["supplier_pricelist_categ_id"] = tmpl.categ_id.id

        records = super().create(vals_list)

        templates = records.mapped("product_tmpl_id") | records.mapped("product_id.product_tmpl_id")
        self._sync_templates_from_preferred_vendor(templates)
        return records

    def write(self, vals):
        templates_before = (self.mapped("product_tmpl_id") | self.mapped("product_id.product_tmpl_id"))
        res = super().write(vals)

        # Si cambió algo relevante, resincronizamos el/los templates afectados
        relevant = {"sequence", "min_qty", "partner_id", "product_tmpl_id", "product_id", "supplier_pricelist_categ_id"}
        if relevant.intersection(set(vals.keys())):
            templates_after = (self.mapped("product_tmpl_id") | self.mapped("product_id.product_tmpl_id"))
            templates = templates_before | templates_after
            self._sync_templates_from_preferred_vendor(templates)

        return res

    def unlink(self):
        templates = (self.mapped("product_tmpl_id") | self.mapped("product_id.product_tmpl_id"))
        res = super().unlink()
        self._sync_templates_from_preferred_vendor(templates)
        return res
