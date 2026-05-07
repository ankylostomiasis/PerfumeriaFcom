from .models import Product


def cart_context(request):
    cart = request.session.get("cart", {})
    normalized_cart = {}
    items = []
    total_price = 0
    total_quantity = 0

    for pid, raw_item in cart.items():
        quantity = raw_item.get("quantity", 0) if isinstance(raw_item, dict) else raw_item

        try:
            product = Product.objects.filter(id=int(pid)).first()
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if not product or quantity <= 0:
            continue

        normalized_cart[pid] = quantity
        subtotal = product.price * quantity
        total_price += subtotal
        total_quantity += quantity
        items.append(
            {
                "product": product,
                "id": product.id,
                "name": product.name,
                "quantity": quantity,
                "total_price": subtotal,
                "picture_url": product.picture.url if product.picture else "",
            }
        )

    if normalized_cart != cart:
        request.session["cart"] = normalized_cart

    return {
        "cart_items": items,
        "cart_total_quantity": total_quantity,
        "cart_total_price": total_price,
    }
