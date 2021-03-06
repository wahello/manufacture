# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    refurbish_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Refurbished Product",
        compute="_compute_refurbish_product",
        inverse="_inverse_refurbish_product",
        search="_search_refurbish_product",
        domain="[('type', '=', 'product')]",
    )

    property_stock_refurbish = fields.Many2one(
        comodel_name="stock.location",
        string="Refurbish Location",
        company_dependent=True,
        domain=[("usage", "like", "production")],
        help="This stock location will be used, instead of the "
        "default one, as the source location for "
        "stock moves generated by repair orders when refurbishing takes "
        "place.",
    )

    @api.depends("product_variant_ids", "product_variant_ids.refurbish_product_id")
    def _compute_refurbish_product(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.refurbish_product_id = (
                template.product_variant_ids.refurbish_product_id
            )

    def _inverse_refurbish_product(self):
        for rec in self:
            if len(rec.product_variant_ids) == 1:
                rec.product_variant_ids.refurbish_product_id = rec.refurbish_product_id

    def _search_refurbish_product(self, operator, value):
        products = self.env["product.product"].search(
            [("refurbish_product_id", operator, value)], limit=None
        )
        return [("id", "in", products.mapped("product_tmpl_id").ids)]
