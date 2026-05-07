def cart_to_json(cart):
    cart_items = []
    total_price = 0
    total_quantity = 0

    for pid, item in cart.items():
        item_total = round(item["quantity"] * item["price"], 2)
        total_price += item_total
        total_quantity += item["quantity"]

        cart_items.append({
            "id": pid,
            "name": item["name"],
            "slug": item.get("slug", ""),
            "category": item.get("category", ""),
            "quantity": item["quantity"],
            "price": float(item["price"]),
            "total_price": item_total,
            "picture_url": item.get("picture_url", ""),
        })

    return {
        "cart_items": cart_items,
        "cart_total_price": round(total_price, 2),
        "cart_total_quantity": total_quantity,
    }
