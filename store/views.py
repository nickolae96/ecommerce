import json
import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import RedirectView

from .models import *
from .utils import Utils
from .forms import CreateUserForm


class StoreView(View):
    store_template = 'store/store.html'

    def get(self, request):
        data = Utils().get_cart_data(request)
        cart_items = data.cart_items
        products = Product.objects.all()
        context = {'products': products, 'cart_items': cart_items}
        return render(request, self.store_template, context)


class CartView(View):
    cart_template = 'store/cart.html'

    def get(self, request):
        data = Utils().get_cart_data(request)
        cart_items = data.cart_items
        order = data.order
        items = data.items
        context = {'items': items, 'order': order, 'cart_items': cart_items}
        return render(request, self.cart_template, context)


class CheckoutView(View):
    checkout_template = 'store/checkout.html'

    def get(self, request):
        data = Utils().get_cart_data(request)
        cart_items = data.cart_items
        order = data.order
        items = data.items
        context = {'items': items, 'order': order, 'cart_items': cart_items}
        return render(request, self.checkout_template, context)


class UpdateItemView(View):

    def post(self, request):
        data = json.loads(request.body)
        product_id = data['productId']
        action = data['action']
        customer = request.user.customer
        product = Product.objects.get(id=product_id)
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        order_item, _ = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            order_item.quantity = order_item.quantity + 1
        elif action == 'remove':
            order_item.quantity = order_item.quantity - 1
        order_item.save()

        if order_item.quantity <= 0:
            order_item.delete()

        return JsonResponse('Item was added', safe=False)


class ProcessOrderView(View):

    def post(self, request):
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)
        if request.user.is_authenticated:
            customer = request.user.customer
            order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = Utils().create_guest_order(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        if float(total) == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode']
            )
        return JsonResponse('Payment completed..', safe=False)


class LoginView(View):
    login_template = 'store/login.html'

    def get(self, request):
        context = {}
        return render(request, self.login_template, context)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username or password is incorrect')
        context = {}
        return render(request, self.login_template, context)


class LogOutView(RedirectView):
    pattern_name = 'store'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class RegisterView(View):
    register_template = 'store/register.html'
    form = CreateUserForm()
    context = {'form': form}

    def get(self, request):
        return render(request, self.register_template, self.context)

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            form.save()
            customer, created = Customer.objects.get_or_create(email=email)
            customer.name = name
            customer.user = User.objects.get(email=email)
            customer.save()
            messages.success(request, f"Account was created for {form.cleaned_data.get('username')}")
            return redirect('login')
        return render(request, self.register_template, self.context)


