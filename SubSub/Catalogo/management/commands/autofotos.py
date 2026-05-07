import requests
import time
import random

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db.models import Q

from Catalogo.models import Product
from ddgs import DDGS


class Command(BaseCommand):
    help = "Busca imágenes de perfumes automáticamente y las guarda"

    def handle(self, *args, **kwargs):
        productos = Product.objects.filter(
            Q(picture="") | Q(picture__isnull=True)
        )

        total = productos.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("Todos los perfumes ya tienen imagen 😏")
            )
            return

        self.stdout.write(
            self.style.WARNING(f"Procesando {total} perfumes...\n")
        )

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        for index, producto in enumerate(productos, start=1):
            try:
                nombre = producto.name.strip()

                # Pausa para evitar rate limit
                time.sleep(random.uniform(2, 4))

                query = f"{nombre} perfume bottle luxury"

                self.stdout.write(
                    f"[{index}/{total}] Buscando: {query}"
                )

                with DDGS(timeout=20) as ddgs:
                    resultados = list(
                        ddgs.images(
                            query=query,
                            max_results=10
                        )
                    )

                if not resultados:
                    self.stdout.write(
                        self.style.ERROR("❌ Sin resultados")
                    )
                    continue

                url_imagen = None

                for r in resultados:
                    url = r.get("image")

                    if url and url.startswith("http"):
                        url_imagen = url
                        break

                if not url_imagen:
                    self.stdout.write(
                        self.style.ERROR("❌ Sin URL válida")
                    )
                    continue

                respuesta = requests.get(
                    url_imagen,
                    headers=headers,
                    timeout=15
                )

                if respuesta.status_code != 200:
                    self.stdout.write(
                        self.style.ERROR("❌ Error descargando imagen")
                    )
                    continue

                if len(respuesta.content) < 8000:
                    self.stdout.write(
                        self.style.ERROR("❌ Imagen demasiado pequeña")
                    )
                    continue

                nombre_archivo = (
                    nombre.lower()
                    .replace(" ", "_")
                    .replace("/", "_")
                    [:80]
                    + ".jpg"
                )

                producto.picture.save(
                    nombre_archivo,
                    ContentFile(respuesta.content),
                    save=True
                )

                self.stdout.write(
                    self.style.SUCCESS("✅ Imagen guardada")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error: {str(e)}")
                )