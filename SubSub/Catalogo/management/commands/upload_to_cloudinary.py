from Catalogo.models import Product

def run():
    for product in Product.objects.all():
        if product.picture:
            product.picture = product.picture
            product.save()
            print(f"Subida: {product.name}")

    print("Migración terminada.")