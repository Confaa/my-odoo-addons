# -*- coding: utf-8 -*-
{
    "name": "Supplier Pricelist Category",
    "version": "19.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Categoría por proveedor (supplierinfo) y sincronización con categoría del producto",
    "license": "LGPL-3",
    "depends": ["product", "purchase"],
    "data": [
        "security/ir.model.access.csv",  # ← Agregado
        "views/product_supplierinfo_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}