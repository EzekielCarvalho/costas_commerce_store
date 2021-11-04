from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm

import random
import string
import stripe
from django.views.decorators.csrf import csrf_exempt

from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Category

stripe.api_key = settings.SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET


def create_reference_code():                                                                  # This is a function to create random reference numbers for orders
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):                                                                  # This is a function to show all the items present in the Item class in models.py. These items are visible in Django admin.
    context = {                                                                         # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
        'items': Item.objects.all()                                                     # 'items' is used part of the loop in the home page.html. This is the Items class in models.py, objects.all asks for access to all the items in this class.
    }
    return render(request, "products.html", context)                                    # This is all part of the format. The render() function takes the request object as its first argument, a template name as its second argument and a dictionary as its optional third argument. It returns an HttpResponse object of the given template rendered with the given context. ref https://docs.djangoproject.com/en/3.2/intro/tutorial03/


def validator(values):                  # This function has been made to validate entries made for the shipping address, because the required in forms.py have been set to False, so people can enter empty strings. To avoid this, and add validation, this function has been made
    valid = True                        # Set valid originally to True
    for field in values:                # For each field in the values that are submitted
        if field == '':                 # if each field is an empty string
            valid = False               # Then valid will be set to False, so it would be an "invalid" entry
    return valid                        # Return the valid field


def searchbar(request):                         # This is a function for our search bar, it takes in a request
    if request.method == 'GET':                 # If the method of the request is a "GET". This is shown on the form HTML
        search = request.GET.get('search')      # Then we get the 'search' name details and save it in this variable
        post = Item.objects.all().filter(       # Then we filter all objects from the Item method and save to the post variable
            Q(description__icontains=search)    # we filter as per description matching the search variable results, regardless if it contains capital or small letters  
            | Q(title__icontains=search)        # we filter as per title matching the search variable results, regardless if it contains capital or small letters  
            | Q(category__icontains=search)     # we filter as per category matching the search variable results, regardless if it contains capital or small letters  
        ).distinct()                            # distinct() Returns a new QuerySet that uses SELECT DISTINCT in its SQL query. This eliminates duplicate rows from the query results. By default, a QuerySet will not eliminate duplicate rows. ref https://docs.djangoproject.com/en/3.2/ref/models/querysets/#:~:text=distinct()&text=Returns%20a%20new%20QuerySet%20that,will%20not%20eliminate%20duplicate%20rows.
        context = {
            'post': post}                                       # here we try to connect the previous code to fetch the order that has been completed so that we can fetch the reference code and other order details to post to the success.html page after payment       
        return render(request, "searchbar.html", context)
    
    else:
        messages.warning(
            request, "Nothing to look here")
        return redirect("core:home-page.html")

def process_payment(request):
    order = Order.objects.get(user=request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
    if order.billing_address:                                                       # Only if there is a billing address entered in the Order class then proceed with the following:
        context = {                                                                 # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
            'order': order,                                                         # order is equal to the order definied above
            'SHOW_COUPON_FORM': False,                                              # connected to order_snippet.html
        }
    else:
        messages.warning(
            request, "You're missing a billing address buddy :(")
        return redirect("core:checkout-page")
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': int(order.get_total()),
        'item_name': 'Final Total of product/s',
        'currency_code': 'EUR',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('core:success_paypal')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('core:cancelled_paypal')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'process_payment.html', {'order': order, 'form': form})


@csrf_exempt
def success_paypal(request):
    order = Order.objects.get(user=request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable      

    order_items = order.items.all()                                             # here we ask for all items from the Item class from the Order class to be shown. This is saved to a variable
    order.reference_code = create_reference_code()                                    # The reference code in the order class is going to be set equal to the function above created to make random reference codes
    order_items.update(ordered=True)                                            # Then we update all these items and set ordered to being "True" meaning that the items have been ordered.
    for item in order_items:                                                    # we start looping over each item in the variable, so this sets all of the ordered to true, and then we save all of them                                         
        item.save()

    order.ordered = True                                                        # order has been set to true so the order is completed
    order.save()

    order_success = Order.objects.filter(user=request.user, ordered=True, reference_code=order.reference_code)                # This is to get and set the variable to pull back the Order that has now been completed as per reference code and save it to the variable    

    context = {
        'payment_status': 'success',                                           # Set the payment status to success
        'order_success': order_success                                         # here we try to connect the previous code to fetch the order that has been completed so that we can fetch the reference code and other order details to post to the success.html page after payment
    }                    
    
    return render(request, 'success_paypal.html', context)


@csrf_exempt
def cancelled_paypal(request):
    return render(request, 'cancelled_paypal.html')



class CheckoutView(View):                                                               # This class is created for the checkout page. Class-based views provide an alternative way to implement views as Python objects instead of functions. ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#handling-forms-with-class-based-views
    def get(self, *args, **kwargs):                                                     # part of format of class based views, this will handle the "GET" requests from the user
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)            # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
            form = CheckoutForm()                                                       # This is from forms.py line 16 
            context = {                                                                 # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
                'form': form,                                                           # form is set equal to the form variable above
                'couponform': CouponForm(),                                             # This is from forms.py line 39 
                'order': order,                                                         # order is equal to the order definied above
                'SHOW_COUPON_FORM': True                                                # connected to order_snippet.html
            }

            shipping_address_qs = Address.objects.filter(user=self.request.user, address_type='S', default=True)  # Filter from the Address class as per the attributes set here. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
# default is set to true so that we can get the default address
            if shipping_address_qs.exists():                                            # If this address query set exists then we will grab this address from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                context.update({'default_shipping_address': shipping_address_qs[0]})    # Here, update the default shipping address to the one in the queryset, but the very first one. This refers to the first available order in the Address class
            # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
            # The constructor of django.template.Context takes an optional argument — a dictionary mapping variable names to variable values.
            # In addition to push() and pop(), the Context object also defines an update() method. This works like push() but takes a dictionary as an argument and pushes that dictionary onto the stack instead of an empty one. ref https://docs.djangoproject.com/en/3.2/ref/templates/api/#django.template.Context.update
            
            billing_address_qs = Address.objects.filter(user=self.request.user, address_type='B', default=True)  # Filter from the Address class as per the attributes set here. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
