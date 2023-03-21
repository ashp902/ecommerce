from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import datetime
import json

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@127.0.0.1:5432/review_db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Review(db.Model):
    __tablename__ = "reviews"

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
            "id": self.id,
            "posted_on": self.posted_on.isoformat(),
            "content": self.content,
            "rating": self.rating,
            "user_id": self.user_id,
            "product_id": self.product_id,
        }
        return obj


# Create a review
@app.route("/add/", methods=["POST"])
def add_review():
    review = Review(
        content=request.form["content"],
        rating=request.form["rating"],
        user_id=request.form["user_id"],
        product_id=request.form["product_id"],
    )
    db.session.add(review)
    db.session.commit()

    return "ok"


# Get reviews of a product
@app.route("/product/<int:product_id>/", methods=["GET"])
def get_reviews(product_id):
    reviews = Review.query.filter(Review.product_id == product_id)
    reviews = [review.to_dict() for review in reviews]

    return json.dumps({"reviews": reviews})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
