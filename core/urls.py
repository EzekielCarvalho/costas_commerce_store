# Note: Now that we have a working view as explained in the previous chapters. We want to access that view via a URL. Django has his own way for URL mapping and it's done by editing your project url.py file (myproject/url.py) When a user makes a request for a page on your web app, Django controller takes over to look for the corresponding view via the url.py file, and then return the HTML response or a 404 not found error, if not found. In url.py, the most important thing is the "urlpatterns" tuple. It’s where you define the mapping between URLs and views. ref: https://www.tutorialspoint.com/django/django_url_mapping.htmhttps://www.tutorialspoint.com/django/django_url_mapping.htm
# a mapping is composed of three elements − The pattern − A regexp matching the URL you want to be resolved and map. Everything that can work with the python 're' module is eligible for the pattern (useful when you want to pass parameters via url).
# The python path to the view − Same as when you are importing a module.
# The name − In order to perform URL reversing, you’ll need to use named URL patterns as done in the examples above. Once done, just start the server to access your view via :http://127.0.0.1/hello
# The name is used for accessingg that url from your Django / Python code.
# additional ref: https://www.geeksforgeeks.org/django-url-patterns-python/

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from .views import (
    CouponAddView, HomeView, ProductDetailView, addition_to_cart, aboutus, contactus, remove_item_from_cart, OrderSummaryView, CheckoutView, remove_one_item_from_cart, CouponAddView, RequestRefundView, PaymentView, paymentSuccess, paymentCancel, remove_coupon, my_webhook_view, process_payment, success_paypal, cancelled_paypal, searchbar
)

app_name = 'core'                                                   # With the help of the app_name value, you're able to differentiate between the future cases where name would be equal to 'core', such as in apps.py name = 'core'. ref: https://www.webforefront.com/django/namedjangourls.html

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),                 # (as_view is the format of the ListView usage. Ref : https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview and https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-display/#generic-views-of-objects) first value is the address link, second is the file to where the view is located, this is the path to the view and third is the name of the urlpattern. The name is used for accessingg that url from your Django / Python code. 
     
    path('admin/', admin.site.urls),
    
    path('accounts/', include('allauth.urls')),
                                                                                       # By assigning the url a name you can use this value as a reference in view methods and templates, which means any future changes made to the url path, automatically updates all url definitions in view methods and templates.
    path('checkout-page/', CheckoutView.as_view(), name='checkout-page'),

    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),          # The most direct way to use generic views is to create them directly in your URLconf. If you’re only changing a few attributes on a class-based view, you can pass them into the as_view() method call itself ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/#usage-in-your-urlconf

    path('product-page/<slug>/', ProductDetailView.as_view(), name='product-page'),     # the slug, and "as_view" and name are as per the format giving by Django for using the "Detail view". It is required. Ref: https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#detailview)

    path('about-us/', aboutus, name='about-page'),                                      # This is for our about us page. A simple static page

    path('contact-us/', contactus, name='contact-page'),                                # This is for our contact us page. A simple static page

    path('add-to-my-cart/<slug>/', addition_to_cart, name='add-to-cart'),               # This is in connection to the addition_to_cart function in the views.py

    path('add-coupon/', CouponAddView.as_view(), name='add-coupon'),                    # This is in connection to the addition_to_cart function in the views.py # (as_view is the format of the ListView usage. Ref : https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview and https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-display/#generic-views-of-objects) first value is the address link, second is the file to where the view is located, this is the path to the view and third is the name of the urlpattern. The name is used for accessingg that url from your Django / Python code. 

    path('remove-from-cart/<slug>/', remove_item_from_cart, name='remove-from-cart'),   # This is in connection to the remove_item_from_cart function in the views.py

    path('remove-coupon/', remove_coupon, name='remove-coupon'),                        # This is in connection to the remove_item_from_cart function in the views.py

    path('remove-item-from-cart/<slug>/', remove_one_item_from_cart, name='remove-one-item-from-cart'),    # This is in connection to the remove_one_item_from_cart function in the views.py

    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),           # The most direct way to use generic views is to create them directly in your URLconf. If you’re only changing a few attributes on a class-based view, you can pass them into the as_view() method call itself ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/#usage-in-your-urlconf payment_option will be either stripe or paypal as per forms.py payment_option feature. It's like the slug value before

    path('payment_via_paypal/', process_payment, name='process_payment'),
    
    path('success-paypal/', success_paypal, name='success_paypal'),
    
    path('cancelled-paypal/', cancelled_paypal, name='cancelled_paypal'),
    
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),           # The most direct way to use generic views is to create them directly in your URLconf. If you’re only changing a few attributes on a class-based view, you can pass them into the as_view() method call itself ref https://docs.djangoproject.com/en/3.2/topics/class-based-views/#usage-in-your-urlconf RequestRefundView is from views.py

    # path('final-checkout/', PaymentView.as_view(), name='final-checkout'),

    path('searchbar/', searchbar, name='searchbar'),

    path('payment-success/', paymentSuccess, name='payment-success'),

    path('payment-cancel/', paymentCancel, name='payment-cancel'),

    path('webhook/stripe', my_webhook_view, name='webhook-stripe')
]

if settings.DEBUG:                                                                          # supposed to be present with django installation automatically
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]