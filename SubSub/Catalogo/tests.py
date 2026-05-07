from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Product


class StoreViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Arabes")
        self.product = Product.objects.create(
            name="Amber Oud Gold",
            description="Fragancia intensa con salida fresca y fondo ambarado.",
            price="65.00",
            category=self.category,
            stock=3,
        )
        self.sold_out = Product.objects.create(
            name="Club de Nuit",
            description="Opcion agotada para validar reglas de stock.",
            price="45.00",
            category=self.category,
            stock=0,
        )

    def test_categoria_endpoint_returns_serialized_products(self):
        response = self.client.get(reverse("categoria", args=[self.category.id]))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["categoria"], self.category.name)
        self.assertEqual(len(data["productos"]), 2)
        self.assertEqual(data["productos"][0]["detail_url"], reverse("product_detail", args=[data["productos"][0]["id"]]))

    def test_search_endpoint_matches_name_and_description(self):
        response = self.client.get(reverse("search_products"), {"q": "ambarado"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.product.name)

    def test_add_to_cart_requires_post(self):
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_respects_stock(self):
        url = reverse("add_to_cart", args=[self.product.id])

        for _ in range(3):
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "success")

        blocked = self.client.post(url)
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(blocked.json()["status"], "error")

    def test_add_to_cart_blocks_sold_out_products(self):
        response = self.client.post(reverse("add_to_cart", args=[self.sold_out.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

    def test_ask_for_stock_redirects_to_whatsapp(self):
        response = self.client.get(reverse("ask_for_stock"), {"product_id": self.sold_out.id})

        self.assertEqual(response.status_code, 302)
        self.assertIn("wa.me", response.url)
