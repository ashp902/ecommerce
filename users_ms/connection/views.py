from django.shortcuts import render, redirect
from django.http import HttpResponse

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

import requests
import json

from .forms import ProductForm, OrderForm

from core.models import Address


# URL on which the product microservice runs on
PRODUCT_MS_URL = 'http://127.0.0.1:8002/api/product/'
CART_MS_URL = 'http://127.0.0.1:5000/'
ORDER_MS_URL = 'http://127.0.0.1:8003/api/order/'

# Function to help writing urls faster
def append_url(*args):
    return ''.join([*args])


# Convert response (from requests module) to response (from rest_framework)
def process_response(response):
    return Response(
        data=response.content,
        status=response.status_code,
        content_type=response.headers['Content-Type']
    )

# Viewset with all product microservice views
class ProductViewSet(ViewSet):
    
    # GET, /api/connection/product/create/
    def create_product_page(self, request): # Renders a HTML page with an empty form to create a new product
        if request.user:

            form = ProductForm()

            context = {

                'form': form,

            }

            return render(request, 'product_form.html', context)
        
        # If no user is logged in, display error
        return HttpResponse('No user found')


    # POST, /api/connection/product/create/
    def create_product(self, request): # Creates a new product

        # if user is logged in, perform validations
        if request.user:

            form = ProductForm(request.POST)

            # if form data is valid, make an api call to products service
            if form.is_valid():

                post_data = dict(request.POST.lists())

                data = {

                    'user_id': request.user.id,

                    **post_data

                }

                response = requests.post(url=append_url(PRODUCT_MS_URL, 'create/'), data=data)

                # return process_response(response)
                return redirect('http://127.0.0.1:8001/api/core/home/')
            
            else:

                return HttpResponse('Form not valid')
            
        # if no user is logged in, display error
        return HttpResponse('No user found')


    # GET, /api/connection/product/<int:id>/
    def product_page(self, request, id):

        # if user is logged in, make an api call to product service
        if request.user:

            response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), '/'))

            product = json.loads(json.loads(response.content))
            seller_id = product.pop('seller_id')

            can_edit = request.user.id == seller_id

            

            context = {

                'product': product,

                'can_edit': can_edit,

                'user_id': request.user.id,

            }

            return render(request, 'product_page.html', context)
        
        # if no user is logged in, display error
        else:

            return HttpResponse('User not found')


    # GET, /api/connection/product/change/<int:id>/
    def edit_product_page(self, request, id):

        # if user is logged in, make an api call to product service
        if request.user:

            response = requests.get(url=append_url(PRODUCT_MS_URL, str(id), '/'))

            product = json.loads(json.loads(response.content))
            seller_id = product.pop('seller_id')

            form = ProductForm(product)

            context = {

                'seller_id': seller_id,

                'form': form,

            }

            return render(request, 'edit_product_page.html', context)
        
        # if no user is logged in, display error
        else:
            return HttpResponse('User logged in')


    # POST, /api/connection/product/change/<int:id>/
    def edit_product(self, request, id):

        # if user is logged in, perform validation 
        if request.user:

            form = ProductForm(request.POST)

            # if form data is valid, make an api call to products service
            if form.is_valid():
                if form['delete'].value():
                    response = requests.delete(url=append_url(PRODUCT_MS_URL, 'change/', str(id), '/'))

                    response = requests.delete(url=append_url(CART_MS_URL, 'product/', str(id), '/'))
                    
                    return redirect('/api/core/home/')
                else:

                    data = dict(request.POST.lists())

                    response = requests.post(url=append_url(PRODUCT_MS_URL, 'change/', str(id), '/'), data=data)

                    if response.status_code == 200:

                        context = {

                            'form': form,

                        }
                        
                        # re-render the form with updated data
                        return render(request, 'edit_product_page.html', context)
                    
                    # if updating failed, display error
                    else:

                        return HttpResponse('Updating failed')
            
            # if form data is not valid, display error
            else:

                return HttpResponse('Form not valid')
        
        # if no user is logged in, display error
        return HttpResponse('No user found')  


    # GET, /api/connection/product/all/
    def get_all_products(self, request):

        # make an api call to products service
        response = requests.get(url=append_url(PRODUCT_MS_URL, 'all/'))

        data = json.loads(response.content)

        return Response(data=json.dumps(data))


    # GET, /api/myproducts/<int:id>/
    def get_all_products_with_user_id(self, request, id):

        # make an api call to products service
        response = requests.get(url=append_url(PRODUCT_MS_URL, 'seller/', str(id)))

        data = json.loads(response.content)

        return Response(data=json.dumps(data))
    

    def search_products(self, request):
        print(request.GET.get('query', ''))
        return HttpResponse('reached')


