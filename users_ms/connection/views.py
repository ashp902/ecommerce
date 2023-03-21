from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

import requests
import json
import os

from .forms import ProductForm, OrderForm

from core.models import Address


# URL on which the product microservice runs on
PRODUCT_MS_URL = "http://127.0.0.1:8002/api/product/"
CART_MS_URL = "http://127.0.0.1:5000/"
ORDER_MS_URL = "http://127.0.0.1:8003/api/order/"
REVIEW_MS_URL = "http://127.0.0.1:5001/"


# Function to help writing urls faster
def append_url(*args):
    return "".join([*args])


# Convert response (from requests module) to response (from rest_framework)
def process_response(response):
    return Response(
        data=response.content,
        status=response.status_code,
        content_type=response.headers["Content-Type"],
    )


# Viewset with all product microservice views
class ProductViewSet(ViewSet):
    # GET, /api/connection/product/create/
    def create_product_page(
        self, request
    ):  # Renders a HTML page with an empty form to create a new product
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm()

            context = {
                "form": form,
            }

            return render(request, "product_form.html", context)

        # If no user is logged in or if the user is not a seller, display error
        return redirect("/api/core/404/")

    # POST, /api/connection/product/create/
    def create_product(self, request):  # Creates a new product
        # if user is logged in, perform validations
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm(request.POST)

            img = request.FILES["image"]
            img_extension = os.path.splitext(img.name)[1]

            path = "media/images/products/"

            if not os.path.exists(path):
                os.mkdir(path)

            # if form data is valid, make an api call to products service
            if form.is_valid():
                post_data = dict(request.POST.lists())

                data = {"user_id": request.user.id, **post_data}

                response = requests.post(
                    url=append_url(PRODUCT_MS_URL, "create/"), data=data
                )
                if response.status_code == 201:
                    product_id = response.content.decode()
                    img_save_path = path + str(product_id) + img_extension

                    with open(img_save_path, "wb+") as f:
                        for chunk in img.chunks():
                            f.write(chunk)

                    return redirect("http://127.0.0.1:8001/api/core/home/")
                else:
                    redirect("/api/core/404/")

            else:
                return redirect("/api/connection/product/create/")

        # if no user is logged in, display error
        return redirect("/api/core/404/")

    # GET, /api/connection/product/<int:id>/
    def product_page(self, request, id):
        response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), "/"))
        if response.status_code == 200:
            product = json.loads(json.loads(response.content))
            seller_id = product.pop("seller_id")

            can_edit = request.user.id == seller_id

            response = requests.get(
                url=append_url(REVIEW_MS_URL, "product/", str(id), "/")
            )
            reviews = json.loads(response.content)["reviews"]

            total_rating = "{:.1f}".format(
                sum([review["rating"] for review in reviews]) / len(reviews)
            )

            context = {
                "product": product,
                "product_tags": list(product["product_tags"][0].split(",")),
                "can_edit": can_edit,
                "user_id": request.user.id,
                "effective_price": product["price"] - product["discount"]
                if product["discount"] > 0
                else product["price"],
                "reviews": reviews,
                "total_rating": total_rating,
            }

            return render(request, "product_page.html", context)
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/product/change/<int:id>/
    def edit_product_page(self, request, id):
        # if user is logged in, make an api call to product service
        if request.user.id != None and request.user.user_role_id == 2:
            response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), "/"))

            product = json.loads(json.loads(response.content))
            seller_id = product.pop("seller_id")

            form = ProductForm(product)

            context = {
                "seller_id": seller_id,
                "form": form,
            }

            return render(request, "edit_product_page.html", context)

        # if no user is logged in, display error
        else:
            return redirect("/api/core/404/")

    # POST, /api/connection/product/change/<int:id>/
    def edit_product(self, request, id):
        # if user is logged in, perform validation
        if request.user.id != None and request.user.user_role_id == 2:
            form = ProductForm(request.POST)

            # if form data is valid, make an api call to products service
            if form.is_valid():
                data = dict(request.POST.lists())

                response = requests.post(
                    url=append_url(PRODUCT_MS_URL, "change/", str(id), "/"), data=data
                )

                if response.status_code == 200:
                    context = {
                        "form": form,
                    }

                    # re-render the form with updated data
                    return render(request, "edit_product_page.html", context)

                # if updating failed, display error
                else:
                    return redirect("/api/core/404/")

            # if form data is not valid, display error
            else:
                return render(request, "edit_product_page.html", context)

        # if no user is logged in, display error
        return redirect("/api/core/404/")

    # GET, /api/connection/product/all/
    def get_all_products(self, request):
        # make an api call to products service

        response = requests.get(url=append_url(PRODUCT_MS_URL, "all/"))
        if response.status_code == 200:
            data = json.loads(response.content)

            return Response(data=response.content)
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/myproducts/<int:id>/
    def get_all_products_with_user_id(self, request, id):
        # make an api call to products service
        response = requests.get(url=append_url(PRODUCT_MS_URL, "seller/", str(id)))
        if response.status_code == 200:
            data = json.loads(response.content)

            return Response(data=json.dumps(data))
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/product/search/
    def search_products(self, request):
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
                "user": request.user if request.user.id != None else False,
            }
            return render(request, "search.html", context)
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/product/delete/<int:id>/
    def delete_product(self, request, id):
        if request.user.id != None and request.user.user_role_id == 2:
            response = requests.delete(
                url=append_url(PRODUCT_MS_URL, "change/", str(id))
            )
            response = requests.delete(
                url=append_url(CART_MS_URL, "product/", str(id), "/")
            )

            return redirect("/api/core/home/")
        else:
            return redirect("/api/connection/product/" + str(id) + "/")


