from django.urls import path

from .views import (
    create_product,
    product_page,
    edit_product,
    get_all_products_with_user_id,
    get_all_products,
    search_products,
    delete_product,
)

from .views import (
    get_cart,
    cart_item,
    add_to_cart,
    remove_from_cart,
    add_back,
    decrease_quantity,
    increase_quantity,
)

from .views import place_order, view_all_orders

from .views import add_review, delete_review

PRODUCT_PATHS = [
    # Create new product page (only sellers)
    path(
        "product/create/",
        create_product,
    ),
    # Product details page (any user)
    path(
        "product/<int:id>/",
        product_page,
    ),
    # Edit product page (only sellers only on products they created)
    path(
        "product/change/<int:id>/",
        edit_product,
    ),
    # Get all products (any user)
    path(
        "product/all/",
        get_all_products,
    ),
    # Get products created by a particular user
    path(
        "product/myproducts/<int:id>",
        get_all_products_with_user_id,
    ),
    # Search for products
    path(
        "product/search/",
        search_products,
    ),
    # Delete a product
    path("product/delete/<int:id>/", delete_product),
]

CART_PATHS = [
    # Get cart for a user
    path(
        "cart/",
        get_cart,
    ),
    # Get a single cart item, edit a cart item
    path(
        "cart/<int:id>/",
        cart_item,
    ),
    # Add a product to cart
    path(
        "cart/add/",
        add_to_cart,
    ),
    # Delete an item from cart
    path(
        "cart/delete/<int:id>/",
        remove_from_cart,
    ),
    # Add back an item to cart
    path(
        "cart/addback/<int:id>/",
        add_back,
    ),
    # Decrement an item quantity by 1
    path(
        "cart/update/minus/<int:id>/",
        decrease_quantity,
    ),
    # Increment an item quantity by 1
    path(
        "cart/update/plus/<int:id>/",
        increase_quantity,
    ),
]

ORDER_PATHS = [
    # Checkout page, place order
    path(
        "order/place/",
        place_order,
    ),
    # Get all orders of a user
    path(
        "order/all/",
        view_all_orders,
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
        add_review,
    ),
    path(
        "review/delete/<int:product_id>/",
        delete_review,
    ),
]

urlpatterns = PRODUCT_PATHS + CART_PATHS + ORDER_PATHS + REVIEW_PATHS