class CartViewSet(ViewSet):

    def get_cart(self, request):
        if request.user:
            response = requests.get(url=append_url(CART_MS_URL, str(request.user.id)))
            items = json.loads(response.content)
            cart_items = items['cart_items']
            history = items['history']
            context = {
                'cart_items': cart_items,
                'history': history,
            }
            return render(request, 'cart.html', context)
        
    def cart_item_page(self, request, id):
        if request.user:
            response = requests.get(url=append_url(CART_MS_URL, '/item/', str(id)))
            cart_item = json.loads(response.content)
            
            response = requests.get(url=append_url(PRODUCT_MS_URL, str(cart_item['product_id']), '/'))
            product = json.loads(json.loads(response.content))

            context = {
                'cart_item': cart_item,
                'product': product
            }
            return render(request, 'cart_item.html', context)

    def edit_cart_item(self, request, id):
        if request.user:
            # print(dir(request.POST))
            # print(request.POST.keys())
            if 'delete' in request.POST.keys():
                response = requests.delete(url=append_url(CART_MS_URL, '/item/', str(id), '/'))

                return redirect('/api/connection/cart/')
            else:
                quantity = request.POST['quantity']
                response = requests.post(url=append_url(CART_MS_URL, '/item/', str(id), '/'), data={'quantity': quantity})

                response = requests.get(url=append_url(CART_MS_URL, '/item/', str(id), '/'))
                cart_item = json.loads(response.content)
                
                response = requests.get(url=append_url(PRODUCT_MS_URL, str(cart_item['product_id']), '/'))
                product = json.loads(json.loads(response.content))      

                context = {
                    'cart_item': cart_item,
                    'product': product
                }

                return render(request, 'cart_item.html', context)
        

class OrderViewSet(ViewSet):

    def place_order(self, request):
        if request.user:
            response = requests.get(url=append_url(CART_MS_URL, str(request.user.id)))
            items = json.loads(response.content)
            cart_items = items['cart_items']

            products = [
                {**json.loads(json.loads(requests.get(url=append_url(PRODUCT_MS_URL, str(cart_item['product_id']), '/')).content)), **cart_item}
                        for cart_item in cart_items
                ]
            
            addresses = Address.objects.filter(user_id = request.user.id)

            total_amount = sum([((item['price'] - item['discount']) * item['quantity']) for item in products])

            # addresses = [(address.id, str(address)) for address in addresses]

            # form = OrderForm(addresses=addresses)
            # print(form)
            request.session['products'] = products
            request.session['total_amount'] = total_amount

            context = {
                'products': products,
                # 'form': form,
                'addresses': addresses,
                'total_amount': total_amount,
            }
            # response = requests.post(url=append_url(ORDER_MS_URL, 'place/'), data={'products': products})
            return render(request, 'place_order.html', context)
    
    def initiate_payment(self, request):
        if request.user:
            # print(request.session['products'])
            products = json.dumps(request.session['products'])
            # print(request.session['products'])
            # print(products)
            # print(request.POST['address'])
            order = {
                'user_id': request.user.id,
                'address_id': request.POST['address'],
                'delivery_status': 'Order recieved',
                'total_amount': request.session['total_amount'],
                'products': products,
            }

            response = requests.post(url=append_url(PRODUCT_MS_URL, 'place/'), data={'products': products})
            if response.status_code != 200:
                return HttpResponse('Order failed')

            response = requests.post(url=append_url(ORDER_MS_URL, 'place/'), data=order)

            return redirect('/api/connection/order/all/')
    
    def view_all_orders(self, request):
        if request.user:
            response = requests.get(url=append_url(ORDER_MS_URL, 'all/' + str(request.user.id) + '/'))

            orders = json.loads(response.content)

            context = {
                'orders': orders
            }

            return render(request, 'orders_page.html', context)
        
    def order_page(self, request, id):
        if request.user:
            response = requests.get(url=append_url(ORDER_MS_URL, str(id), '/'))

            order = json.loads(response.content)

            context = {
                'order': order,
            }

            return render(request, 'order_page.html', context)
    
    def cancel_order(self, request, id):
        if request.user:
            response = requests.post(url=append_url(ORDER_MS_URL, str(id), '/'))

            return redirect('/api/connection/order/all/')


class ReviewViewSet(ViewSet):

    pass