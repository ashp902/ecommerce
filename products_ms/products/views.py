from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from datetime import datetime
import json

from .forms import ProductForm
from .models import Product
from .serializers import ProductSerializer
from inventory.models import InventoryItem


# POST, /api/product/create/
@swagger_auto_schema(
    operation_description="Creates a new product",
    method="post",
)
@csrf_exempt
@api_view(["POST"])
def create_product(request):
    product = Product(
        product_name=request.POST["product_name"],
        product_description=request.POST["product_description"],
        product_tags=[request.POST["product_tags"]],
        seller_id=request.POST["user_id"],
    )
    product.save()

    inventory_item = InventoryItem(
        product_id=product.id,
        count=request.POST["product_count"],
        price=request.POST["price"],
        last_updated=datetime.now(),
        last_stocked=datetime.now(),
        discount=request.POST["discount"],
    )
    inventory_item.save()

    return HttpResponse(product.id, status=status.HTTP_201_CREATED)


# GET, /api/product/seller/<int:id>/
@swagger_auto_schema(
    operation_description="Fetches all products by a particular user",
    method="get",
)
@api_view(["GET"])
def get_all_products_with_user_id(request, id):  # Optimize
    products = Product.objects.filter(seller_id=id, status="A")
    data = [
        {
            **InventoryItem.objects.filter(product_id=product.id)[0].to_dict(),
            **product.to_dict(),
        }
        for product in products
    ]

    return Response(json.dumps({"data": data}), status=status.HTTP_200_OK)


# GET, /api/product/all/
@swagger_auto_schema(
    operation_description="Fetches all products",
    method="get",
)
@api_view(["GET"])
def get_all_products(request):
    products = Product.objects.filter(status="A")
    data = [
        {
            **InventoryItem.objects.filter(product_id=product.id)[0].to_dict(),
            **product.to_dict(),
        }
        for product in products
    ]
    print(data)
    return Response(json.dumps({"data": data}), status=status.HTTP_200_OK)


# GET, /api/product/<int:id>/
@swagger_auto_schema(
    operation_description="Renders product page",
    method="get",
)
@api_view(["GET"])
def product_page(request, id):
    try:
        product = Product.objects.get(id=id)
        if product.status == "A":
            inventory_item = InventoryItem.objects.only(
                "count", "price", "discount"
            ).filter(product_id=id)[0]

            data = {
                "id": product.id,
                "product_name": product.product_name,
                "product_description": product.product_description,
                "product_tags": product.product_tags,
                "seller_id": product.seller_id,
                "product_count": inventory_item.count,
                "price": inventory_item.price,
                "discount": inventory_item.discount,
            }
            return Response(json.dumps(data), status=status.HTTP_200_OK)
        else:
            data = {
                "id": 0,
                "product_name": "Product deleted",
                "product_description": "",
                "product_tags": "",
                "seller_id": "",
                "product_count": "",
                "price": "",
                "discount": "",
            }
            return Response(json.dumps(data), status=status.HTTP_200_OK)
    except:
        data = {
            "id": 0,
            "product_name": "Product deleted",
            "product_description": "",
            "product_tags": "",
            "seller_id": "",
            "product_count": "",
            "price": "",
            "discount": "",
        }
        return Response(json.dumps(data), status=status.HTTP_200_OK)


# [POST, DELETE], /api/product/change/<int:id>/
@swagger_auto_schema(
    operation_description="Edit a product",
    method="post",
)
@swagger_auto_schema(
    operation_description="Delete a product",
    method="delete",
)
@csrf_exempt
@api_view(["POST", "DELETE"])
def edit_product(request, id):
    # POST method updates an existing product
    if request.method == "POST":
        product = Product.objects.get(id=id)

        product.product_name = request.POST["product_name"]
        product.product_description = request.POST["product_description"]
        product.product_tags = [request.POST["product_tags"]]

        product.save()

        inventory_item = InventoryItem.objects.filter(product_id=id)[0]

        inventory_item.count = request.POST["product_count"]
        inventory_item.price = request.POST["price"]
        inventory_item.last_updated = datetime.now()
        inventory_item.last_stocked = datetime.now()
        inventory_item.discount = request.POST["discount"]

        inventory_item.save()
        return HttpResponse("saved")

    # DELETE method deletes the product
    elif request.method == "DELETE":
        product = Product.objects.get(id=id)
        # inventory_item = InventoryItem.objects.filter(product_id=id)[0]

        product.status = "R"
        # inventory_item.delete()
        product.save()

        return HttpResponse("deleted")


@swagger_auto_schema(
    operation_description="Checks if the items in order are in stock",
    method="post",
)
@csrf_exempt
@api_view(["POST"])
def place_order(request):
    products = json.loads(request.data["products"])
    items = [
        (InventoryItem.objects.filter(product_id=product["product_id"])[0], product)
        for product in products
    ]
    for item, product in items:
        if item.count >= product["quantity"]:
            item.count -= product["quantity"]
        else:
            return HttpResponse("Not in stock", status=status.HTTP_406_NOT_ACCEPTABLE)
    for item, product in items:
        item.save()
    return HttpResponse("ok", status=status.HTTP_200_OK)


@swagger_auto_schema(
    operation_description="Fetches products that match the search query",
    method="get",
)
@api_view(["GET"])
def search(request):
    queries = list(request.GET.get("search", "").split())
    products = []

    for query in queries:
        results = Product.objects.filter(
            Q(product_tags__icontains=query)
            | Q(product_name__icontains=query)
            | Q(product_description__icontains=query)
        )
        for result in results:
            result = result.to_dict()
            if result not in products:
                products.append(result)

    products = [
        {
            **product,
            **InventoryItem.objects.filter(product_id=product["id"])[0].to_dict(),
        }
        for product in products
    ]

    return Response(json.dumps({"data": products}), status=status.HTTP_200_OK)
