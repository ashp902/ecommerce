from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import random
from datetime import datetime

from transactions.models import Transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer

def random_generator():
    while True:
        x = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        try:
            Transaction.objects.get(id=x)
        except:
            return x

# Create your views here.
@csrf_exempt
@api_view(['POST'])
def place_order(request):
    
    # print(request.data)
    # print(request.data['products'])
    products = json.loads(request.data['products'])
    # print(products, type(products[0]))

    transaction_number = random_generator()

    transaction = Transaction(
        transaction_id = transaction_number,
        sender = 'x',
        receiver = 'y',
        payment_type = 'card',
        payment_status = 'success',
        payment_time = datetime.now()
    )
    transaction.save()

    order = Order(
        user_id = request.data['user_id'],
        address_id = request.data['address_id'],
        placed_time = datetime.now(),
        updated_time = datetime.now(),
        delivery_status = request.data['delivery_status'],
        total_amount = request.data['total_amount'],
        transaction_id = transaction_number
    )
    order.save()

    for product in products:
        order_item = OrderItem(
            order_id = order.id,
            product_id = product['id'],
            price = product['price'],
            discount = product['discount'],
            quantity = product['quantity']
        )
        order_item.save()

    return HttpResponse('received')

@api_view(['GET'])
def get_all_orders(request, user_id):
    orders = Order.objects.filter(user_id=user_id)

    orders = OrderSerializer(orders, many=True)

    return Response(orders.data)

@csrf_exempt
@api_view(['GET', 'POST'])
def order_page(request, id):
    order = Order.objects.get(id=id)
    if request.method == 'GET':
        order = OrderSerializer(order)

        return Response(order.data)
    elif request.method == 'POST':
        order.delivery_status = 'Cancelled'
        order.save()

        return Response('deleted')
