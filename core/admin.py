# Note: The Django admin application can use your models to automatically build a site area that you can use to create, view, update, and delete records. This can save you a lot of time during development, making it very easy to test your models and get a feel for whether you have the right data. The admin application can also be useful for managing data in production, depending on the type of website. The Django project recommends it only for internal data management. all you must do to add your models to the admin application is to register them. After registering the models you have to create a new "superuser", login to the site, and create some items for the ecommerce site.
# Ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site

from django.contrib import admin

from .models import Item, Category, OrderItem, Order, Payment, Coupon, Refund, Address      # Classes you created in models.py


def make_refund_accepted(modeladmin, request, queryset):        # This function is to make a new action to update a bulk of order entries to refund_requested=False, refund_granted=True. First, we’ll need to write a function that gets called when the action is triggered from the admin. Ref to http://www.matrix.umcs.lublin.pl/DOC/python-django-doc/html/ref/contrib/admin/actions.html for writing action functions. The syntax is given there
    queryset.update(refund_requested=False, refund_granted=True)    # as per format, here we change refund_requested=False, refund_granted=True to be our actions


make_refund_accepted.short_description = "Update orders to refund granted"


class OrderAdmin(admin.ModelAdmin):                      # The ModelAdmin class is the representation of a model in the admin interface. Usually, these are stored in a file named admin.py in your application. Let’s take a look at an example of the ModelAdmin. ref https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin This class is made so that we can get a separate column in django admin which will show which orders were successful and which were not. Set list_display to control which fields are displayed on the change list page of the admin. If you don’t set list_display, the admin site will display a single column that displays the __str__() representation of each object. ref https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    list_display = ['user', 'ordered', 'received', 'billing_address', 'shipping_address', 'payment', 'coupon', 'being_delivered', 'refund_requested', 'refund_granted']                   # user is the heading of one column and "ordered" is the heading of the second column

    list_filter = ['ordered', 'received', 'billing_address', 'shipping_address', 'payment', 'coupon', 'being_delivered', 'refund_requested', 'refund_granted']      # This will create a filter box so that you can filter while searching

    search_fields = ['user__username', 'reference_code']          # we used __username because otherwise an error would come up related to icontains. You can use icontains lookup on text fields. user is related (integer) field. Instead of user use user__username. ref https://stackoverflow.com/questions/35012942/related-field-got-invalid-lookup-icontains            # This is so that we can search based on these fields

    list_display_links = [          # This is to add links in the table of orders in django admin. These entries will have their own rows and will have links
        'user',
        'billing_address',
        'payment',
        'coupon']

    actions = [make_refund_accepted]        # as par tof the format of making our own actions


class AddressAdmin(admin.ModelAdmin):        # The ModelAdmin class is the representation of a model in the admin interface. Usually, these are stored in a file named admin.py in your application. Let’s take a look at an example of the ModelAdmin. ref https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin This class is made so that we can get a separate column in django admin which will show which orders were successful and which were not. Set list_display to control which fields are displayed on the change list page of the admin. If you don’t set list_display, the admin site will display a single column that displays the __str__() representation of each object. ref https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    list_display = [
            'user',
            'first_name',
            'last_name',
            'username',
            'street_address',
            'apartment_address',
            'country',
            'zip',
            'address_type',
            'default' 
    ]

    list_filter = ['default', 'address_type', 'country']      # This will create a filter box so that you can filter while searching

    search_fields = ['user', 'street_address', 'apartment_address', 'zip', 'country']          # Set search_fields to enable a search box on the admin change list page. This should be set to a list of field names that will be searched whenever somebody submits a search query in that text box.

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)                       
admin.site.register(Payment)   
admin.site.register(Coupon)
admin.site.register(Category)
admin.site.register(Address, AddressAdmin)

                


