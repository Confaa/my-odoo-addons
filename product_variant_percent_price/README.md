Product Variant Percent Pricing (Odoo 19)
================================================

Adds a field `Extra (%)` on Product Template Attribute Values so you can define
variant price adjustments as a percentage of the product template Sale Price
(`list_price`).

Formula:
- price_extra = list_price * (percent/100)

Behavior:
- Setting Extra (%) recomputes price_extra automatically.
- Setting price_extra recomputes Extra (%) automatically.
- Changing template list_price recomputes all % extras.
- If Extra (%) is 0, price_extra is not overwritten (fixed-amount mode remains).
