from django.urls import path

from .views import ProductViewSet, CartViewSet, OrderViewSet, ReviewViewSet

PRODUCT_PATHS = [
    # Create new product page (only sellers)
    path(
        "product/create/",
        ProductViewSet.as_view(
            {
                "get": "create_product_page",
                "post": "create_product",
            }
        ),
    ),
    # Product details page (any user)
    path(
        "product/<int:id>/",
        ProductViewSet.as_view(
            {
                "get": "product_page",
            }
        ),
    ),
    # Edit product page (only sellers only on products they created)
    path(
        "product/change/<int:id>/",
        ProductViewSet.as_view(
            {
                "get": "edit_product_page",
                "post": "edit_product",
            }
        ),
    ),
    # Get all products (any user)
    path(
        "product/all/",
        ProductViewSet.as_view(
            {
                "get": "get_all_products",
            }
        ),
    ),
    # Get products created by a particular user
    path(
        "product/myproducts/<int:id>",
        ProductViewSet.as_view(
            {
                "get": "get_all_products_with_user_id",
            }
        ),
    ),
    # Search for products
    path(
        "product/search/",
        ProductViewSet.as_view(
            {
                "get": "search_products",
            }
        ),
    ),
    # Delete a product
    path("product/delete/<int:id>/", ProductViewSet.as_view({"get": "delete_product"})),
]

CART_PATHS = [
    # Get cart for a user
    path(
        "cart/",
        CartViewSet.as_view(
            {
                "get": "get_cart",
            }
        ),
    ),
    # Get a single cart item, edit a cart item
    path(
        "cart/<int:id>/",
        CartViewSet.as_view(
            {
                "get": "cart_item_page",
                "post": "edit_cart_item",
            }
        ),
    ),
    # Add a product to cart
    path(
        "cart/add/",
        CartViewSet.as_view(
            {
                "post": "add_to_cart",
            }
        ),
    ),
    # Delete an item from cart
    path(
        "cart/delete/<int:id>/",
        CartViewSet.as_view(
            {
                "get": "remove_from_cart",
            }
        ),
    ),
    # Add back an item to cart
    path(
        "cart/addback/<int:id>/",
        CartViewSet.as_view(
            {
                "get": "add_back",
            }
        ),
    ),
    # Decrement an item quantity by 1
    path(
        "cart/update/minus/<int:id>/",
        CartViewSet.as_view(
            {
                "get": "decrease_quantity",
            }
        ),
    ),
    # Increment an item quantity by 1
    path(
        "cart/update/plus/<int:id>/",
        CartViewSet.as_view(
            {
                "get": "increase_quantity",
            }
        ),
    ),
]

ORDER_PATHS = [
    # Checkout page, place order
    path(
        "order/place/",
        OrderViewSet.as_view(
            {
                "get": "checkout_page",
                "post": "place_order",
            }
        ),
    ),
    # Get all orders of a user
    path(
        "order/all/",
        OrderViewSet.as_view(
            {
                "get": "view_all_orders",
            }
        ),
    ),
    # path(
    #     "order/<int:id>/",
    #     OrderViewSet.as_view(
    #         {
    #             "get": "order_page",
    #             "post": "cancel_order",
    #         }
    #     ),
    # ),
]

REVIEW_PATHS = [
    path(
        "review/add/<int:product_id>/",
        ReviewViewSet.as_view(
            {
                "post": "add_review",
            }
        ),
    ),
]

urlpatterns = PRODUCT_PATHS + CART_PATHS + ORDER_PATHS + REVIEW_PATHS
