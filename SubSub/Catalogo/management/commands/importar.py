import csv
import os
from django.core.management.base import BaseCommand
from Catalogo.models import Product

class Command(BaseCommand):
    help = "Importa productos desde un CSV"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, "catalogo.csv")

        with open(csv_path, encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                Product.objects.create(
                    name=row["product"],
                    price=float(row["price"]),
                    description="Fragancia original",
                    stock=10
                )

        self.stdout.write(self.style.SUCCESS("Productos importados con éxito 🔥"))