# default is set to true so that we can get the default address
            if billing_address_qs.exists():                                            # If this address query set exists then we will grab this address from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                context.update({'default_billing_address': billing_address_qs[0]})    # Here, update the default shipping address to the one in the queryset, but the very first one. This refers to the first available order in the Address class
            # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
            # The constructor of django.template.Context takes an optional argument — a dictionary mapping variable names to variable values.
            # In addition to push() and pop(), the Context object also defines an update() method. This works like push() but takes a dictionary as an argument and pushes that dictionary onto the stack instead of an empty one. ref https://docs.djangoproject.com/en/3.2/ref/templates/api/#django.template.Context.update
            
            return render(self.request, "checkout-page.html", context)                  # This is all part of the format. The render() function takes the request object as its first argument, a template name as its second argument and a dictionary as its optional third argument. It returns an HttpResponse object of the given template rendered with the given context. ref https://docs.djangoproject.com/en/3.2/intro/tutorial03/
        except ObjectDoesNotExist:                                                      # The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/#objectdoesnotexist
            messages.info(self.request, "You do not have an active order")              # regarding self.request, If you're using class-based views, then your views are member functions, so by convention their first argument will be self, e.g. def view_name(self, request, ...). In this case, refer to the Django documentation regarding which arguments are provided to which functions depending on which view you're subclassing. ref https://stackoverflow.com/questions/35578885/request-v-self-request-in-django
            return redirect("core:checkout-page")                                       # return to checkout-page html

    def post(self, *args, **kwargs):                                                    # This will handle the POST requests made by the user, such as in a form for example. This is all part of the format. 
        form = CheckoutForm(self.request.POST or None)                                  # CheckoutForm from forms.py line 16. The use of or in this case does not evaluate to True or False, but returns one of the objects. Keep in mind that or is evaluated from left to right. When the QueryDict request.POST is empty, it takes a Falsy value, so the item on RHS of the or operation is selected (which is None), and the form is initialized without vanilla arguments (i.e. with None): ref https://stackoverflow.com/questions/38251922/logic-behind-formrequest-post-or-none
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)            # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable. The user is going to be set as the user who is making the request. THis is the "Self.request.user"   
            if form.is_valid():                                                         # The primary task of a Form object is to validate data. With a bound Form instance, call the is_valid() method to run validation and return a boolean designating whether the data was valid. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#using-forms-to-validate-data
                
                use_default_shipping = form.cleaned_data.get('use_default_shipping')    # This will fetch or get the data submitted from the checkout form, particularly the "use_default_shipping" feature from the forms.py. If it is true or false since it's a Boolean field. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                if use_default_shipping:                                                # If use_default_shipping is true (if statements are always true, and if it is else, then it is false)
                    print("We're going to use your default address for shipping")
                    address_qs = Address.objects.filter(user=self.request.user, address_type='S', default=True)  # Filter from the Address class as per the attributes set here. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                    # default is set to true so that we can get the default address
                    if address_qs.exists():                                             # If a shipping address does exist in the django database (and is saved in the address_qs variable). If this address query set exists then we will grab this address from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                        shipping_address = address_qs[0]                                # Here, since the shipping address does exist, then set a variable to the one in the queryset, but the very first one. This refers to the first available order in the database. Whenever you're filtering and searching within a query set, remember youre searching from within the django database
                    # We have to save the shipping_address to the order (connected to Order class) too
                        order.shipping_address = shipping_address                                   # The shipping address in the Order class in models.py is going to be set equal to the billing address we just prepared above which was fed in by the user via the form
                        order.save()  
                    else:
                        messages.warning(self.request, "Sorry buddy, no such shipping address found in our server:( ")                  # Else give a warning message
                        return redirect('core:checkout-page')                               # And redirect
                else:
                    print("Looks like you're entering a new shipping address")

                    # Hence to follow the else statement, the new shipping address will be taken based on what the user enters in the checkout form.
                    shipping_address1 = form.cleaned_data.get('shipping_address')           # The shipping address feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    shipping_address2 = form.cleaned_data.get('shipping_address2')          # The shipping address2 feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    shipping_country = form.cleaned_data.get('shipping_country')            # The shipping country feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    shipping_zip = form.cleaned_data.get('shipping_zip')                    # The shipping zip feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    
                    # The previous few lines were just getting the data entered in the form to get the data for the shipping address.
                    # The next few lines are going to set the obtained data to make the new shipping address
                    # The lines after these save the set data into the shipping_address variable
                    
                    if validator([shipping_address1, shipping_country, shipping_zip]):      # If these values are valid, then proceed with the shipping address below. Ref line 31 for note on validator function                

                        shipping_address = Address(                                             # This Address is from models.py
                            user=self.request.user,                                             # This is calling the Address class from models.py and setting each attribute. The user is going to be set as the user who is making the request. THis is the "Self.request.user"   
                            street_address=shipping_address1,                                # This is calling the Address class from models.py and setting each attribute. The street address is going to be set as the street address fed into the form.
                            apartment_address=shipping_address2,                                # This is calling the Address class from models.py and setting each attribute. The apartment address is going to be set as the apartment address fed into the form by the user.
                            country=shipping_country,                                  # This is calling the Address class from models.py and setting each attribute. The country is going to be set as the country fed into the form.
                            zip=shipping_zip,                                                            # This is calling the Address class from models.py and setting each attribute. The zip is going to be set as the zip fed into the form.
                            address_type='S'                                                    # when we create a Shipping address, we just have to mention that the address type is S for Shipping Address
                        )
                        shipping_address.save()                                                 # Shipping address is saved
                    
                      # We decide to save the shipping address outside the else statement so that either way a shipping address will get saved either from the default one above, or from the new one entered by the user
                        order.shipping_address = shipping_address                                   # The shipping address in the Order class in models.py is going to be set equal to the billing address we just prepared above which was fed in by the user via the form
                        order.save()                                                            # save the order (variable)

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')    # This will fetch or get the data submitted from the checkout form, particularly the "set_default_shipping" feature from the forms.py. If it is true or false since it's a Boolean field. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                        if set_default_shipping:                                                # If set_default_shipping is true (if statements are always true, and if it is else, then it is false)
                            shipping_address.default = True                                     # This is going to save as a default shipping address. This shipping_address is from the Order class, from "order" in the previous line. The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#default
                            shipping_address.save()
                    
                    else:
                        messages.warning(self.request, "Sorry, we need you to fill in the missing shipping address fields :(")                  # Else give a warning message
      
                use_default_billing = form.cleaned_data.get('use_default_billing')    # This will fetch or get the data submitted from the checkout form, particularly the "use_default_billing" feature from the forms.py. If it is true or false since it's a Boolean field. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                same_billing_address = form.cleaned_data.get('same_billing_address')    # This will fetch or get the data submitted from the checkout form, particularly the "same_billing_address" feature from the forms.py. If it is true or false since it's a Boolean field. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                
                if same_billing_address:                                                # billing_address is from forms.py what has been entered. If same_billing_address is true (if statements are always true, and if it is else, then it is false)
                    billing_address = shipping_address                                  # then billing_address will be set equal to the shipping address
                    billing_address.pk = None                                           # This is to clone the billing_address since we want to copy it for the shipping address. You have to always set the primary key (pk) to none for cloning a model instantance. Although there is no built-in method for copying model instances, it is possible to easily create new instance with all fields’ values copied. In the simplest case, you can set pk to None and _state.adding to True. ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#copying-model-instances
                    billing_address.save()                                              # This will create a new address
                    billing_address.address_type = 'B'                                  # Here we will set the address type of the Billing address to B for billing address
                    billing_address.save()                                              # This will save the billing address onto the order
                    order.billing_address = billing_address                             # The billing address in the Order class in models.py is going to be set equal to the billing address we just prepared above which was fed in by the user via the form
                    order.save()                                                    # save the order (variable)

                elif use_default_billing:                                                # else If use_default_billing is true (if statements are always true, and if it is else, then it is false)
                    print("We're going to use your default address for billing")
                    address_qs = Address.objects.filter(user=self.request.user, address_type='B', default=True)  # Filter from the Address class as per the attributes set here. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                    # default is set to true so that we can get the default address
                    if address_qs.exists():                                             # If a billing address does exist in the django database (and is saved in the address_qs variable). If this address query set exists then we will grab this address from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
                        billing_address = address_qs[0]                                # Here, since the shipping address does exist, then set a variable to the one in the queryset, but the very first one. This refers to the first available order in the database. Whenever you're filtering and searching within a query set, remember youre searching from within the django database
                     # We have to save billing address to the order (lined to the Order class) too
                        order.billing_address = billing_address                                 # The billing address in the Order class in models.py is going to be set equal to the billing address we just prepared above which was fed in by the user via the form
                        order.save()                                                            # save the order (variable)
                    else:
                        messages.warning(self.request, "Sorry buddy, no such billing address found in our server:( ")                  # Else give a warning message
                        return redirect('core:checkout-page')                               # And redirect
                else:
                    print("Looks like you're entering a new billing address")
                    # Hence to follow the else statement, the new billing address will be taken based on what the user enters in the checkout form.
                    billing_address1 = form.cleaned_data.get('billing_address')           # The billing address feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    billing_address2 = form.cleaned_data.get('billing_address2')          # The billing address2 feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    billing_country = form.cleaned_data.get('billing_country')            # The billing country feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    billing_zip = form.cleaned_data.get('billing_zip')                    # The billing zip feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                    
                    # The previous few lines were just getting the data entered in the form to get the data for the billing address.
                    # The next few lines are going to set the obtained data to make the new billing address
                    # The lines after these save the set data into the billing_address variable
                    
                    if validator([billing_address1, billing_country, billing_zip]):      # If these values are valid, then proceed with the billing address below. Ref line 31 for note on validator function                
                        billing_address = Address(                                             # This Address is from models.py
                            user=self.request.user,                                             # This is calling the Address class from models.py and setting each attribute. The user is going to be set as the user who is making the request. THis is the "Self.request.user"   
                            street_address=billing_address1,                                # This is calling the Address class from models.py and setting each attribute. The street address is going to be set as the street address fed into the form.
                            apartment_address=billing_address2,                                # This is calling the Address class from models.py and setting each attribute. The apartment address is going to be set as the apartment address fed into the form by the user.
                            country=billing_country,                                  # This is calling the Address class from models.py and setting each attribute. The country is going to be set as the country fed into the form.
                            zip=billing_zip,                                          # This is calling the Address class from models.py and setting each attribute. The zip is going to be set as the zip fed into the form.
                            address_type='B'                                                  # when we create a Billing address, we just have to mention that the address type is B for Billing Address
                        )
                        billing_address.save()                                                 # billing_address is saved
                    
                      # We decide to save the billing address outside the else statement so that either way a billing address will get saved either from the default one above, or from the new one entered by the user
                        order.billing_address = billing_address                                 # The billing address in the Order class in models.py is going to be set equal to the billing address we just prepared above which was fed in by the user via the form
                        order.save()                                                            # save the order (variable)

                        set_default_billing = form.cleaned_data.get('set_default_billing')    # This will fetch or get the data submitted from the checkout form, particularly the "set_default_billing" feature from the forms.py. If it is true or false since it's a Boolean field. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                        if set_default_billing:                                                # If set_default_billing is true (if statements are always true, and if it is else, then it is false)
                            billing_address.default = True                                     # This is going to save as a default billing address. This billing_address is from the Order class, from "order" in the previous line. The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#default
                            billing_address.save()
                    
                    else:
                        messages.warning(self.request, "Sorry, we need you to fill in the missing billing address fields :(")                  # Else give a warning message
      
                payment_option = form.cleaned_data.get('payment_option')                # The payment option feature is from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data

                if payment_option == 'S':                                               # from forms.py lne 11. If the payment option is equal to "S" for "stripe" as per forms.py
                    return redirect('core:payment', payment_option='Stripe')            # Then redirect to the payment page for stripe
                elif payment_option == 'P':                                             # from forms.py lne 12. If the payment option is equal to "P" for "paypal" as per forms.py
                    messages.warning(                                                   
                        self.request, "Thanks for choosing Paypal, you'll be redirected to Paypal's website to complete your payment :)")                  # Else give a warning message
                    return redirect('core:process_payment')
                             # Then redirect to the payment page for paypal
                else:
                    messages.warning(                                                   
                        self.request, "invalid payment option chosen")                  # Else give a warning message
                    return redirect('core:checkout-page')                               # And redirect
            else:
                return HttpResponse(form.errors)
        
        except ObjectDoesNotExist:                                                      # If an error is caught after trying the above then the objectdoesnotexist error is given. The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):                                                                # This is the payment class responsible for the payment page form.  Class-based views provide an alternative way to implement views as Python objects instead of functions. ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#handling-forms-with-class-based-views
    def get(self, *args, **kwargs):                                                     # part of format of class based views, this will handle the "GET" requests from the user 
        order = Order.objects.get(user=self.request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
        if order.billing_address:                                                       # Only if there is a billing address entered in the Order class then proceed with the following:
            context = {                                                                 # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
                'order': order,                                                         # order is equal to the order definied above
                'SHOW_COUPON_FORM': False,                                              # connected to order_snippet.html
                'STRIPE_PUBLIC_KEY' : settings.PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:                                         # we check if one click purchasing is activated here
                # fetch the users card list
                cards = stripe.Customer.list_sources(                                       # if it is activated then we fetch the customer's cards with list_sources, and specify the arguments, the userprofile, the limits of results, the objects, which is card
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )                                                                           # then we get a list of cards which we can iterate through or grab the first one 
                card_list = cards['data']
                if len(card_list) > 0:                                                      # if the list of cards is greater than 0 then we update the context to have a card, the very first card [0] 
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You're missing a billing address buddy :(")
            return redirect("core:checkout-page")

    def post(self, *args, **kwargs):
        try:
            host = self.request.get_host()      
            order = Order.objects.get(user=self.request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable      
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # TODO: replace this with the `price` of the product you want to sell
                    'price_data': {
                    'unit_amount': int(order.get_total() * 100),
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Final Total Order Completion',
                        'images': ['https://i.pinimg.com/564x/11/07/f2/1107f2935eea21bebb21b56712ad2c8e.jpg'],
                        },
                    },
                    'quantity': 1,
                    },
                    ],
                payment_method_types=[
                'card'
                ],
                mode='payment',
                success_url="http://{}{}".format(host, reverse('core:payment-success')),
                cancel_url="http://{}{}".format(host, reverse('core:payment-cancel'))
            )
            return redirect(checkout_session.url, code=303)

        except stripe.error.CardError as e:                                             # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            messages.warning(self.request, f"{'Message is: %s' % e.user_message}")      # we show a warning message. The message code was taken from stripe https://stripe.com/docs/api/errors/handling 

        except stripe.error.RateLimitError as e:                                        # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            # Too many requests made to the API too quickly                             
            messages.warning(self.request, "You've got a rate limit error")                                          # we show a warning message. 

        except stripe.error.InvalidRequestError as e:                                   # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            # Invalid parameters were supplied to Stripe's API                          
            messages.warning(self.request, "You've got an invalid request error")                                          # we show a warning message. 

        except stripe.error.AuthenticationError as e:                                   # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            # Authentication with Stripe's API failed                                   
            # (maybe you changed API keys recently)
            messages.warning(self.request, "You've got an authentication error")                                          # we show a warning message. 

        except stripe.error.APIConnectionError as e:                                    
            # Network communication with Stripe failed                                  
            messages.warning(self.request, "There is an API connection error")                                          # we show a warning message. 

        except stripe.error.StripeError as e:                                           # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, "We've got a stripe error. Don't worry, you've not been charged.")                                          # we show a warning message. 

        except Exception as e:                                                          # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
            # Something else happened, completely unrelated to Stripe
            messages.warning(self.request, "There is a seriour error. We've been notified, and you've not been charged. Euston we have a problem here! :(")                                          # we show a warning message. 


