from django.urls import path

from .views import ProductViewSet, CartViewSet, OrderViewSet, ReviewViewSet

PRODUCT_PATHS = [

    # Create new product page (only sellers)
    path('product/create/', ProductViewSet.as_view({
        'get': 'create_product_page',
        'post': 'create_product',
    })),

    # Product details page (any user)
    path('product/<int:id>/', ProductViewSet.as_view({
        'get': 'product_page',
    })),

    # Edit product page (only sellers only on products they created)
    path('product/change/<int:id>/', ProductViewSet.as_view({
        'get': 'edit_product_page',
        'post': 'edit_product',
    })),

    # Get all products (any user)
    path('product/all/', ProductViewSet.as_view({
        'get': 'get_all_products',
    })),

    # Get products created by a particular user
    path('product/myproducts/<int:id>', ProductViewSet.as_view({
        'get': 'get_all_products_with_user_id',
    })),

    path('product/search/', ProductViewSet.as_view({
        'get': 'search_products',
    }))

]

CART_PATHS = [

    path('cart/', CartViewSet.as_view({
        'get': 'get_cart',
    })),

    path('cart/<int:id>', CartViewSet.as_view({
        'get': 'cart_item_page',
        'post': 'edit_cart_item',
    })),

]

ORDER_PATHS = [
    path('order/place/', OrderViewSet.as_view({
        'get': 'place_order',
        'post': 'initiate_payment',
    })),

    path('order/all/', OrderViewSet.as_view({
        'get': 'view_all_orders',
    })),
    path('order/<int:id>/', OrderViewSet.as_view({
        'get': 'order_page',
        'post': 'cancel_order',
    }))
]

# REVIEW_PATHS = [
#     path(),
# ]

urlpatterns = PRODUCT_PATHS + CART_PATHS + ORDER_PATHS