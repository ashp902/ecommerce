from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5432/review_db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.BigInteger, primary_key=True)
    posted_on = db.Column(db.DateTime())
    content = db.Column(db.String())
    rating = db.Column(db.Integer())
    user_id = db.Column(db.BigInteger())
    product_id = db.Column(db.BigInteger())

    def __init__(self, content, rating, user_id, product_id):
        self.content = content
        self.rating = rating
        self.user_id = user_id
        self.product_id = product_id
        self.posted_on = datetime.now()
    
    def to_dict(self):
        obj = {
            'id': self.id,
            'posted_on': self.posted_on,
            'content': self.content,
            'rating': self.rating,
            'user_id': self.user_id,
            'product_id': self.product_id,
        }
        return obj
    

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    app.run(debug=True, port=5001)