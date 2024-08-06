from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import requests
import json
import os

from .forms import ProductForm, OrderForm

from core.models import Address


# PRODUCT_MS_URL = "http://127.0.0.1:8002/api/product/"
# CART_MS_URL = "http://127.0.0.1:5000/"
# ORDER_MS_URL = "http://127.0.0.1:8003/api/order/"
# REVIEW_MS_URL = "http://127.0.0.1:5001/"

PRODUCT_MS_URL = "http://products-ms:8002/api/product/"
CART_MS_URL = "http://cart-ms:5000/"
ORDER_MS_URL = "http://order-ms:8003/api/order/"
REVIEW_MS_URL = "http://review-ms:5001/"


def append_url(*args):
    return "".join([*args])


def process_response(response):
    return Response(
        data=response.content,
        status=response.status_code,
        content_type=response.headers["Content-Type"],
    )


def get_user(request):
    if request.user.id == None:
        return False
    return request.user


@swagger_auto_schema(
    operation_description="Renders create product page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Create a new product",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "product_name": openapi.Schema(type=openapi.TYPE_STRING),
            "product_description": openapi.Schema(type=openapi.TYPE_STRING),
            "product_tags": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
            ),
            "product_count": openapi.Schema(type=openapi.TYPE_INTEGER),
            "price": openapi.Schema(type=openapi.TYPE_NUMBER),
            "discount": openapi.Schema(type=openapi.TYPE_NUMBER),
        },
    ),
)
@api_view(["GET", "POST"])
def create_product(request):
    if request.method == "GET":
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm()

            errors = request.session.pop("errors", None)
            context = {
                "form": form,
                "user": get_user(request),
                "errors": errors,
            }

            return render(request, "product_form.html", context)

        request.session["errors"] = ["Access denied"]
        return redirect("/api/core/404/")
    elif request.method == "POST":
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm(request.POST)

            img = False
            try:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]

                path = "media/images/products/"

                if not os.path.exists(path):
                    os.mkdir(path)
            except:
                pass

            if form.is_valid():
                post_data = dict(request.POST.lists())

                data = {"user_id": request.user.id, **post_data}

                response = requests.post(
                    url=append_url(PRODUCT_MS_URL, "create/"), data=data
                )
                if response.status_code == 201:
                    if img:
                        product_id = response.content.decode()
                        img_save_path = path + str(product_id) + img_extension

                        with open(img_save_path, "wb+") as f:
                            for chunk in img.chunks():
                                f.write(chunk)

                    request.session["errors"] = ["Product created successfully."]
                    return redirect("http://127.0.0.1:8001/api/core/home/")
                else:
                    request.session["errors"] = [
                        "Failed to create a product. Server error."
                    ]
                    redirect("/api/core/404/")
            else:
                errors = form.errors
                error_messages = []
                for error in errors.values():
                    error_messages += error
                request.session["errors"] = error_messages
                return redirect("/api/connection/product/create/")

        request.session["errors"] = ["Access denied."]

        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Renders product page",
    method="get",
)
@api_view(["GET"])
def product_page(request, id):
    response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), "/"))
    if response.status_code == 200:
        print(response.content)
        product = json.loads(json.loads(response.content))
        seller_id = product.pop("seller_id")

        can_edit = request.user.id == seller_id

        response = requests.get(url=append_url(REVIEW_MS_URL, "product/", str(id), "/"))
        reviews = json.loads(response.content)["reviews"]
        if len(reviews) != 0:
            total_rating = "{:.1f}".format(
                sum([review["rating"] for review in reviews]) / len(reviews)
            )

        product_tags = list(product["product_tags"][0].split(","))
        related = []

        for tag in product_tags:
            response = requests.get(
                url=append_url(PRODUCT_MS_URL, "search/"), params={"search": tag}
            )
            if response.status_code == 200:
                products = json.loads(json.loads(response.content))["data"]

                for x in products:
                    if x["id"] != id:
                        related.append(
                            {
                                "effective_price": "{:.2f}".format(
                                    x["price"] - x["discount"]
                                ),
                                **x,
                            }
                        )
                        break

        context = {
            "product": product,
            "product_tags": product_tags,
            "can_edit": can_edit,
            "user": get_user(request),
            "effective_price": "{:.2f}".format(product["price"] - product["discount"])
            if product["discount"] > 0
            else product["price"],
            "reviews": reviews if len(reviews) > 0 else None,
            "total_rating": total_rating if len(reviews) > 0 else None,
            "related": related,
        }

        return render(request, "product_page.html", context)
    else:
        request.session["errors"] = ["Product not found."]
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Renders edit product page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Edit a product",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "product_name": openapi.Schema(type=openapi.TYPE_STRING),
            "product_description": openapi.Schema(type=openapi.TYPE_STRING),
            "product_tags": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
            ),
            "product_count": openapi.Schema(type=openapi.TYPE_INTEGER),
            "price": openapi.Schema(type=openapi.TYPE_NUMBER),
            "discount": openapi.Schema(type=openapi.TYPE_NUMBER),
        },
    ),
)
@api_view(["GET", "POST"])
def edit_product(request, id):
    if request.method == "GET":
        if request.user.id != None and request.user.user_role_id == 2:
            response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), "/"))

            product = json.loads(json.loads(response.content))
            seller_id = product.pop("seller_id")

            form = ProductForm(product)
            errors = request.session.pop("errors", None)

            context = {
                "seller_id": seller_id,
                "form": form,
                "product_id": id,
                "user": get_user(request),
                "errors": errors,
            }

            return render(request, "edit_product_page.html", context)

        else:
            return redirect("/api/core/404/")
    elif request.method == "POST":
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm(request.POST)
            img = False
            try:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]

                path = "media/images/products/"

                if not os.path.exists(path):
                    os.mkdir(path)
            except:
                pass

            if form.is_valid():
                data = dict(request.POST.lists())

                response = requests.post(
                    url=append_url(PRODUCT_MS_URL, "change/", str(id), "/"), data=data
                )

                if response.status_code == 200:
                    context = {
                        "form": form,
                        "user": get_user(request),
                    }
                    if img:
                        img_save_path = path + str(id) + img_extension

                        with open(img_save_path, "wb+") as f:
                            for chunk in img.chunks():
                                f.write(chunk)

                    request.session["errors"] = ["Updating product details successful."]
                    return redirect("/api/core/home/")

                else:
                    request.session["errors"] = ["Updating product details failed."]
                    return redirect("/api/core/404/")

            else:
                errors = form.errors
                error_messages = []
                for error in errors.values():
                    error_messages += error

                request.session["errors"] = error_messages
                return redirect("/api/connection/product/change/" + str(id) + "/")

        request.session["errors"] = ["Access denied."]
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Fetches all available products",
    method="get",
)
@api_view(["GET"])
def get_all_products(request):
    response = requests.get(url=append_url(PRODUCT_MS_URL, "all/"))
    if response.status_code == 200:
        data = json.loads(response.content)

        return Response(data=response.content)
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Fetches products created by a particular user",
    method="get",
)
@api_view(["GET"])
def get_all_products_with_user_id(request, id):
    response = requests.get(url=append_url(PRODUCT_MS_URL, "seller/", str(id)))
    if response.status_code == 200:
        data = json.loads(response.content)

        return Response(data=json.dumps(data))
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Fetched products that match the search query",
    method="get",
)
@api_view(["GET"])
def search_products(request):
    response = requests.get(
        url=append_url(PRODUCT_MS_URL, "search/"),
        params={"search": request.GET.get("search", "")},
    )
    if response.status_code == 200:
        products = json.loads(json.loads(response.content))["data"]

        products = [
            {
                "effective_price": "{:.2f}".format(
                    product["price"] - product["discount"]
                ),
                **product,
            }
            for product in products
        ]

        paginator = Paginator(products, 9)
        page = request.GET.get("page")
        products = paginator.get_page(page)

        context = {
            "user": request.user,
            "products": products,
            "user": get_user(request),
        }
        return render(request, "search.html", context)
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Deletes a product",
    method="get",
)
@api_view(["GET"])
def delete_product(request, id):
    if request.user.id != None and request.user.user_role_id == 2:
        requests.delete(url=append_url(PRODUCT_MS_URL, "change/", str(id)))
        requests.delete(url=append_url(CART_MS_URL, "product/", str(id), "/"))
        requests.delete(url=append_url(REVIEW_MS_URL, "product/", str(id), "/"))
        os.remove("media/images/products/" + str(id) + ".jpg")

        request.session["errors"] = ["Product deleted."]
        return redirect("/api/core/home/")
    else:
        request.session["errors"] = ["Access denied."]
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Add item to cart",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
)
@api_view(["POST"])
def add_to_cart(request):
    if request.user.id != None:
        data = {
            "user_id": request.POST["user_id"],
            "product_id": request.POST["product_id"],
            "quantity": request.POST["quantity"],
        }
        response = requests.post(url=append_url(CART_MS_URL, "add/"), data=data)
        request.session["errors"] = ["Item added to cart."]
        return redirect("/api/connection/cart/")
    else:
        request.session["errors"] = ["Failed to add to cart."]
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Render cart page",
    method="get",
)
@api_view(["GET"])
def get_cart(request):
    if request.user.id != None:
        response = requests.get(url=append_url(CART_MS_URL, str(request.user.id)))
        items = json.loads(response.content)

        cart_items = items["cart_items"]
        cart_items = [
            {
                **cart_item,
                "product": json.loads(
                    json.loads(
                        requests.get(
                            url=append_url(
                                PRODUCT_MS_URL, str(cart_item["product_id"]), "/"
                            )
                        ).content
                    )
                ),
            }
            for cart_item in cart_items
        ]

        history = items["history"]
        history = [
            {
                **history_item,
                "product": json.loads(
                    json.loads(
                        requests.get(
                            url=append_url(
                                PRODUCT_MS_URL, str(history_item["product_id"]), "/"
                            )
                        ).content
                    )
                ),
            }
            for history_item in history
        ]

        cart_items = [
            {
                "effective_price": "{:.2f}".format(
                    cart_item["product"]["price"] - cart_item["product"]["discount"]
                ),
                "product_total": "{:.2f}".format(
                    (cart_item["product"]["price"] - cart_item["product"]["discount"])
                    * cart_item["quantity"]
                ),
                **cart_item,
            }
            for cart_item in cart_items
        ]
        history = [
            {
                "effective_price": "{:.2f}".format(
                    history_item["product"]["price"]
                    - history_item["product"]["discount"]
                ),
                "product_total": "{:.2f}".format(
                    (
                        history_item["product"]["price"]
                        - history_item["product"]["discount"]
                    )
                    * history_item["quantity"]
                ),
                **history_item,
            }
            for history_item in history
        ]

        subtotal = 0
        for cart_item in cart_items:
            subtotal += float(cart_item["product_total"])

        subtotal = "{:.2f}".format(subtotal)

        errors = request.session.pop("errors", None)
        context = {
            "cart_items": cart_items,
            "history": history,
            "subtotal": subtotal,
            "user": get_user(request),
            "errors": errors,
        }
        return render(request, "cart.html", context)
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Renders cart item page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Updates a cart item",
    method="post",
)
@api_view(["GET", "POST"])
def cart_item(request, id):
    if request.method == "GET":
        if request.user.id != None:
            response = requests.get(url=append_url(CART_MS_URL, "/item/", str(id)))
            cart_item = json.loads(response.content)

            response = requests.get(
                url=append_url(PRODUCT_MS_URL, str(cart_item["product_id"]), "/")
            )
            product = json.loads(json.loads(response.content))

            context = {
                "cart_item": cart_item,
                "product": product,
                "user": get_user(request),
            }
            return render(request, "cart_item.html", context)
        else:
            return redirect("/api/core/404/")
    elif request.method == "POST":
        if request.user.id != None:
            quantity = request.POST["quantity"]
            response = requests.post(
                url=append_url(CART_MS_URL, "/item/", str(id), "/"),
                data={"quantity": quantity},
            )

            response = requests.get(url=append_url(CART_MS_URL, "/item/", str(id), "/"))
            cart_item = json.loads(response.content)

            response = requests.get(
                url=append_url(PRODUCT_MS_URL, str(cart_item["product_id"]), "/")
            )
            product = json.loads(json.loads(response.content))

            context = {
                "cart_item": cart_item,
                "product": product,
                "user": get_user(request),
            }

            return render(request, "cart_item.html", context)
        else:
            return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Remove item from cart",
    method="get",
)
@api_view(["GET"])
def remove_from_cart(request, id):
    if request.user.id != None:
        requests.delete(url=append_url(CART_MS_URL, "/item/", str(id), "/"))
        request.session["errors"] = ["Item removed from cart."]
        return redirect("/api/connection/cart/")
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Add a removed item back to cart",
    method="get",
)
@api_view(["GET"])
def add_back(request, id):
    if request.user.id != None:
        requests.put(url=append_url(CART_MS_URL, "/item/", str(id), "/"))
        request.session["errors"] = ["Item added back to cart."]
        return redirect("/api/connection/cart/")
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Decrement cart item quantity by 1",
    method="get",
)
@api_view(["GET"])
def decrease_quantity(request, id):
    if request.user.id != None:
        requests.post(
            url=append_url(CART_MS_URL, "/item/", str(id), "/"),
            data={"quantity": -1},
        )
        return redirect("/api/connection/cart/")
    else:
        return redirect("/api/home/404/")


