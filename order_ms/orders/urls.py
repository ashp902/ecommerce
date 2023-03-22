from django.urls import path
from .views import place_order, get_all_orders  # , order_page

urlpatterns = [
    path("place/", place_order),
    path("all/<int:user_id>/", get_all_orders),
    # path("<int:id>/", order_page),
]
