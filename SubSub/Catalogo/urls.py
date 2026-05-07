from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_click/<int:product_id>/', views.add_click, name='add_click'),
    path('view_cart/', views.get_cart_data, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('categoria/<int:categoria_id>/', views.categoria, name='categoria'),
    path('search/', views.search_products, name='search_products'),
    path('search_results/', views.search_products_page, name='search_results'),
    path('whatsapp_link/', views.whatsapp_link, name='whatsapp_link'),
    path('ask_for_stock/', views.ask_for_stock, name='ask_for_stock'),
]
