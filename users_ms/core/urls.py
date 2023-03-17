from django.urls import path
from .views import landing_page, LoginRegisterViewSet, home, profile, address, create_address, edit_address, logout_user

urlpatterns = [

    # Landing page
    path('', landing_page, name='landing_page'),

    # Login page for all users
    path('login/', LoginRegisterViewSet.as_view({
    
        'post': 'login_user',

        'get': 'login_page'

    }), name='login'),


    path('register/', LoginRegisterViewSet.as_view({
        'get': 'registration_page'
    })),


    # Register page for buyers
    path('register/buyer/', LoginRegisterViewSet.as_view({
    
        'post': 'create_buyer',

    }), name='register_buyer'),

    # Register page for sellers
    path('register/seller/', LoginRegisterViewSet.as_view({
    
        'post': 'create_seller',

    }), name='register_seller'),


    # Only for debugging
    # Displays all users
    # path('all/', LoginRegisterViewSet.as_view({
    
    #     'get': 'all_users',

    # }), name='all'),


    # Profile page for all users
    path('profile/', profile, name='profile'),


    # Home page for all users
    path('home/', home, name='home'),


    # Address page for buyers
    path('address/', address, name='address'),


    # Create address page for buyers
    path('address/create/', create_address, name='address_form'),


    # Edit address page for buyers
    path('address/edit/<int:id>/', edit_address, name='edit_address'),

    path('logout/', logout_user, name='logout'),

]
