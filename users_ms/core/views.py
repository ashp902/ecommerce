from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
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
from .forms import RegisterUserForm, LoginUserForm, EditUserForm, AddressForm


def get_user(request):
    if request.user.id == None:
        return False
    return request.user


def get_categories(products):
    tag_counts = {}
    for product in products:
        for tag in product["product_tags"][0].split(","):
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1
    tag_counts = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:4])
    return tag_counts


@swagger_auto_schema(
    operation_description="Create a user with buyer role",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password1": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "password2": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            "date_of_birth": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            "gender": openapi.Schema(type=openapi.TYPE_STRING, enum=["M", "F", "O"]),
        },
    ),
)
@api_view(["POST"])
def create_buyer(request):
    form = RegisterUserForm(request.POST)

    if form.is_valid():
        form.save_buyer()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=raw_password)

        if user is not None:
            auth_login(request, user)
            request.session["errors"] = ["User logged in"]
            return redirect("home")

        else:
            return redirect("login")

    else:
        errors = form.errors
        error_messages = []
        for error in errors.values():
            error_messages += error

        request.session["errors"] = error_messages

        return redirect("register")


@swagger_auto_schema(
    operation_description="Create a user with seller role",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password1": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "password2": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            "date_of_birth": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            "gender": openapi.Schema(type=openapi.TYPE_STRING, enum=["M", "F", "O"]),
        },
    ),
)
@api_view(["POST"])
def create_seller(request):
    form = RegisterUserForm(request.POST)

    if form.is_valid():
        form.save_seller()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=raw_password)

        if user is not None:
            auth_login(request, user)
            request.session["errors"] = ["User logged in"]
            return redirect("home")

        else:
            return redirect("login")

    else:
        errors = form.errors
        error_messages = []
        for error in errors.values():
            error_messages += error

        request.session["errors"] = error_messages

        return redirect("register")


@swagger_auto_schema(
    operation_description="Renders user registration page",
    method="get",
)
@api_view(["GET"])
def registration_page(request):
    if request.user.id != None:
        return redirect("home")

    errors = request.session.pop("errors", None)

    form = RegisterUserForm()

    context = {
        "form": form,
        "user": get_user(request),
        "errors": errors,
    }

    return render(request, "register.html", context)


@swagger_auto_schema(
    operation_description="Renders login page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Logs in user",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
        },
    ),
)
@api_view(["GET", "POST"])
def login(request):
    if request.method == "GET":
        if request.user.id != None:
            return redirect("home")

        errors = request.session.pop("errors", None)

        form = LoginUserForm()

        context = {
            "form": form,
            "user": get_user(request),
            "errors": errors,
        }

        return render(request, "login.html", context)
    elif request.method == "POST":
        form = LoginUserForm(request.POST)
        # print(request.POST)

        email = request.POST["email"]
        raw_password = request.POST["password"]
        # print(email, raw_password)

        user = authenticate(email=email, password=raw_password)

        if user is not None:
            auth_login(request, user)
            request.session["errors"] = ["User logged in"]
            return redirect("home")

        else:
            request.session["errors"] = ["Invalid Email ID or Password"]
            return redirect("login")


@swagger_auto_schema(
    operation_description="Renders home page",
    method="get",
)
@api_view(["GET"])
def home(request):
    errors = request.session.pop("errors", None)

    if request.user.id != None:
        user = User.objects.get(id=request.user.id)
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

            categories = get_categories(products)

            paginator = Paginator(products, 9)
            page = request.GET.get("page")
            products = paginator.get_page(page)

            context = {
                "products": products,
                "user": get_user(request),
                "errors": errors,
                "categories": categories,
            }
            return render(request, "landing_page.html", context)

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
                "user": get_user(request),
                "errors": errors,
            }
            return render(request, "landing_page.html", context)
        elif user.user_role_id == 3:
            return redirect("/admin")
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
            "user": get_user(request),
            "errors": errors,
        }
        return render(request, "landing_page.html", context)


