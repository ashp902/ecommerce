from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

import requests
import json

from .models import User, Address
from .serializers import UserSerializer
from .forms import RegisterUserForm, LoginUserForm, EditUserForm, AddressForm

# Landing page view
def landing_page(request):
    all_products = requests.get(url="http://127.0.0.1:8001/api/connection/product/all/")
    all_products = json.loads(json.loads(all_products.content))
    print(request.user.id)
    context = {
        'all_products': all_products,
        'user': request.user.id != None,
    }
    return render(request, 'landing_page.html', context)

# Views for login and register pages
class LoginRegisterViewSet(viewsets.ViewSet):

    # GET, /api/all/
    def all_users(self, request): # Displays data of all users

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)


    # POST, /api/register/buyer/
    def create_buyer(self, request): # Registers a new buyer

        form = RegisterUserForm(request.POST)

        # if all fields are valid save and login buyer
        if form.is_valid():

            form.save_buyer()

            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(email=email, password=raw_password)

            # if authentication is successful, redirect to home page
            if user is not None :
                
                login(request, user)
                return redirect('home')
            
            # if authentication fails, redirect to login page
            else :
                
                return redirect('login')
            
        # if any field is not valid, redirect to register page
        else :
            
            return redirect('register_buyer')


    # POST, /api/register/seller/
    def create_seller(self, request): # Registers a new seller

        form = RegisterUserForm(request.POST)

        # if all fields are valid save and login seller
        if form.is_valid():

            form.save_seller()

            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(email=email, password=raw_password)

            # if authentication is successful, redirect to home page
            if user is not None :
                
                login(request, user)
                return redirect('home')
            
            # if authentication fails, redirect to login page
            else :
                
                return redirect('login')
            
        # if any field is not valid, redirect to register page
        else :
            
            return redirect('register_seller')


    # GET, /api/register/buyer/ , /api/register/seller/
    def registration_page(self, request):

        if request.user.id != None:
            return redirect('home')

        form = RegisterUserForm()

        context = {

            'form': form,

            'user': request.user.id != None,

        }

        return render(request, 'register.html', context)


    # POST, /api/login/
    def login_user(self, request):

        form = LoginUserForm(request.POST)

        email = form['email'].value()
        raw_password = form['password'].value()

        user = authenticate(email=email, password=raw_password)

        # if authentication is successful, redirect to home page
        if user is not None:
            
            login(request, user)
            return redirect('home')
        
        # if authentication fails, display error
        else:
            
            return HttpResponse('not valid')

   
    # GET, /api/login/
    def login_page(self, request):

        if request.user.id != None:
            return redirect('home')

        form = LoginUserForm()

        context = {

            'form': form,

            'user': request.user.id != None,

        }

        return render(request, 'login.html', context)
    
# Home page view, /api/home/
def home(request) :
    if request.user.id != None:
        user = User.objects.get(id=request.user.id)
        if user.user_role_id == 1:
            all_products = requests.get(url="http://127.0.0.1:8001/api/connection/product/all/")
            all_products = json.loads(json.loads(all_products.content))
            context = {
                'all_products': all_products,
                'user': user,
            }
            return render(request, 'landing_page.html', context)
        elif user.user_role_id == 2:
            products = requests.get(url="http://127.0.0.1:8001/api/connection/product/myproducts/" + str(request.user.id))
            products = json.loads(json.loads(products.content))
            context = {
                'products': products,
                'user': user,
            }
            return render(request, 'landing_page.html', context)
        elif user.user_role_id == 3:
            return redirect('/admin')
    else:
        all_products = requests.get(url="http://127.0.0.1:8001/api/connection/product/all/")
        all_products = json.loads(json.loads(all_products.content))

        context = {
            'all_products': all_products,
            'user': request.user.id != None,
        }
        return render(request, 'landing_page.html', context)

# Profile page, /api/profile/
@login_required
def profile(request):

    # GET request displays the profile page with user details
    if request.method == 'GET':

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        # Populate form with user details
        data = {
            'email': user.email,
            'username': user.username,
            'password1': '',
            'password2': '',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_of_birth': user.date_of_birth,
            'gender': user.gender
        }
        form = EditUserForm(data)

        context = {

            'form': form,

            'user': user,

        }

        return render(request, 'profile.html', context)
    
    # POST request updates the user details and displays the profile page
    elif request.method == 'POST':

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        form = EditUserForm(request.POST)

        # Update the user instance with new details
        user.first_name = form['first_name'].value()
        user.last_name = form['last_name'].value()
        user.date_of_birth = form['date_of_birth'].value()
        user.gender = form['gender'].value()

        if form['password1'].value() and form['password2'].value() and form['password1'].value() == form['password2'].value():

            user.set_password(form['password1'].value())
        
        user.save()

        context = {

            'form': form,
            'user': user,

        }

        return render(request, 'profile.html', context)


# Address page, only available for buyers, /api/address/
@login_required
def address(request):

    user_id = request.user.id
    user = User.objects.get(id=user_id)

    # If user is not a buyer, display error
    if user.user_role_id != 1:

        return HttpResponse('not found')
    
    # GET request displays all addresses of the current user
    if request.method == 'GET':
        
        addresses = Address.objects.filter(user_id = user_id)

        context = {

            'addresses': addresses,

            'user': user,

        }

        return render(request, 'address.html', context)


# Create new address page, /api/address/create/
@login_required
def create_address(request):

    user_id = request.user.id
    user = User.objects.get(id=user_id)

    # If user is not a buyer, display error
    if user.user_role_id != 1:

        return HttpResponse('not found')
    
    # GET request displays form to create a new address
    if request.method == 'GET':
        
        form = AddressForm()
        context = {

            'form': form,

            'user': user,

        }

        return render(request, 'address_form.html', context)
    
    # POST request creates a new address
    elif request.method == 'POST':

        form = AddressForm(request.POST)

        # If all fields are valid, save the address to the current user
        if form.is_valid():

            form.save_with_user_id(request.user.id)

            # Redirect to address page
            return redirect('address')

        # If any field is not valid, redirect to create address page        
        else:

            return redirect('address_form')


# Edit address page, /api/address/edit/<int:id>
@login_required
def edit_address(request, id):

    # GET request displays a form to edit the selected address
    if request.method == 'GET':

        address = Address.objects.get(id=id)

        # Populate the form with current address data
        data = {
            'door_no': address.door_no,
            'street': address.street,
            'area': address.area,
            'city': address.city,
            'state': address.state,
            'country': address.country,
            'pincode': address.pincode
        }
        form = AddressForm(data)

        context = {

            'form': form

        }

        return render(request, 'edit_address.html', context)
    
    # POST request updates the address with new data
    elif request.method == 'POST':

        form = AddressForm(request.POST)
        address = Address.objects.get(id=id)

        address.door_no = form['door_no'].value()
        address.street = form['street'].value()
        address.area = form['area'].value()
        address.city = form['city'].value()
        address.state = form['state'].value()
        address.country = form['country'].value()
        address.pincode = form['pincode'].value()

        address.save()

        context = {

            'form': form

        }

        return render(request, 'edit_address.html', context)

  
@login_required
def logout_user(request):
    logout(request)
    return redirect('login')
