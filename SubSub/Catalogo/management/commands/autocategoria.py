from django.core.management.base import BaseCommand
from Catalogo.models import Product, Category

STOPWORDS = {"de", "la", "el", "the", "for", "pour", "&"}

class Command(BaseCommand):
    help = "Auto-categoriza productos de forma inteligente"

    def handle(self, *args, **kwargs):
        categories = Category.objects.all()

        # 🔥 Lista de (keyword, category) ordenada por longitud
        keyword_list = []

        for category in categories:
            words = category.name.lower().split()

            for word in words:
                clean_word = word.strip().lower()
                if clean_word and clean_word not in STOPWORDS:
                    keyword_list.append((clean_word, category))

        # 🔥 ordenar por longitud (más específicas primero)
        keyword_list.sort(key=lambda x: len(x[0]), reverse=True)

        otros_category, _ = Category.objects.get_or_create(name="Otros")

        products = Product.objects.all()

        to_update = []
        assigned = 0
        others_count = 0

        for product in products:
            product_name = product.name.lower()
            matched_category = None

            for keyword, category in keyword_list:
                if keyword in product_name:
                    matched_category = category
                    break

            if matched_category:
                if product.category != matched_category:
                    product.category = matched_category
                    to_update.append(product)
                    assigned += 1
            else:
                if product.category != otros_category:
                    product.category = otros_category
                    to_update.append(product)
                    others_count += 1

        Product.objects.bulk_update(to_update, ['category'])

        self.stdout.write(self.style.SUCCESS(
            f"🔥 Mejorado: {assigned} categorizados, {others_count} en 'Otros'"
        ))