def paymentSuccess(request):
    order = Order.objects.get(user=request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable      

    order_items = order.items.all()                                             # here we ask for all items from the Item class from the Order class to be shown. This is saved to a variable
    order.reference_code = create_reference_code()                                    # The reference code in the order class is going to be set equal to the function above created to make random reference codes
    order_items.update(ordered=True)                                            # Then we update all these items and set ordered to being "True" meaning that the items have been ordered.
    for item in order_items:                                                    # we start looping over each item in the variable, so this sets all of the ordered to true, and then we save all of them                                         
        item.save()

    order.ordered = True                                                        # order has been set to true so the order is completed
    order.save()

    order_success = Order.objects.filter(user=request.user, ordered=True, reference_code=order.reference_code)                # This is to get and set the variable to pull back the Order that has now been completed as per reference code and save it to the variable    

    context = {
        'payment_status': 'success',                                           # Set the payment status to success
        'order_success': order_success                                         # here we try to connect the previous code to fetch the order that has been completed so that we can fetch the reference code and other order details to post to the success.html page after payment
    }                                                                          # ref to https://www.youtube.com/watch?v=H3joYTIRqKk&ab_channel=Codemy.com for details on doing this step

    messages.success(request, "Your order was successful")
    return render(request, 'success.html', context)                             # we render the success.html and the context containing the order_success code variable
  

def paymentCancel(request):
    context = {
        'payment_status': 'cancel'
    }
    return render(request, 'cancel.html', context)


    # def post(self, *args, **kwargs):                                                    # This will handle the POST requests made by the user, such as in a form for example. This is all part of the format. 
    #     order = Order.objects.get(user=self.request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable. The user is going to be set as the user who is making the request. THis is the "Self.request.user"   
    #     form = PaymentForm(self.request.POST)
    #     userprofile = UserProfile.objects.get(user=self.request.user)
    #     if form.is_valid():
    #         token = form.cleaned_data.get('stripeToken')                                       # We receive the token. request.POST['sth'] will raise a KeyError exception if 'sth' is not in request.POST. request.POST.get('sth') will return None if 'sth' is not in request.POST. Additionally, .get allows you to provide an additional parameter of a default value which is returned if the key is not in the dictionary. For example, request.POST.get('sth', 'mydefaultvalue') This is the behavior of any python dictionary and is not specific to request.POST. REF https://stackoverflow.com/questions/12518517/request-post-getsth-vs-request-poststh-difference
    #         save = form.cleaned_data.get('save')                                            # To save the current card that we get from the user
    #         use_default = form.cleaned_data.get('use_default')                              # to use the default card
        
    #         if save:                                                                        # if we are going to save it, then we will assign it to the user
    #             if not userprofile.stripe_customer_id: # if the userprofile.stripe_cust_id (from models.py) does not exist, then proceed with the below code. first we check if there is a stripe customer id associated on that user profile, if not then that means that this is the first time the user is saving information
    #                 customer = stripe.Customer.create(             # so since such a user doesn't exist, we're going to create a new customer and pass the source as the token (the card that they just entered)
    #                     email=self.request.user.email,         # retrieve based on the stripe_customer_id
    #                     source=token                            # they pass in the source as the card that they enter in
    #                 )                 
    #                 userprofile.stripe_customer_id = customer['id'] # here we assign the stripe customer id to the api call of the customer (customer[id])
    #                 userprofile.one_click_purchasing = True         # for future references
    #                 userprofile.save() 
    #             else:
    #                 stripe.Customer.create_source(                                      # since the customer does exist, then we create a source (part of stripe)
    #                     userprofile.stripe_customer_id,                                 # these are features of creating the source in the previous line. You enter the stripe customer id and the source being equal to token
    #                     source=token
    #                 )

    #         amount = int(order.get_total() * 100)                                           # To get the total from the order class. It is put in "int" to convert to an integer value. It is multiplied with 100 because of the cents.

    #         try:
    #             if use_default or save:
    #                 # charge the customer because we cannot charge the token more than once
    #                 charge = stripe.Charge.create(                                              # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     amount=amount,  # cents                                                 # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     currency="usd",                                                         # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     customer=userprofile.stripe_customer_id     #source=token                            # the stripe customer id is obtained and stored in customer variable. XX From stripe website ref https://stripe.com/docs/api/charges/create
    #             )
    #             else:
    #                 # charge the customer because we cannot charge the token more than once
    #                 charge = stripe.Charge.create(                                              # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     amount=amount,  # cents                                                 # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     currency="usd",                                                         # From stripe website ref https://stripe.com/docs/api/charges/create
    #                     source=token                                                            # From stripe website ref https://stripe.com/docs/api/charges/create
    # #                 )
    #             # We create the payment here
    #             payment = Payment()                                                         # Payment is from the Payment class in models.py. We save it to a variable
    #             payment.stripe_charge_id = charge['id']                                     # part of the format of the Payment class from models.py. Here we're trying to grab the id from the charge that is made by the user in line 105
    #             payment.user = self.request.user                                            # Again part of the payment class format. Here we're setting the user to be the user who has made the request
    #             payment.amount = order.get_total()                                          # Again part of the format. Here we set amount equal to the total of the order with get_total
    #             payment.save()                                                              # Finally we save the payment

    #             # Here we assign the payment to the order

    #             order_items = order.items.all()                                             # here we ask for all items from the Item class from the Order class to be shown. This is saved to a variable
    #             order_items.update(ordered=True)                                            # Then we update all these items and set ordered to being "True" meaning that the items have been ordered.
    #             for item in order_items:                                                    # we start looping over each item in the variable, so this sets all of the ordered to true, and then we save all of them                                         
    #                 item.save()

    #             order.ordered = True
    #             order.payment = payment
    #             order.reference_code = create_reference_code()                                    # The reference code in the order class is going to be set equal to the function above created to make random reference codes
    #             order.save()

    #             messages.success(self.request, "Your order was successful!")
    #             return redirect("/")
    
    #         except stripe.error.CardError as e:                                             # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             messages.warning(self.request, f"{'Message is: %s' % e.user_message}")      # we show a warning message. The message code was taken from stripe https://stripe.com/docs/api/errors/handling 

    #         except stripe.error.RateLimitError as e:                                        # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             # Too many requests made to the API too quickly                             
    #             messages.warning(self.request, "You've got a rate limit error")                                          # we show a warning message. 

    #         except stripe.error.InvalidRequestError as e:                                   # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             # Invalid parameters were supplied to Stripe's API                          
    #             messages.warning(self.request, "You've got an invalid request error")                                          # we show a warning message. 

    #         except stripe.error.AuthenticationError as e:                                   # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             # Authentication with Stripe's API failed                                   
    #             # (maybe you changed API keys recently)
    #             messages.warning(self.request, "You've got an authentication error")                                          # we show a warning message. 

    #         except stripe.error.APIConnectionError as e:                                    
    #             # Network communication with Stripe failed                                  
    #             messages.warning(self.request, "There is an API connection error")                                          # we show a warning message. 

    #         except stripe.error.StripeError as e:                                           # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             # Display a very generic error to the user, and maybe send
    #             # yourself an email
    #             messages.warning(self.request, "We've got a stripe error. Don't worry, you've not been charged.")                                          # we show a warning message. 

    #         except Exception as e:                                                          # Taken from the stripe format ref https://stripe.com/docs/api/errors/handling for python
    #             # Something else happened, completely unrelated to Stripe
    #             messages.warning(self.request, "There is a seriour error. We've been notified, and you've not been charged. Euston we have a problem here! :(")                                          # we show a warning message. 

            #     except stripe.error.CardError as e:
            #     body = e.json_body
            #     err = body.get('error', {})
            #     messages.warning(self.request, f"{err.get('message')}")
            #     return redirect("/")

            # except stripe.error.RateLimitError as e:
            #     # Too many requests made to the API too quickly
            #     messages.warning(self.request, "Rate limit error")
            #     return redirect("/")

            # except stripe.error.InvalidRequestError as e:
            #     # Invalid parameters were supplied to Stripe's API
            #     print(e)
            #     messages.warning(self.request, "Invalid parameters")
            #     return redirect("/")

            # except stripe.error.AuthenticationError as e:
            #     # Authentication with Stripe's API failed
            #     # (maybe you changed API keys recently)
            #     messages.warning(self.request, "Not authenticated")
            #     return redirect("/")

            # except stripe.error.APIConnectionError as e:
            #     # Network communication with Stripe failed
            #     messages.warning(self.request, "Network error")
            #     return redirect("/")

            # except stripe.error.StripeError as e:
            #     # Display a very generic error to the user, and maybe send
            #     # yourself an email
            #     messages.warning(
            #         self.request, "Something went wrong. You were not charged. Please try again.")
            #     return redirect("/")

            # except Exception as e:
            #     # send an email to ourselves
            #     messages.warning(
            #         self.request, "A serious error occurred. We have been notifed.")
            #     return redirect("/")

        # messages.warning(self.request, "Invalid data received")
        # return redirect("/payment/stripe/")


class HomeView(ListView):                                                               # A page representing a list of objects. This is used if you want to show lists of objects. While this view is executing, self.object_list will contain the list of objects (usually, but not necessarily a queryset) that the view is operating upon. ref https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview
    model = Item                                                                        # as part of the format in https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview Item is a class                                                           
    template_name = "home-page.html"                                                    # The full name of a template to use as defined by a string. Not defining a template_name will raise a django.core.exceptions.ImproperlyConfigured exception. ref https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-simple/#django.views.generic.base.TemplateResponseMixin.template_name
    paginate_by = 10                                                                     # as part of the format in https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview This is for pagination

    def get_context_data(self, *args, **kwargs):                                        # This is made as part of our categories obtainer to put on the navbar. get_context_data: This method is used to populate a dictionary to use as the template context. https://stackoverflow.com/questions/36950416/when-to-use-get-get-queryset-get-context-data-in-django
        cat = Category.objects.all()                                                    # we select all the objects present in the Category model
        context = super(HomeView, self).get_context_data(*args, **kwargs)               # ref https://www.youtube.com/watch?v=2MkULPXXXLk
        context["cat"] = cat                                                            # to get the context saved to "cat"
        return context
        

class OrderSummaryView(LoginRequiredMixin, View):                                       # View created for the order summary. When using class-based views, you can achieve the same behavior as with login_required by using the LoginRequiredMixin. This mixin should be at the leftmost position in the inheritance list. If a view is using this mixin, all requests by non-authenticated users will be redirected to the login page or shown an HTTP 403 Forbidden error, depending on the raise_exception parameter. ref https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-loginrequired-mixin  Class-based views provide an alternative way to implement views as Python objects instead of functions. ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#handling-forms-with-class-based-views
    def get(self, *args, **kwargs):                                                     # part of format of class based views, this will handle the "GET" requests from the user
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)            # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
            context = {                                                                 # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
                'object': order                                                         # object is equal to the order definied above
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:                                                      # If an error is caught after trying the above then the objectdoesnotexist error is given. The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


def aboutus(request):                                                                   # This is a function for our aboutus page, it takes in a request                                # here we try to connect the previous code to fetch the order that has been completed so that we can fetch the reference code and other order details to post to the success.html page after payment       
    return render(request, "about-us.html")


def contactus(request):                                                                 # This is a function for our contactus page, it takes in a request                                # here we try to connect the previous code to fetch the order that has been completed so that we can fetch the reference code and other order details to post to the success.html page after payment       
    return render(request, "contact-us.html")                     


class ProductDetailView(DetailView):                                                    # Detail view is if your item has a lot of details in it. Django DetailView refers to that type of view that shows a single instance from the Model Table. ref https://www.askpython.com/django/django-detailview
    model = Item                                                                        # as part of the format in https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#detailview Item is a class                                                           
    template_name = "product-page.html"                                                 # The full name of a template to use as defined by a string. Not defining a template_name will raise a django.core.exceptions.ImproperlyConfigured exception. ref https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-simple/#django.views.generic.base.TemplateResponseMixin.template_name


    def get_context_data(self, *args, **kwargs):                                        # We made this context processor so that we could loop over the Items model in each product page to display all the items in each product page
        each_item = Item.objects.all()                                                  # we select all the objects present in the Category model
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)      # ref https://www.youtube.com/watch?v=2MkULPXXXLk
        context["each_item"] = each_item     
        return context

