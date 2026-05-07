import urllib.parse
import random
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Category, Product


WHATSAPP_NUMBER = "584120741379"


def serialize_product(product, *, description_limit=88):
    description = (product.description or "").strip()
    if description_limit and len(description) > description_limit:
        description = f"{description[:description_limit].rstrip()}..."

    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "description": description,
        "picture_url": product.picture.url if product.picture else "",
        "detail_url": reverse("product_detail", args=[product.id]),
        "category": product.category.name if product.category else "Fragancia",
        "stock": product.stock,
    }


def get_homepage_context():
    products = Product.objects.select_related("category").all()
    categories = Category.objects.order_by("name")
    featured_products = random.sample(list(products), min(8, products.count())) if products.count() > 0 else []
    available_products = products.filter(stock__gt=0)

    return {
        "productos": products,
        "categorias": categories,
        "featured_products": featured_products,
        "hero_product": featured_products[0] if featured_products else None,
        "in_stock_count": available_products.count(),
    }


def homepage(request):
    return render(request, "homepage.html", get_homepage_context())


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)
    product.views_count += 1
    product.save(update_fields=["views_count"])

    related_products = (
        Product.objects.select_related("category")
        .filter(category=product.category)
        .exclude(id=product.id)[:4]
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def categoria(request, categoria_id):
    categoria_obj = get_object_or_404(Category, id=categoria_id)
    productos = Product.objects.select_related("category").filter(category=categoria_obj)

    return JsonResponse(
        {
            "categoria": categoria_obj.name,
            "productos": [serialize_product(producto) for producto in productos],
        }
    )


def add_click(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.clicks_count += 1
    product.save(update_fields=["clicks_count"])
    return JsonResponse({"status": "success", "clicks_count": product.clicks_count})


def iter_valid_cart_items(cart):
    for product_id, raw_quantity in cart.items():
        quantity = raw_quantity.get("quantity", 0) if isinstance(raw_quantity, dict) else raw_quantity

        try:
            quantity = int(quantity)
            product = Product.objects.filter(id=int(product_id)).first()
        except (TypeError, ValueError):
            continue

        if quantity <= 0 or product is None:
            continue

        yield product, quantity


def build_cart_response(cart):
    items = []
    total_price = 0
    total_quantity = 0

    for product, quantity in iter_valid_cart_items(cart):
        subtotal = product.price * quantity
        total_price += subtotal
        total_quantity += quantity
        items.append(
            {
                "id": product.id,
                "name": product.name,
                "quantity": quantity,
                "total_price": float(subtotal),
                "picture_url": product.picture.url if product.picture else "",
                "stock": product.stock,
            }
        )

    return {
        "status": "success",
        "cart_items": items,
        "cart_total_price": float(total_price),
        "cart_total_quantity": total_quantity,
    }


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    product_key = str(product_id)
    current_quantity = cart.get(product_key, 0)

    if isinstance(current_quantity, dict):
        current_quantity = current_quantity.get("quantity", 0)

    if current_quantity >= product.stock and product.stock > 0:
        return JsonResponse(
            {
                "status": "error",
                "message": "Ya agregaste el maximo disponible de este producto.",
            }
        )

    if product.stock <= 0:
        return JsonResponse(
            {
                "status": "error",
                "message": "Este producto no tiene stock disponible en este momento.",
            }
        )

    cart[product_key] = current_quantity + 1
    request.session["cart"] = cart
    return JsonResponse(build_cart_response(cart))


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return JsonResponse(build_cart_response(cart))


@require_POST
def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})
    product_key = str(product_id)

    if product_key not in cart:
        return JsonResponse({"status": "error", "message": "Producto no encontrado"})

    quantity = cart[product_key] if isinstance(cart[product_key], int) else cart[product_key].get("quantity", 1)

    if quantity > 1:
        cart[product_key] = quantity - 1
    else:
        del cart[product_key]

    request.session["cart"] = cart
    return JsonResponse(build_cart_response(cart))


def search_products(request):
    query = request.GET.get("q", "").strip()
    products = (
        Product.objects.select_related("category")
        .filter(Q(name__icontains=query) | Q(description__icontains=query))
        if query
        else Product.objects.none()
    )
    return JsonResponse([serialize_product(product) for product in products], safe=False)


def search_products_page(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.select_related("category").all()

    if query:
        words = query.split()

        for word in words:
            products = products.filter(
                Q(name__icontains=word) |
                Q(description__icontains=word)
            )

    return render(
        request,
        "search_results.html",
        {
            "products": products,
            "query": query,
        },
    )

def get_cart_data(request):
    cart = request.session.get("cart", {})
    return JsonResponse(build_cart_response(cart))


def whatsapp_link(request):
    cart = request.session.get("cart", {})
    items = [f"{quantity} x {product.name}" for product, quantity in iter_valid_cart_items(cart)]

    if not items:
        context = get_homepage_context()
        context["message"] = "Tu carrito esta vacio. Agrega al menos una fragancia antes de continuar a WhatsApp."
        return render(request, "homepage.html", context)

    message = "Hola, me interesan estas fragancias:\n" + "\n".join(items)
    encoded_message = urllib.parse.quote(message)

    return redirect(f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}")


def ask_for_stock(request):
    product_id = request.GET.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    message = f"Hola, quisiera consultar disponibilidad para: {product.name}"
    encoded_message = urllib.parse.quote(message)
    return redirect(f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}")
