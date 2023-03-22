from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import requests
import json
import os

from .models import User, Address
from .serializers import UserSerializer, RegisterUserSeraializer
from .forms import RegisterUserForm, LoginUserForm, EditUserForm, AddressForm


# # Landing page view
# def landing_page(request):
#     all_products = requests.get(url="http://127.0.0.1:8001/api/connection/product/all/")
#     all_products = json.loads(json.loads(all_products.content))
#     print(request.user.id)
#     context = {
#         "all_products": all_products,
#         "user": request.user.id != None,
#     }
#     return render(request, "landing_page.html", context)


# Views for login and register pages
# class LoginRegisterViewSet(viewsets.ViewSet):
# GET, /api/core/all/
# def all_users(self, request):  # Displays data of all users
#     users = User.objects.all()
#     serializer = UserSerializer(users, many=True)

#     return Response(serializer.data)


# POST, /api/core/register/buyer/
@swagger_auto_schema(
    operation_description="Creates a user with buyer role",
    method="post",
    # request_body=openapi.Schema(
    #     type=openapi.TYPE_OBJECT,
    #     properties={
    #         "first_name": openapi.Schema(type=openapi.TYPE_STRING),
    #     },
    # ),
    # manual_parameters=[
    #     openapi.Parameter("first_name", openapi.IN_QUERY, type=openapi.TYPE_STRING)
    # ],
    request_body=RegisterUserSeraializer,
)
@api_view(["POST"])
def create_buyer(request):  # Registers a new buyer
    # if request.method == "GET":
    #     print(request.body)
    #     return HttpResponse(request.build_absolute_uri())

    form = RegisterUserForm(request.POST)

    # if all fields are valid save and login buyer
    if form.is_valid():
        form.save_buyer()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=raw_password)

        # if authentication is successful, redirect to home page
        if user is not None:
            login(request, user)
            return redirect("home")

        # if authentication fails, redirect to login page
        else:
            return redirect("login")

    # if any field is not valid, redirect to register page
    else:
        return redirect("register_buyer")


# POST, /api/core/register/seller/
@swagger_auto_schema(
    operation_description="Create a user with seller role",
    method="post",
)
@api_view(["POST"])
def create_seller(request):  # Registers a new seller
    form = RegisterUserForm(request.POST)

    # if all fields are valid save and login seller
    if form.is_valid():
        form.save_seller()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=raw_password)

        # if authentication is successful, redirect to home page
        if user is not None:
            login(request, user)
            return redirect("home")

        # if authentication fails, redirect to login page
        else:
            return redirect("login")

    # if any field is not valid, redirect to register page
    else:
        return redirect("register_seller")


# GET, /api/core/register/
@swagger_auto_schema(
    operation_description="Renders registration page",
    method="get",
)
@api_view(["GET"])
def registration_page(request):
    # if any user is already logged in, redirect to home page
    if request.user.id != None:
        return redirect("home")

    form = RegisterUserForm()

    context = {
        "form": form,
        "user": request.user.id != None,
    }

    return render(request, "register.html", context)


class Login(APIView):
    # POST, /api/core/login/
    # @swagger_auto_schema(
    #     operation_description="Logs in a user",
    #     method="post",
    # )
    # @api_view(["POST"])
    def post(self, request):
        form = LoginUserForm(request.POST)

        email = form["email"].value()
        raw_password = form["password"].value()

        user = authenticate(email=email, password=raw_password)

        # if authentication is successful, redirect to home page
        if user is not None:
            login(request, user)
            return redirect("home")

        # if authentication fails, display error
        else:
            return HttpResponse("not valid")

    # GET, /api/core/login/
    # @swagger_auto_schema(
    #     operation_description="Renders login page",
    #     method="get",
    # )
    # @api_view(["GET"])
    def get(self, request):
        # if any user is already logged in, redirect to home page
        if request.user.id != None:
            return redirect("home")

        form = LoginUserForm()

        context = {
            "form": form,
            "user": request.user.id != None,
        }

        return render(request, "login.html", context)


# Home page view, /api/core/home/
@swagger_auto_schema(
    operation_description="Renders home page",
    method="get",
)
@api_view(["GET"])
def home(request):
    # if user is logged in
    if request.user.id != None:
        user = User.objects.get(id=request.user.id)
        # if user is a buyer
        if user.user_role_id == 1:
            products = requests.get(
                url="http://127.0.0.1:8001/api/connection/product/all/"
            )
            products = json.loads(json.loads(json.loads(products.content)))["data"]
            products = [
                {
                    "effective_price": "{:.2f}".format(
                        product["price"] - product["discount"]
                    ),
                    **product,
                }
                for product in products
            ]

            paginator = Paginator(products, 9)
            page = request.GET.get("page")
            products = paginator.get_page(page)

            context = {
                "products": products,
                "user": user,
            }
            return render(request, "landing_page.html", context)

        # if user is a seller
        elif user.user_role_id == 2:
            products = requests.get(
                url="http://127.0.0.1:8001/api/connection/product/myproducts/"
                + str(user.id)
            )
            products = json.loads(json.loads(json.loads(products.content)))["data"]
            products = [
                {
                    "effective_price": "{:.2f}".format(
                        product["price"] - product["discount"]
                    ),
                    **product,
                }
                for product in products
            ]

            paginator = Paginator(products, 9)
            page = request.GET.get("page")
            products = paginator.get_page(page)

            context = {
                "products": products,
                "user": user,
            }
            return render(request, "landing_page.html", context)
        elif user.user_role_id == 3:
            return redirect("/admin")
    # if no user is logged in
    else:
        products = requests.get(url="http://127.0.0.1:8001/api/connection/product/all/")
        products = json.loads(json.loads(json.loads(products.content)))["data"]
        products = [
            {
                "effective_price": "{:.2f}".format(
                    product["price"] - product["discount"]
                ),
                **product,
            }
            for product in products
        ]

        paginator = Paginator(products, 9)
        page = request.GET.get("page")
        products = paginator.get_page(page)

        context = {
            "products": products,
            "user": request.user.id != None,
        }
        return render(request, "landing_page.html", context)


