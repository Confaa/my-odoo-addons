# -*- coding: utf-8 -*-
{
    "name": "Supplier Price Recalculation",
    "version": "19.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Recalcula categoría, costo y precio de venta desde proveedor preferido",
    "license": "LGPL-3",
    "depends": [
        "supplier_pricelist_category",
        "product",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",  # ← Agregado
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}