@login_required                                                                         # From loginrequired mixin format for decorators ref https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-loginrequired-mixin
def addition_to_cart(request, slug):                                                    # Function created to make the feature for adding items to the cart. It accepts two parameters i.e. the request which will come from the user and slug which will also come from the user. This is going to take the Item, create an order item, and assign the orderitem to the order if the user has an order otherwise if not, then its going to create an order on the spot. If you remove the order, it's going to remove the order from the items field. In the next line, slug is set equal to the slug of the item.
    item = get_object_or_404(Item, slug=slug)                                           # get_object_or_404 Calls get() on a given model manager, but it raises Http404 instead of the model’s DoesNotExist exception. get_object_or_404(klass, *args, **kwargs) where klass is A Model class, a Manager, or a QuerySet instance from which to get the object. and kwargs are Lookup parameters, which should be in the format accepted by get() and filter(). This function calls the given model and get object from that if that object or model doesn’t exist it raise 404 error.ref https://docs.djangoproject.com/en/3.2/topics/http/shortcuts/#get-object-or-404 ref https://www.geeksforgeeks.org/get_object_or_404-method-in-django-models/
    order_item, created = OrderItem.objects.get_or_create(                              # This is as per the format. order_item here is the variable where the Object returned as a result of the code after that will be stored in that variable. A convenience method for looking up an object with the given kwargs (may be empty if your model has defaults for all fields), creating one if necessary. Returns a tuple of (object, created), where object is the retrieved or created object and created is a boolean specifying whether a new object was created. This is meant to prevent duplicate objects from being created when requests are made in parallel, and as a shortcut to boilerplatish code
        item=item,                                                                      # this is from the OrderItem class attribute                                  
        user=request.user,                                                              # this is from the OrderItem class attribute                                  
        ordered=False                                                                   # this is from the OrderItem class attribute                                  
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)                   # Filter from the Order class as per the attributes set here
    if order_qs.exists():                                                               # If this order query set exists then we will grab this order from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
        order = order_qs[0]                                                             # This refers to the first available order in the Order class
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():                           # If the items in the Order class on filtering have the slug equal to the slug from the Item class, then the quantity in the order_item class will be added a 1. Returns a new QuerySet containing objects that match the given lookup parameters. The lookup parameters (**kwargs) should be in the format described in Field lookups below. Multiple parameters are joined via AND in the underlying SQL statement. ref https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.query.QuerySet.filter
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)                                                 # If not, then add an order_item to the Order class items
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()                                                   # Returns a datetime that represents the current point in time. ref https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.timezone.now 
        order = Order.objects.create(                                                   # Creates a new object
            user=request.user, ordered_date=ordered_date)                               # user will be set equal to the user meaking the request and ordered date is set equal to the ordered date above
        order.items.add(order_item)                                                     # We add the ordered_item to the order class
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required                                                                         # From loginrequired mixin format for decorators ref https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-loginrequired-mixin
def remove_item_from_cart(request, slug):                                                    # this is a function to remove an item from the cart
    item = get_object_or_404(Item, slug=slug)                                           # get_object_or_404 Calls get() on a given model manager, but it raises Http404 instead of the model’s DoesNotExist exception. get_object_or_404(klass, *args, **kwargs) where klass is A Model class, a Manager, or a QuerySet instance from which to get the object. and kwargs are Lookup parameters, which should be in the format accepted by get() and filter(). This function calls the given model and get object from that if that object or model doesn’t exist it raise 404 error.ref https://docs.djangoproject.com/en/3.2/topics/http/shortcuts/#get-object-or-404 ref https://www.geeksforgeeks.org/get_object_or_404-method-in-django-models/
    order_qs = Order.objects.filter(                                                    # Filter from the Order class as per the attributes set here
        user=request.user,
        ordered=False
    )
    if order_qs.exists():                                                               # If this order query set exists then we will grab this order from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
        order = order_qs[0]                                                             # This refers to the first available order in the Order class
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():                           # If the items in the Order class on filtering have the slug equal to the slug from the Item class, then the quantity in the order_item class will be added a 1. Returns a new QuerySet containing objects that match the given lookup parameters. The lookup parameters (**kwargs) should be in the format described in Field lookups below. Multiple parameters are joined via AND in the underlying SQL statement. ref https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.query.QuerySet.filter
            order_item = OrderItem.objects.filter(                                      # Filter from the Orderitem class as per the attributes set here and pick the first entry [0]
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)                                              # if it exists then remove the order_item
            order_item.delete()  
            if order.coupon:
               order.coupon = None                                              # The code to delete the coupon code. ref https://stackoverflow.com/questions/62534452/django-how-to-remove-a-coupon-from-an-order-without-deleting-coupon-from-databa
               order.save()                                                       # delete the order item
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product-page", slug=slug)