@swagger_auto_schema(
    operation_description="Renders profile page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Updates user details",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password1": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "password2": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
            ),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            "date_of_birth": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            "gender": openapi.Schema(type=openapi.TYPE_STRING, enum=["M", "F", "O"]),
            "img": openapi.Schema(type=openapi.TYPE_FILE),
        },
    ),
)
@login_required
@api_view(["GET", "POST"])
def profile(request):
    if request.method == "GET":
        user_id = request.user.id
        user = User.objects.get(id=user_id)

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

        errors = request.session.pop("errors", None)

        context = {
            "form": form,
            "user": get_user(request),
            "errors": errors,
        }

        return render(request, "profile.html", context)

    elif request.method == "POST":
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        form = EditUserForm(request.POST)

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
            return redirect("/api/core/login/")

        user.save()

        context = {
            "form": form,
            "user": get_user(request),
        }
        img = False
        try:
            img = request.FILES["image"]
        except:
            print("Fetch failed")
            pass
        if img:
            img_extension = os.path.splitext(img.name)[1]

            path = "media/images/users/"

            if not os.path.exists(path):
                os.mkdir(path)

            img_save_path = path + str(user.id) + img_extension

            with open(img_save_path, "wb+") as f:
                for chunk in img.chunks():
                    f.write(chunk)

        request.session["errors"] = ["User details updated successfully"]
        return redirect("profile")


@swagger_auto_schema(
    operation_description="Renders addresses page",
    method="get",
)
@login_required
@api_view(["GET"])
def address(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    if user.user_role_id != 1:
        return redirect("404")

    addresses = Address.objects.filter(user_id=user_id)
    errors = request.session.pop("errors", None)

    context = {
        "addresses": addresses,
        "user": get_user(request),
        "errors": errors,
    }

    return render(request, "address.html", context)


@swagger_auto_schema(
    operation_description="Renders create address form",
    method="get",
)
@swagger_auto_schema(
    operation_description="Creates a new address",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "address_name": openapi.Schema(type=openapi.TYPE_STRING),
            "door_no": openapi.Schema(type=openapi.TYPE_STRING),
            "street": openapi.Schema(type=openapi.TYPE_STRING),
            "area": openapi.Schema(type=openapi.TYPE_STRING),
            "city": openapi.Schema(type=openapi.TYPE_STRING),
            "state": openapi.Schema(type=openapi.TYPE_STRING),
            "country": openapi.Schema(type=openapi.TYPE_STRING),
            "pincode": openapi.Schema(type=openapi.TYPE_NUMBER),
        },
    ),
)
@login_required
@api_view(["GET", "POST"])
def create_address(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    if user.user_role_id != 1:
        return redirect("404")

    if request.method == "GET":
        errors = request.session.pop("errors", None)
        form = AddressForm()
        context = {
            "form": form,
            "user": get_user(request),
            "errors": errors,
        }

        return render(request, "address_form.html", context)

    elif request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            form.save_with_user_id(request.user.id)

            request.session["errors"] = ["Address created successfully"]

            return redirect("address")

        else:
            errors = form.errors
            error_messages = []
            for error in errors.values():
                error_messages += error

            request.session["errors"] = error_messages
            return redirect("address_form")


@swagger_auto_schema(
    operation_description="Renders edit address page",
    method="get",
)
@swagger_auto_schema(
    operation_description="Updates the address details",
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "address_name": openapi.Schema(type=openapi.TYPE_STRING),
            "door_no": openapi.Schema(type=openapi.TYPE_STRING),
            "street": openapi.Schema(type=openapi.TYPE_STRING),
            "area": openapi.Schema(type=openapi.TYPE_STRING),
            "city": openapi.Schema(type=openapi.TYPE_STRING),
            "state": openapi.Schema(type=openapi.TYPE_STRING),
            "country": openapi.Schema(type=openapi.TYPE_STRING),
            "pincode": openapi.Schema(type=openapi.TYPE_NUMBER),
        },
    ),
)
@login_required
@api_view(["GET", "POST"])
def edit_address(request, id):
    if request.method == "GET":
        address = Address.objects.get(id=id)

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

        errors = request.session.pop("errors", None)

        context = {
            "form": form,
            "user": get_user(request),
            "address_id": address.id,
            "errors": errors,
        }

        return render(request, "edit_address.html", context)

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
        request.session["errors"] = ["Address edited successfully"]

        return redirect("address")


@swagger_auto_schema(
    operation_description="Delete an address",
    method="get",
)
@login_required
@api_view(["GET"])
def delete_address(request, id):
    address = Address.objects.get(id=id)
    address.delete()

    request.session["errors"] = ["Address deleted successfully"]

    return redirect("address")


@swagger_auto_schema(
    operation_description="Logs out an user",
    method="get",
)
@login_required
@api_view(["GET"])
def logout_user(request):
    logout(request)

    request.session["errors"] = ["Logged out successfully"]
    return redirect("home")


@swagger_auto_schema(
    operation_description="404 page",
    method="get",
)
@api_view(["GET"])
def no_page(request):
    errors = request.session["errors"] if "errors" in request.session else []
    request.session.pop("errors", None)

    context = {
        "user": get_user(request),
        "errors": errors,
    }
    return render(request, "404.html", context, status=status.HTTP_404_NOT_FOUND)