@swagger_auto_schema(
    operation_description="Increment cart item quantity by 1",
    method="get",
)
@api_view(["GET"])
def increase_quantity(request, id):
    if request.user.id != None:
        requests.post(
            url=append_url(CART_MS_URL, "/item/", str(id), "/"),
            data={"quantity": 1},
        )
        return redirect("/api/connection/cart/")
    else:
        return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Renders checkout page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Create a new order",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"address": openapi.Schema(type=openapi.TYPE_INTEGER)},
    ),
)
@api_view(["GET", "POST"])
def place_order(request):
    if request.method == "GET":
        if request.user.id != None:
            response = requests.get(url=append_url(CART_MS_URL, str(request.user.id)))
            items = json.loads(response.content)
            cart_items = items["cart_items"]

            cart_items = [
                {
                    **cart_item,
                    "product": json.loads(
                        json.loads(
                            requests.get(
                                url=append_url(
                                    PRODUCT_MS_URL, str(cart_item["product_id"]), "/"
                                )
                            ).content
                        )
                    ),
                }
                for cart_item in cart_items
            ]
            cart_items = [
                {
                    "effective_price": "{:.2f}".format(
                        cart_item["product"]["price"] - cart_item["product"]["discount"]
                    ),
                    "product_total": "{:.2f}".format(
                        (
                            cart_item["product"]["price"]
                            - cart_item["product"]["discount"]
                        )
                        * cart_item["quantity"]
                    ),
                    **cart_item,
                }
                for cart_item in cart_items
            ]
            subtotal = 0
            for cart_item in cart_items:
                subtotal += float(cart_item["product_total"])

            subtotal = "{:.2f}".format(subtotal)

            if len(cart_items) == 0:
                return redirect("/api/connection/cart/")

            addresses = Address.objects.filter(user_id=request.user.id)

            errors = request.session.pop("errors", None)
            context = {
                "cart_items": cart_items,
                "addresses": addresses,
                "subtotal": subtotal,
                "user": get_user(request),
                "errors": errors,
            }

            return render(request, "place_order.html", context)
        else:
            return redirect("/api/core/404/")
    elif request.method == "POST":
        if request.user.id != None:
            response = requests.get(url=append_url(CART_MS_URL, str(request.user.id)))
            items = json.loads(response.content)
            cart_items = items["cart_items"]

            cart_items = [
                {
                    **cart_item,
                    "product": json.loads(
                        json.loads(
                            requests.get(
                                url=append_url(
                                    PRODUCT_MS_URL, str(cart_item["product_id"]), "/"
                                )
                            ).content
                        )
                    ),
                }
                for cart_item in cart_items
            ]
            cart_items = [
                {
                    "effective_price": "{:.2f}".format(
                        cart_item["product"]["price"] - cart_item["product"]["discount"]
                    ),
                    "product_total": "{:.2f}".format(
                        (
                            cart_item["product"]["price"]
                            - cart_item["product"]["discount"]
                        )
                        * cart_item["quantity"]
                    ),
                    **cart_item,
                }
                for cart_item in cart_items
            ]

            response = requests.post(
                url=append_url(PRODUCT_MS_URL, "place/"),
                data={"products": json.dumps(cart_items)},
            )
            if response.status_code != 200:
                return HttpResponse("Order failed")

            subtotal = 0
            for cart_item in cart_items:
                subtotal += float(cart_item["product_total"])

            subtotal = "{:.2f}".format(subtotal)
            order = {
                "user_id": request.user.id,
                "address_id": request.POST["address"],
                "delivery_status": "Order recieved",
                "total_amount": subtotal,
                "products": json.dumps(cart_items),
            }

            response = requests.post(url=append_url(ORDER_MS_URL, "place/"), data=order)
            if response.status_code == 201:
                for cart_item in cart_items:
                    requests.delete(
                        url=append_url(CART_MS_URL, "item/", str(cart_item["id"]), "/")
                    )

            request.session["errors"] = ["Order placed successfully."]
            return redirect("/api/connection/order/all/")
        else:
            return redirect("/api/core/404/")