class CartViewSet(ViewSet):
    # POSt, /api/connection/cart/add/
    def add_to_cart(self, request):
        if request.user.id != None:
            data = {
                "user_id": request.POST["user_id"],
                "product_id": request.POST["product_id"],
                "quantity": request.POST["quantity"],
            }
            response = requests.post(url=append_url(CART_MS_URL, "add/"), data=data)
            return redirect("/api/connection/cart/")
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/cart/
    def get_cart(self, request):
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

            context = {
                "cart_items": cart_items,
                "history": history,
                "subtotal": subtotal,
            }
            return render(request, "cart.html", context)
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/cart/<int:id>/
    def cart_item_page(self, request, id):
        if request.user.id != None:
            response = requests.get(url=append_url(CART_MS_URL, "/item/", str(id)))
            cart_item = json.loads(response.content)

            response = requests.get(
                url=append_url(PRODUCT_MS_URL, str(cart_item["product_id"]), "/")
            )
            product = json.loads(json.loads(response.content))

            context = {"cart_item": cart_item, "product": product}
            return render(request, "cart_item.html", context)
        else:
            return redirect("/api/core/404/")

    # POST, /api/connection/cart/<int:id>/
    def edit_cart_item(self, request, id):
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

            context = {"cart_item": cart_item, "product": product}

            return render(request, "cart_item.html", context)
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/cart/delete/<int:id>/
    def remove_from_cart(self, request, id):
        if request.user.id != None:
            requests.delete(url=append_url(CART_MS_URL, "/item/", str(id), "/"))
            return redirect("/api/connection/cart/")
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/cart/addback/<int:id>/
    def add_back(self, request, id):
        if request.user.id != None:
            requests.put(url=append_url(CART_MS_URL, "/item/", str(id), "/"))
            return redirect("/api/connection/cart/")
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/cart/update/minus/<int:id>/
    def decrease_quantity(self, request, id):
        if request.user.id != None:
            requests.post(
                url=append_url(CART_MS_URL, "/item/", str(id), "/"),
                data={"quantity": -1},
            )
            return redirect("/api/connection/cart/")
        else:
            return redirect("/api/home/404/")

    # GET, /api/connection/cart/update/plus/<int:id>/
    def increase_quantity(self, request, id):
        if request.user.id != None:
            requests.post(
                url=append_url(CART_MS_URL, "/item/", str(id), "/"),
                data={"quantity": 1},
            )
            return redirect("/api/connection/cart/")
        else:
            return redirect("/api/core/404/")


class OrderViewSet(ViewSet):
    # GET, /api/connection/order/place/
    def chekout_page(self, request):
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

            context = {
                "cart_items": cart_items,
                "addresses": addresses,
                "subtotal": subtotal,
            }

            return render(request, "place_order.html", context)
        else:
            return redirect("/api/core/404/")

    # POST, /api/connection/order/place/
    def place_order(self, request):
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

            return redirect("/api/connection/order/all/")
        else:
            return redirect("/api/core/404/")

    # GET, /api/connection/order/all/
    def view_all_orders(self, request):
        if request.user:
            response = requests.get(
                url=append_url(ORDER_MS_URL, "all/" + str(request.user.id) + "/")
            )

            orders = json.loads(json.loads(response.content))

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
                        }
                        for order_item in order["order_items"]
                    ],
                }
                for order in orders
            ]

            context = {"orders": orders}

            return render(request, "orders_page.html", context)

    # def order_page(self, request, id):
    #     if request.user:
    #         response = requests.get(url=append_url(ORDER_MS_URL, str(id), "/"))

    #         order = json.loads(response.content)

    #         context = {
    #             "order": order,
    #         }

    #         return render(request, "order_page.html", context)

    # def cancel_order(self, request, id):
    #     if request.user:
    #         response = requests.post(url=append_url(ORDER_MS_URL, str(id), "/"))

    #         return redirect("/api/connection/order/all/")


class ReviewViewSet(ViewSet):
    # Post a review on a product
    def add_review(self, request, product_id):
        data = {
            "content": request.POST["content"],
            "rating": request.POST["rating"],
            "product_id": product_id,
            "user_id": request.user.id,
        }

        requests.post(url=append_url(REVIEW_MS_URL, "add/"), data=data)

        return redirect("/api/connection/product/" + str(product_id) + "/")
