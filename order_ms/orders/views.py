from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import json
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from transactions.models import Transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer


# Generate a random transaction number
def random_generator():
    while True:
        x = "".join([str(random.randint(0, 9)) for _ in range(10)])
        try:
            Transaction.objects.get(id=x)
        except:
            return x


# POST, /api/order/place/
@swagger_auto_schema(
    operation_description="Create a new order",
    method="post",
)
@csrf_exempt
@api_view(["POST"])
def place_order(request):
    try:
        products = json.loads(request.data["products"])
    except:
        return Response("Invalid order data", status=status.HTTP_400_BAD_REQUEST)

    if len(products) != 0:
        transaction_number = random_generator()
        try:
            transaction = Transaction(
                transaction_id=transaction_number,
                sender="x",
                receiver="y",
                payment_type="card",
                payment_status="success",
                payment_time=datetime.now(),
            )
            transaction.save()

            order = Order(
                user_id=request.data["user_id"],
                address_id=request.data["address_id"],
                placed_time=datetime.now(),
                updated_time=datetime.now(),
                delivery_status=request.data["delivery_status"],
                total_amount=request.data["total_amount"],
                transaction_id=transaction_number,
            )
            order.save()

            for product in products:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product["product"]["id"],
                    price=product["product"]["price"],
                    discount=product["product"]["discount"],
                    quantity=product["quantity"],
                )
                order_item.save()
        except:
            return Response("Invalid order data", status=status.HTTP_400_BAD_REQUEST)

        return Response("Order received", status=status.HTTP_201_CREATED)
    else:
        return Response("Invalid order data", status=status.HTTP_400_BAD_REQUEST)


# GET, /api/order/all/<int:user_id>/
@swagger_auto_schema(
    operation_description="Fetches all orders of a user",
    method="get",
)
@api_view(["GET"])
def get_all_orders(request, user_id):
    orders = Order.objects.filter(user_id=user_id)

    if orders.count():
        orders = [
            {
                **order.to_dict(),
                "order_items": [
                    order_item.to_dict()
                    for order_item in OrderItem.objects.filter(order_id=order.id)
                ],
            }
            for order in orders
        ]

        return Response(json.dumps(orders), status=status.HTTP_200_OK)
    else:
        return Response("No records fetched", status=status.HTTP_204_NO_CONTENT)


# GET, POST, /api/order/<int:id>/
# @csrf_exempt
# @api_view(["GET", "POST"])
# def order_page(request, id):
#     order = Order.objects.get(id=id)
#     if request.method == "GET":
#         order = OrderSerializer(order)

#         return Response(order.data)
#     elif request.method == "POST":
#         order.delivery_status = "Cancelled"
#         order.save()

#         return Response("deleted")