@swagger_auto_schema(
    operation_description="Renders orders page",
    method="get",
)
@api_view(["GET"])
def view_all_orders(request):
    if request.user:
        try:
            response = requests.get(
                url=append_url(ORDER_MS_URL, "all/" + str(request.user.id) + "/")
            )

            orders = json.loads(json.loads(response.content))
        except:
            return render(request, "orders_page.html", context={"orders": []})

        orders = [
            {
                "user_id": order["user_id"],
                "address_id": order["address_id"],
                "delivery_status": order["delivery_status"],
                "total_amount": order["total_amount"],
                "order_items": [
                    {
                        "product": json.loads(
                            json.loads(
                                requests.get(
                                    url=append_url(
                                        PRODUCT_MS_URL,
                                        str(order_item["product_id"]),
                                        "/",
                                    )
                                ).content
                            )
                        ),
                        "product_id": order_item["product_id"],
                        "price": order_item["price"],
                        "discount": order_item["discount"],
                        "quantity": order_item["quantity"],
                        "effective_price": "{:.2f}".format(
                            order_item["price"] - order_item["discount"]
                        ),
                        "product_total": "{:.2f}".format(
                            (order_item["price"] - order_item["discount"])
                            * order_item["quantity"]
                        ),
                        "review": json.loads(
                            requests.get(
                                append_url(
                                    REVIEW_MS_URL,
                                    "/check/",
                                    str(order_item["product_id"]),
                                    "/",
                                    str(order["user_id"]),
                                )
                            ).content
                        ),
                    }
                    for order_item in order["order_items"]
                ],
            }
            for order in orders
        ]

        errors = request.session.pop("errors", None)

        context = {
            "orders": orders,
            "user": get_user(request),
            "errors": errors,
        }

        return render(request, "orders_page.html", context)


@swagger_auto_schema(
    operation_description="Create a review",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "rating": openapi.Schema(type=openapi.TYPE_INTEGER, enum=[1, 2, 3, 4, 5]),
            "content": openapi.Schema(type=openapi.TYPE_STRING),
            "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
)
@api_view(["POST"])
def add_review(request, product_id):
    data = {
        "content": request.POST["content"],
        "rating": request.POST["rating"],
        "product_id": product_id,
        "user_id": request.user.id,
    }

    requests.post(url=append_url(REVIEW_MS_URL, "add/"), data=data)
    request.session["errors"] = ["Review posted successfully."]
    return redirect("/api/connection/order/all/")


@swagger_auto_schema(
    operation_description="Delete a review",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
)
@api_view(["POST"])
def delete_review(request, product_id):
    data = {
        "product_id": product_id,
        "user_id": request.user.id,
    }

    requests.post(url=append_url(REVIEW_MS_URL, "delete/"), data=data)
    request.session["errors"] = ["Review deleted successfully."]
    return redirect("/api/connection/order/all/")