# Profile page, /api/core/profile/
@swagger_auto_schema(
    operation_description="Renders profile page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Updates user details",
    method="post",
)
@login_required
@api_view(["GET", "POST"])
def profile(request):
    # GET request displays the profile page with user details
    if request.method == "GET":
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        # Populate form with user details
        data = {
            "email": user.email,
            "username": user.username,
            "password1": "",
            "password2": "",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth,
            "gender": user.gender,
        }
        form = EditUserForm(data)

        context = {
            "form": form,
            "user": user,
        }

        return render(request, "profile.html", context)

    # POST request updates the user details and displays the profile page
    elif request.method == "POST":
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        form = EditUserForm(request.POST)

        # Update the user instance with new details
        user.first_name = form["first_name"].value()
        user.last_name = form["last_name"].value()
        user.date_of_birth = form["date_of_birth"].value()
        user.gender = form["gender"].value()

        if (
            form["password1"].value()
            and form["password2"].value()
            and form["password1"].value() == form["password2"].value()
        ):
            user.set_password(form["password1"].value())

        user.save()

        context = {
            "form": form,
            "user": user,
        }

        img = request.FILES["image"]
        img_extension = os.path.splitext(img.name)[1]

        path = "media/images/users/"

        if not os.path.exists(path):
            os.mkdir(path)

        img_save_path = path + str(user.id) + img_extension

        with open(img_save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)

        return render(request, "profile.html", context)


# Address page, only available for buyers, /api/core/address/
@swagger_auto_schema(
    operation_description="Renders addresses page",
    method="get",
)
@login_required
@api_view(["GET"])
def address(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    # If user is not a buyer, display error
    if user.user_role_id != 1:
        return redirect("404")

    # GET request displays all addresses of the current user
    if request.method == "GET":
        addresses = Address.objects.filter(user_id=user_id)

        context = {
            "addresses": addresses,
            "user": user,
        }

        return render(request, "address.html", context)


# Create new address page, /api/core/address/create/
@swagger_auto_schema(
    operation_description="Renders create address form",
    method="get",
)
@swagger_auto_schema(
    operation_description="Creates a new address",
    method="post",
)
@login_required
@api_view(["GET", "POST"])
def create_address(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    # If user is not a buyer, display error
    if user.user_role_id != 1:
        return redirect("404")

    # GET request displays form to create a new address
    if request.method == "GET":
        form = AddressForm()
        context = {
            "form": form,
            "user": user,
        }

        return render(request, "address_form.html", context)

    # POST request creates a new address
    elif request.method == "POST":
        form = AddressForm(request.POST)

        # If all fields are valid, save the address to the current user
        if form.is_valid():
            form.save_with_user_id(request.user.id)

            # Redirect to address page
            return redirect("address")

        # If any field is not valid, redirect to create address page
        else:
            return redirect("address_form")


# Edit address page, /api/core/address/edit/<int:id>/
@swagger_auto_schema(
    operation_description="Renders edit address page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Updates the address details",
    method="post",
)
@login_required
@api_view(["GET", "POST"])
def edit_address(request, id):
    # GET request displays a form to edit the selected address
    if request.method == "GET":
        address = Address.objects.get(id=id)

        # Populate the form with current address data
        data = {
            "address_name": address.address_name,
            "door_no": address.door_no,
            "street": address.street,
            "area": address.area,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "pincode": address.pincode,
        }
        form = AddressForm(data)

        context = {
            "form": form,
            "user": request.user,
            "address_id": address.id,
        }

        return render(request, "edit_address.html", context)

    # POST request updates the address with new data
    elif request.method == "POST":
        form = AddressForm(request.POST)
        address = Address.objects.get(id=id)

        address.door_no = form["door_no"].value()
        address.street = form["street"].value()
        address.area = form["area"].value()
        address.city = form["city"].value()
        address.state = form["state"].value()
        address.country = form["country"].value()
        address.pincode = form["pincode"].value()

        address.save()

        return redirect("address")


# Delete address, /api/core/address/delete/<int:id>/
@swagger_auto_schema(
    operation_description="Delete an address",
    method="get",
)
@login_required
@api_view(["GET"])
def delete_address(request, id):
    address = Address.objects.get(id=id)
    address.delete()
    return redirect("address")


# Logout, /api/core/logout/
@swagger_auto_schema(
    operation_description="Logs out an user",
    method="get",
)
@login_required
@api_view(["GET"])
def logout_user(request):
    logout(request)
    return redirect("home")


# 404 page, /api/core/404/
@swagger_auto_schema(
    operation_description="404 page",
    method="get",
)
@api_view(["GET"])
def no_page(request):
    if request.user.id != None:
        context = {
            "user": request.user,
        }
    else:
        context = {
            "user": False,
        }
    return render(request, "404.html", context, status=status.HTTP_404_NOT_FOUND)
