from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin

from datetime import datetime
import json

app = Flask(__name__)

# cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5432/cart_db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class CartItem(db.Model):
    __tablename__ = 'cartitems'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger())
    product_id = db.Column(db.BigInteger())
    added_time = db.Column(db.DateTime())
    quantity = db.Column(db.Integer())
    status = db.Column(db.String())

    def __init__(self, user_id, product_id, quantity, status):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.status = "In cart" if status == 1 else "Removed"
        self.added_time = datetime.now()
    
    def to_dict(self):
        obj = {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'added_time': self.added_time.isoformat(),
            'quantity': self.quantity,
            'status': self.status,
        }
        return obj

def clean_history(cart_item):
    deleted_items = CartItem.query.filter(CartItem.user_id == cart_item.user_id, CartItem.status == 'Removed').order_by(CartItem.added_time)
    while len(deleted_items) > 10:
        db.session.delete(deleted_items.pop(0))


# @app.route('/')
# def home():
#     return "Hello"

@app.route('/add/', methods=['POST'])
def add_to_cart():
    cart_item = CartItem(
        user_id=request.form.get('user_id'),
        product_id=request.form.get('product_id'),
        quantity=request.form.get('quantity'),
        status=1
    )
    db.session.add(cart_item)
    db.session.commit()
    return "request"

@app.route('/<int:user_id>/', methods=['GET'])
def get_cart(user_id):
    cart_items = CartItem.query.filter(CartItem.user_id == user_id, CartItem.status == 'In cart')
    history = CartItem.query.filter(CartItem.user_id == user_id, CartItem.status == 'Removed')
    return json.dumps({
        'cart_items': [cart_item.to_dict() for cart_item in cart_items],
        'history': [item.to_dict() for item in history]
    })

@app.route('/item/<int:id>/', methods=['GET', 'POST', 'DELETE'])
def get_cart_item(id):
    cart_item = CartItem.query.get(id)
    if request.method == 'GET':
        return json.dumps(cart_item.to_dict())
    elif request.method == 'POST':
        cart_item.quantity = request.form.get('quantity')
        db.session.add(cart_item)
        db.session.commit()
        return 'Updated'
    elif request.method == 'DELETE':
        cart_item.status = 'Removed'
        db.session.commit()
        clean_history(cart_item)
        return 'Deleted'

@app.route('/product/<int:id>/', methods=['DELETE'])
def remove_product(id):
    cart_items = CartItem.query.filter(CartItem.product_id == id)
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return 'Cleaned carts'

if __name__ == '__main':
    app.run()