from django.urls import path
from .views import (
    create_buyer,
    create_seller,
    registration_page,
    login,
    home,
    profile,
    address,
    create_address,
    edit_address,
    delete_address,
    logout_user,
    no_page,
)

urlpatterns = [
    # Landing page
    # path('', landing_page, name='landing_page'),
    # Login page for all users
    path(
        "login/",
        login,
        name="login",
    ),
    path("register/", registration_page, name="register"),
    # Register page for buyers
    path(
        "register/buyer/",
        create_buyer,
        name="register_buyer",
    ),
    # Register page for sellers
    path(
        "register/seller/",
        create_seller,
        name="register_seller",
    ),
    # Only for debugging
    # Displays all users
    # path('all/', LoginRegisterViewSet.as_view({
    #     'get': 'all_users',
    # }), name='all'),
    # Profile page for all users
    path("profile/", profile, name="profile"),
    # Home page for all users
    path("home/", home, name="home"),
    # Address page for buyers
    path("address/", address, name="address"),
    # Create address page for buyers
    path("address/create/", create_address, name="address_form"),
    # Edit address page for buyers
    path("address/edit/<int:id>/", edit_address, name="edit_address"),
    # Delete address for buyers
    path("address/delete/<int:id>/", delete_address),
    # Logout
    path("logout/", logout_user, name="logout"),
    # 404 page
    path("404/", no_page, name="404"),
]