@login_required                                                                     # From loginrequired mixin format for decorators ref https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-loginrequired-mixin
def remove_one_item_from_cart(request, slug):                                    # this is a function to remove a single quantity item from the cart
    item = get_object_or_404(Item, slug=slug)                                       # get_object_or_404 Calls get() on a given model manager, but it raises Http404 instead of the model’s DoesNotExist exception. get_object_or_404(klass, *args, **kwargs) where klass is A Model class, a Manager, or a QuerySet instance from which to get the object. and kwargs are Lookup parameters, which should be in the format accepted by get() and filter(). This function calls the given model and get object from that if that object or model doesn’t exist it raise 404 error.ref https://docs.djangoproject.com/en/3.2/topics/http/shortcuts/#get-object-or-404 ref https://www.geeksforgeeks.org/get_object_or_404-method-in-django-models/
    order_qs = Order.objects.filter(                                                # Filter from the Order class as per the attributes set here
        user=request.user,
        ordered=False
    )
    if order_qs.exists():                                                           # If this order query set exists then we will grab this order from the query set [0] refers to the first one. A QuerySet represents a collection of objects from your database. It can have zero, one or many filters. Filters narrow down the query results based on the given parameters. In SQL terms, a QuerySet equates to a SELECT statement, and a filter is a limiting clause such as WHERE or LIMIT . ref https://docs.djangoproject.com/en/3.2/topics/db/queries/#:~:text=A%20QuerySet%20represents%20a%20collection,such%20as%20WHERE%20or%20LIMIT%20.
        order = order_qs[0]                                                         # This refers to the first available order in the Order class
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():                       # If the items in the Order class on filtering have the slug equal to the slug from the Item class, then the quantity in the order_item class will be added a 1. Returns a new QuerySet containing objects that match the given lookup parameters. The lookup parameters (**kwargs) should be in the format described in Field lookups below. Multiple parameters are joined via AND in the underlying SQL statement. ref https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.query.QuerySet.filter
            order_item = OrderItem.objects.filter(                                  # Filter from the Orderitem class as per the attributes set here and pick the first entry [0]
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:                                             # If the quantity of the order item is greater than one then
                order_item.quantity -= 1                                            # then remove 1 quantity
                order_item.save()
            else:
                order.items.remove(order_item)                                      # otherwise just remove the order item
                if order.coupon:
                    order.coupon = None                                              # The code to delete the coupon code. ref https://stackoverflow.com/questions/62534452/django-how-to-remove-a-coupon-from-an-order-without-deleting-coupon-from-databa
                    order.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product-page", slug=slug)


def get_coupon(request, code):                                                      # This is a coupon function to get coupons and their codes
    try:
        coupon = Coupon.objects.get(code=code)                                      # From the coupon class, get the code that already exists in the server, and the code attribte should match with the code entered by the user. Remember the function takes in one argument from the user making the request and the other being the code
        return coupon
    except ObjectDoesNotExist:                                                      # If an error is caught after trying the above then the objectdoesnotexist error is given. The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class CouponAddView(View):                                                            # This is a class to add coupons that are added by the user. Class-based views provide an alternative way to implement views as Python objects instead of functions. ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#handling-forms-with-class-based-views
    def post(self, *args, **kwargs):                                                    # This will handle the POST requests made by the user, such as in a form for example. This is all part of the format. 
        form = CouponForm(self.request.POST or None)                                     # CouponForm from forms.py line 16. The use of or in this case does not evaluate to True or False, but returns one of the objects. Keep in mind that or is evaluated from left to right. When the QueryDict request.POST is empty, it takes a Falsy value, so the item on RHS of the or operation is selected (which is None), and the form is initialized without vanilla arguments (i.e. with None): ref https://stackoverflow.com/questions/38251922/logic-behind-formrequest-post-or-none
        if form.is_valid():                                                             # The primary task of a Form object is to validate data. With a bound Form instance, call the is_valid() method to run validation and return a boolean designating whether the data was valid. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#using-forms-to-validate-data
            try:
                code = form.cleaned_data.get('code')                                # The code feature is the only attribute from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
                order = Order.objects.get(user=self.request.user, ordered=False)         # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
                order.coupon = get_coupon(self.request, code)                            # This is saving the results of the get_coupon function to the coupon attribute of the Order class
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout-page")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout-page")
 
                                                                           # From loginrequired mixin format for decorators ref https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-loginrequired-mixin
