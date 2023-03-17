from django.urls import path
from .views import create_product, get_all_products_with_user_id, get_all_products, product_page, edit_product, place_order

urlpatterns = [

    # Create new product
    path('create/', create_product),

    # Get all products created by a seller
    path('seller/<int:id>', get_all_products_with_user_id),

    # Get all products
    path('all/', get_all_products),

    # Get a single product
    path('<int:id>/', product_page),

    # Edit an existing product
    path('change/<int:id>/', edit_product),

    path('place/', place_order),

]