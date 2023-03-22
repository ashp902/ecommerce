from django.test import TestCase
from datetime import datetime
from .models import Order, OrderItem
from transactions.models import Transaction
import json
from .views import random_generator

mock_order = {
    "user_id": 2,
    "address_id": 1,
    "delivery_status": "Order recieved",
    "total_amount": "52.00",
    "products": json.dumps(
        [
            {
                "effective_price": "52.00",
                "product_total": "52.00",
                "id": 13,
                "user_id": 2,
                "product_id": 5,
                "added_time": datetime.now().isoformat(),
                "quantity": 1,
                "status": "In cart",
                "product": {
                    "id": 5,
                    "product_name": "jfjfj",
                    "product_description": "jhjh",
                    "product_tags": ["jhhj"],
                    "seller_id": 3,
                    "product_count": 475,
                    "price": 56.0,
                    "discount": 4.0,
                },
            }
        ]
    ),
}

# effective priece, prodi=uct total, product, cart_item


class Tests(TestCase):
    def setUp(self):
        transaction = Transaction.objects.create(
            transaction_id=random_generator(),
            sender="x",
            receiver="y",
            payment_type="card",
            payment_status="success",
            payment_time=datetime.now(),
        )
        order = Order.objects.create(
            user_id=2,
            address_id=1,
            delivery_status="Order received",
            total_amount="52.00",
            placed_time=datetime.now(),
            updated_time=datetime.now(),
            transaction_id=transaction.transaction_id,
        )
        order_item = OrderItem.objects.create(
            order_id=order.id,
            product_id=5,
            price=56.00,
            discount=4.0,
            quantity=1,
        )

    def test_to_place_order(self):
        response = self.client.post("/api/order/place/", mock_order)
        self.assertEqual(response.status_code, 201)

    def test_to_deny_bad_request(self):
        response = self.client.post("/api/order/place/", {})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/order/place/", {"products": []})
        self.assertEqual(response.status_code, 400)

    def test_to_get_all_orders(self):
        response = self.client.get("/api/order/all/" + str(2) + "/")
        self.assertEqual(response.status_code, 200)

    def test_to_return_regret(self):
        response = self.client.get("/api/order/all/" + str(24) + "/")
        self.assertEqual(response.status_code, 204)
