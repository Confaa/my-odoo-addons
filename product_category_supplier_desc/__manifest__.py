{
    "name": "Product Category: Description & Supplier",
    "version": "19.0.1.0.1",
    "category": "Inventory",
    "summary": "Add description and default supplier to product categories",
    "depends": ["product", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_category_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
