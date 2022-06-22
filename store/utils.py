import json
from django.core import exceptions
from dataclasses import dataclass
from .models import *


@dataclass
class CookieData:
    cart_items: int
    order: dict
    items: list


class Utils:
    @staticmethod
    def cookie_cart(request):
        try:
            cart = json.loads(request.COOKIES['cart'])
        except KeyError:
            cart = {}

        items = []
        order = {'get_cart_total': 0, 'get_cart_total_items': 0, 'shipping': False}
        cart_items = order['get_cart_total_items']
        for i in cart:
            try:
                cart_items += cart[i]["quantity"]
                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])
                order['get_cart_total'] += total
                order['get_cart_total_items'] = cart_items

                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image_url': product.image_url
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total
                }
                items.append(item)
                if not product.digital:
                    order['shipping'] = True
            except exceptions.ObjectDoesNotExist:
                pass
        return CookieData(cart_items=cart_items, order=order, items=items)

    def get_cart_data(self, request):
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cart_items = order.get_cart_total_items
        else:
            cookie_data = self.cookie_cart(request)
            cart_items = cookie_data.cart_items
            order = cookie_data.order
            items = cookie_data.items
        return CookieData(cart_items=cart_items, order=order, items=items)

    @staticmethod
    def create_guest_order(request, data):
        print('User is not logged in..')
        print('COOKIES', request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']
        cookie_data = Utils.cookie_cart(request)
        items = cookie_data.items
        customer, created = Customer.objects.get_or_create(email=email)
        customer.name = name
        customer.save()
        order = Order.objects.create(customer=customer, complete=False)
        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            order_item = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])
        return customer, order
