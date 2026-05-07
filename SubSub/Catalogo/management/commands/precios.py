from django.core.management.base import BaseCommand
from decimal import Decimal
from Catalogo.models import Product


class Command(BaseCommand):
    help = "Aumenta o reduce precios (por porcentaje o valor fijo)"

    def add_arguments(self, parser):
        parser.add_argument("value", type=str, help="Ej: +10%, -5%, +3, -2")

    def handle(self, *args, **kwargs):
        value = kwargs["value"]

        products = Product.objects.all()
        updated = 0

        if "%" in value:
            percent = Decimal(value.replace("%", ""))
            factor = Decimal(1) + (percent / Decimal(100))

            for p in products:
                p.price = p.price * factor
                updated += 1

        else:
            amount = Decimal(value)

            for p in products:
                p.price = p.price + amount
                updated += 1

        Product.objects.bulk_update(products, ["price"])

        self.stdout.write(self.style.SUCCESS(
            f"{updated} precios actualizados correctamente"
        ))