from django.contrib import admin, messages
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from decimal import Decimal

from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "stock")

    # =========================
    # URLS PERSONALIZADAS
    # =========================
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "catalog-tools/",
                self.admin_site.admin_view(self.catalog_tools),
                name="catalog-tools",
            ),
        ]

        return custom_urls + urls

    # =========================
    # DASHBOARD PRINCIPAL
    # =========================
    def catalog_tools(self, request):

        # =========================
        # AUTOCATEGORIZAR
        # =========================
        if request.method == "POST" and "auto_categorize" in request.POST:
            self.auto_categorize()
            messages.success(request, "Productos autocategorizados correctamente.")
            return redirect("admin:catalog-tools")

        # =========================
        # (AUTOFOTOS NO ACTIVO AQUÍ)
        # =========================
        if request.method == "POST" and "auto_photos" in request.POST:
            # aquí lo puedes conectar si luego quieres
            messages.warning(request, "Autofotos se mantiene como comando.")
            return redirect("admin:catalog-tools")

        # =========================
        # UPDATE PRECIOS
        # =========================
        if request.method == "POST" and "update_prices" in request.POST:
            value = request.POST.get("value")

            if not value:
                messages.error(request, "Debes ingresar un valor.")
                return redirect("admin:catalog-tools")

            products = Product.objects.all()

            if "%" in value:
                percent = Decimal(value.replace("%", ""))
                factor = Decimal("1") + (percent / Decimal("100"))

                for p in products:
                    p.price *= factor
            else:
                amount = Decimal(value)
                for p in products:
                    p.price += amount

            Product.objects.bulk_update(products, ["price"])

            messages.success(request, "Precios actualizados correctamente.")
            return redirect("admin:catalog-tools")

        return TemplateResponse(request, "admin/catalog_tools.html", {})

    # =========================
    # AUTOCATEGORIZAR
    # =========================
    def auto_categorize(self):
        categories = Category.objects.all()

        STOPWORDS = {"de", "la", "el", "the", "for", "pour", "&"}

        keyword_list = []

        for category in categories:
            words = category.name.lower().split()

            for word in words:
                if word not in STOPWORDS:
                    keyword_list.append((word, category))

        # priorizar coincidencias largas
        keyword_list.sort(key=lambda x: len(x[0]), reverse=True)

        otros, _ = Category.objects.get_or_create(name="Otros")

        products = Product.objects.all()
        to_update = []

        for product in products:
            name = product.name.lower()
            matched = None

            for keyword, category in keyword_list:
                if keyword in name:
                    matched = category
                    break

            product.category = matched if matched else otros
            to_update.append(product)

        Product.objects.bulk_update(to_update, ["category"])