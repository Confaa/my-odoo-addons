from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    x_category_description = fields.Text(
        string="Descripción de la categoría",
        help="Descripción interna para uso operativo/comercial.",
    )

    x_default_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor sugerido",
        domain=[("supplier_rank", ">", 0)],
        help="Proveedor sugerido para productos de esta categoría.",
    )