def remove_coupon(request):                                                # This is a function to remove a coupon that has been applied                          # this is a function to remove an item from the cart
        try:
            order = Order.objects.get(user=request.user, ordered=False)         # we use get here because coupon is just one thing instead of many. filter will return Queryset.So use get instead of filter. If multiple objects are there use filter, but you need to loop over that queryset to get each objects. ref https://stackoverflow.com/questions/44284850/queryset-object-has-no-attribute This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable
            if order.coupon:
               order.coupon = None                                              # The code to delete the coupon code. ref https://stackoverflow.com/questions/62534452/django-how-to-remove-a-coupon-from-an-order-without-deleting-coupon-from-databa
               order.save()
            
            return redirect("core:order-summary")

        except ObjectDoesNotExist:                                                      # If an error is caught after trying the above then the objectdoesnotexist error is given. The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/
            messages.info(request, "This coupon does not exist")
            return redirect("core:order-summary")                                              # delete the order item


class RequestRefundView(View):                                                            # This is a class to request for a refund. Class-based views provide an alternative way to implement views as Python objects instead of functions. ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#handling-forms-with-class-based-views
    def get(self, *args, **kwargs):                                                     # part of format of class based views, this will handle the "GET" requests from the user
        form = RefundForm()                                                       # This is from forms.py line 16 
        context = {                                                                 # A Context is a dictionary with variable names as the key and their values as the value. Hence, if your context for the above template looks like: {myvar1: 101, myvar2: 102}, when you pass this context to the template render method, {{ myvar1 }} would be replaced with 101 and {{ myvar2 }} with 102 in your template. This is a simplistic example, but really a Context object is the context in which the template is being rendered. ref https://stackoverflow.com/questions/20957388/what-is-a-context-in-django
            'form': form                                                           # form is set equal to the form variable above
        }
        return render(self.request, "request_refund.html", context)                  # This is all part of the format. The render() function takes the request object as its first argument, a template name as its second argument and a dictionary as its optional third argument. It returns an HttpResponse object of the given template rendered with the given context. ref https://docs.djangoproject.com/en/3.2/intro/tutorial03/
    
    def post(self, *args, **kwargs):                                                    # This will handle the POST requests made by the user, such as in a form for example. This is all part of the format. 
        form = RefundForm(self.request.POST)
        if form.is_valid():                                                             # The primary task of a Form object is to validate data. With a bound Form instance, call the is_valid() method to run validation and return a boolean designating whether the data was valid. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#using-forms-to-validate-data
            reference_code = form.cleaned_data.get('reference_code')                                # The reference_code feature is the attribute from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
            message = form.cleaned_data.get('message')                                  # The message feature is the attribute from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
            email = form.cleaned_data.get('email')                                      # The email feature is the attribute from forms.py. Each field in a Form class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output. ref https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.cleaned_data
            # Here we try to edit the order
            try:
                order = Order.objects.get(reference_code = reference_code)         # This is to get and set the reference_code field of the Order class and save them to the 'order' variable. reference_code is defined a few lines earlier
                order.refund_requested = True                        # From models.py it's originally set to false there but here we set it to true
                order.save()

                # Here we try to store the refund
                refund = Refund()                                        # This is the Refund class from models.py
                refund.order = order                                     # We set the order attribute from the Refund class in models.py equal to the order variable which we defined in the previous line
                refund.reason = message                                  # We set the reason feature from the Refund class in models.py equal to the message varaible we defined earlier
                refund.email = email                                     # We set the email attribute from the Refund class in models.py equal to the order variable which we defined in the previous line

                messages.warning(self.request, "We've received your refund request.")
                return redirect("core:request-refund")                   # From urls.py
            except ObjectDoesNotExist:                                   # If an error is caught after trying the above then the objectdoesnotexist error is given. The base class for Model.DoesNotExist exceptions. A try/except for ObjectDoesNotExist will catch DoesNotExist exceptions for all models. ref https://docs.djangoproject.com/en/3.2/ref/exceptions/
                messages.warning(self.request, "Your order isn't here pal.")
                return redirect("core:request-refund")                   # From urls.py


@csrf_exempt                                                             # This is all taken from the stripe website except for fulfilling the order part where I've incorporated our order details in the code
def my_webhook_view(request):                                            # This code is all part of payment with stripe and fulfilling the order or closing the order once the order payment is successful
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

 # Handle the checkout.session.completed event
  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']

    # Fulfill the purchase...
    if session.payment_status == "paid":
        order = Order.objects.get(user=request.user, ordered=False)                # This is to get and set the user and ordered fields of the Order class and save them to the 'order' variable      
        order_items = order.items.all()                                             # here we ask for all items from the Item class from the Order class to be shown. This is saved to a variable
        order_items.update(ordered=True)                                            # Then we update all these items and set ordered to being "True" meaning that the items have been ordered.
        for item in order_items:                                                    # we start looping over each item in the variable, so this sets all of the ordered to true, and then we save all of them                                         
            item.save()

        order.ordered = True
        order.save()

  # Passed signature verification
  return HttpResponse(status=200)