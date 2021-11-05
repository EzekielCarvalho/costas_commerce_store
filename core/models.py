
# Notes: A model is the single, definitive source of information about your data. It contains the essential fields and behaviors of the data you’re storing. Generally, each model maps to a single database table.
# ref https://docs.djangoproject.com/en/3.2/topics/db/models/


from django.db.models.signals import post_save
from django.conf import settings                            #This is necessary since we want to make use of our auth user model. This is from Django settings. This isn’t a module – it’s an object. So importing individual settings is not possible. This extracts or sucks (abstracts) the concepts of default settings and site-specific settings; it presents a single interface. It also separates (decouples) the code that uses settings from the location of your settings. (ref: https://docs.djangoproject.com/en/2.2/topics/settings/#using-settings-in-python-code)
from django.db import models
from cloudinary.models import CloudinaryField
from django.db.models import Sum
from django.urls import reverse 
from django_countries.fields import CountryField
from django.db.utils import OperationalError, ProgrammingError

# CATEGORY_CHOICES = (                                        # This is a tuple (Python tuples are a data structure that store an ordered sequence of values. Tuples are immutable. This means you cannot change the values in a tuple. Tuples are defined with parenthesis.)
#     ('C', 'Compact'),                                        # First entry goes to the database, secnd entry is displayed on the page.
#     ('BR', 'Bridge'),                                        # These are for choices below which are A sequence consisting itself of iterables of exactly two items (e.g. [(A, B), (A, B) ...]) to use as choices for this field. If choices are given, they’re enforced by model validation and the default form widget will be a select box with these choices instead of the standard text field. (Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices))
#     ('DR', 'DSLR'),
#     ('MR', 'Mirrorless cameras')
# )


LABEL_CHOICES = (                                           # This is a tuple (Python tuples are a data structure that store an ordered sequence of values. Tuples are immutable. This means you cannot change the values in a tuple. Tuples are defined with parenthesis.)
    ('P', 'primary'),                                       # First entry goes to the database, secnd entry is displayed on the page.
    ('W', 'warning'),                                       # These are for choices below which are A sequence consisting itself of iterables of exactly two items (e.g. [(A, B), (A, B) ...]) to use as choices for this field. If choices are given, they’re enforced by model validation and the default form widget will be a select box with these choices instead of the standard text field. (Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices))
    ('D', 'danger')
)

ADDRESS_CHOICES = (                                           # This is a tuple (Python tuples are a data structure that store an ordered sequence of values. Tuples are immutable. This means you cannot change the values in a tuple. Tuples are defined with parenthesis.)
    ('B', 'Billing'),                                       # First entry goes to the database, secnd entry is displayed on the page.
    ('S', 'Shipping'),                                       # These are for choices below which are A sequence consisting itself of iterables of exactly two items (e.g. [(A, B), (A, B) ...]) to use as choices for this field. If choices are given, they’re enforced by model validation and the default form widget will be a select box with these choices instead of the standard text field. (Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices))
)


class Category(models.Model):                                # This is the way of connecting the user with his/ her credit card details
    
    name = models.CharField(max_length=255, blank=True, null=True)                  # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))

    def __str__(self):                                       # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return self.name

    def get_absolute_url(self):                              # Define a get_absolute_url() method to tell Django how to calculate the canonical (absolute, recognized) URL for an object. The reverse() function is usually the best approach to be used with get_absolute. One place Django uses get_absolute_url() is in the admin app.  If it makes sense for your model’s instances to each have a unique URL, you should define get_absolute_url(). It’s good practice to use get_absolute_url() in templates, instead of hard-coding your objects’ URLs.  The logic here is that if you change the URL structure of your objects, even for something small like correcting a spelling error, you don’t want to have to track down every place that the URL might be created. Specify it once, in get_absolute_url() and have all your other code call that one place.
        return reverse('core:home-page')                     # "SLUG" from line 26 models.py. "self.slug" is as per the format. "core" from urls.py from line 11 and product-page from line 18. The reverse() function can reverse a large variety of regular expression patterns for URLs, but not every possible one.  kwargs allows you to handle named arguments that you have not defined in advance. ref to for format: https://docs.djangoproject.com/en/3.2/ref/models/instances/#get-absolute-url 
try:
    CHOICES = Category.objects.all().values_list('name','name')  # This is going to grab all the entries made via admin to the Category model

    CATEGORY_CHOICES = []                                         # creates a dictionary

    for item in CHOICES:                                            # For each item that is present in the CHOICES results, append or add each of them to the CATEGORY_CHOICES dictionary.
        CATEGORY_CHOICES.append(item)

except (OperationalError, ProgrammingError):                # This is to avoid Programming errors from arising while deploying onto a new domain and host. This has been used to avoid errors
    pass


class UserProfile(models.Model):                              # This is the way of connecting the user with his/ her credit card details
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)   # We chose one to one field because each credit card info is associated with one user at a time rather than one card for many people, which would not be good. A one-to-one relationship. Conceptually, this is similar to a ForeignKey with unique=True, but the “reverse” side of the relation will directly return a single object.  ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.OneToOneField     # ref https://thetldr.tech/what-is-the-difference-between-blank-and-null-in-django/ . null=True would tell the underlying database that this field is allowed to save  null. blank=True is applicable in the Django forms layer, i.e. any user is allowed to keep empty this field in Django form or Admin page. blank value is stored in the database.For the price.)        # This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)    # The stripe customer id will get populated when if the user decides to save their customer informationw when they checkout i.e. if they click on the checkbox to save for future purchases in the payment page          # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: as CharField(max_length=None, **options))
    one_click_purchasing = models.BooleanField(default=False)            # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield

    def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
            return self.user.username                           # returns the username as the string representation


class Item(models.Model):                                   # This is going to be displayed in the site on the page where the products are displayed for users to purchase. Once it is added to the cart, it becomes an "OrderItem" (next class)
    try:
        title = models.CharField(max_length=100)                # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
        price = models.FloatField(blank=True, null=True)          # For the price. The FloatField class is sometimes mixed up with the DecimalField class. Although they both represent real numbers, they represent those numbers differently. FloatField uses Python’s float type internally, while DecimalField uses Python’s Decimal type. A floating-point number represented in Python by a float instance. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.FloatField
        discount_price = models.FloatField(blank=True, null=True)          # ref https://thetldr.tech/what-is-the-difference-between-blank-and-null-in-django/ . null=True would tell the underlying database that this field is allowed to save  null. blank=True is applicable in the Django forms layer, i.e. any user is allowed to keep empty this field in Django form or Admin page. blank value is stored in the database.For the price. The FloatField class is sometimes mixed up with the DecimalField class. Although they both represent real numbers, they represent those numbers differently. FloatField uses Python’s float type internally, while DecimalField uses Python’s Decimal type. A floating-point number represented in Python by a float instance. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.FloatField
        category = models.CharField(choices=CATEGORY_CHOICES, max_length=255, default='uncategorized')     # Choices are A sequence consisting itself of iterables of exactly two items (e.g. [(A, B), (A, B) ...]) to use as choices for this field. If choices are given, they’re enforced by model validation and the default form widget will be a select box with these choices instead of the standard text field. (Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices)
        label = models.CharField(choices=LABEL_CHOICES, max_length=1)
        slug = models.SlugField()                               # A Slug is basically a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs. SlugField in Django is like a CharField, where you can specify max_length attribute also. If max_length is not specified, Django will use a default length of 50. It also implies setting Field.db_index to True.It is often useful to automatically prepopulate a SlugField based on the value of some other value.It uses validate_slug or validate_unicode_slug for validation. ref: https://www.geeksforgeeks.org/slugfield-django-models/
        description = models.CharField(max_length=5000)                # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
        additional_description = models.CharField(max_length=10000)                # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
        image = CloudinaryField('image')                        # For uploading images to cloudinary

        def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
            return self.title

        def get_absolute_url(self):                             # Define a get_absolute_url() method to tell Django how to calculate the canonical (absolute, recognized) URL for an object. The reverse() function is usually the best approach to be used with get_absolute. One place Django uses get_absolute_url() is in the admin app.  If it makes sense for your model’s instances to each have a unique URL, you should define get_absolute_url(). It’s good practice to use get_absolute_url() in templates, instead of hard-coding your objects’ URLs.  The logic here is that if you change the URL structure of your objects, even for something small like correcting a spelling error, you don’t want to have to track down every place that the URL might be created. Specify it once, in get_absolute_url() and have all your other code call that one place.
            return reverse('core:product-page', kwargs={'slug': self.slug})     # "SLUG" from line 26 models.py. "self.slug" is as per the format. "core" from urls.py from line 11 and product-page from line 18. The reverse() function can reverse a large variety of regular expression patterns for URLs, but not every possible one.  kwargs allows you to handle named arguments that you have not defined in advance. ref to for format: https://docs.djangoproject.com/en/3.2/ref/models/instances/#get-absolute-url

        def get_addition_to_cart_url(self):                     # This function was created mainly because to help with the add to cart feature
            return reverse('core:add-to-cart', kwargs={'slug': self.slug})     # "SLUG" from line 26 models.py. "self.slug" is as per the format. "core" from urls.py from line 11 and add-to-cart is from line 20. The reverse() function can reverse a large variety of regular expression patterns for URLs, but not every possible one.  kwargs allows you to handle named arguments that you have not defined in advance. ref to for format: https://docs.djangoproject.com/en/3.2/ref/models/instances/#get-absolute-url

        def get_remove_item_from_cart(self):                     # This function was created mainly because to help with the add to cart feature
            return reverse('core:remove-from-cart', kwargs={'slug': self.slug})     # "SLUG" from line 26 models.py. "self.slug" is as per the format. "core" from urls.py from line 11 and add-to-cart is from line 20. The reverse() function can reverse a large variety of regular expression patterns for URLs, but not every possible one.  kwargs allows you to handle named arguments that you have not defined in advance. ref to for format: https://docs.djangoproject.com/en/3.2/ref/models/instances/#get-absolute-url

    except (OperationalError, ProgrammingError):
        pass


class OrderItem(models.Model):                              # This is the way of connecting the item with the shopping cart (Order)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)          # ref https://thetldr.tech/what-is-the-difference-between-blank-and-null-in-django/ . null=True would tell the underlying database that this field is allowed to save  null. blank=True is applicable in the Django forms layer, i.e. any user is allowed to keep empty this field in Django form or Admin page. blank value is stored in the database.For the price.)        # This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    ordered = models.BooleanField(default=False)            # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    item = models.ForeignKey(Item, on_delete=models.CASCADE) # We connect the Item from the previous class to the OrderItem class. # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.ForeignKey)
    quantity = models.IntegerField(default=1)               # IntegerField is a integer number represented in Python by a int instance. This field is generally used to store integer numbers in the database. The default form widget for this field is a NumberInput when localize is False or TextInput otherwise. ref https://www.geeksforgeeks.org/integerfield-django-models/ and https://docs.djangoproject.com/en/3.2/ref/models/fields/
    
    def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return f"{self.quantity} of {self.item.title}"      # quantity refers to quantity in OrderItem class of the self.item.title (which is of the OderItem class, which connects to the Item class which has title)

    def get_total_item_price(self):                         # This is a method (A function) made to calculate the price based on the quantity of items in the cart. It multiples the quantity with the price of the product. item is form the OrderedItem class and price is from the Item class
        return self.quantity * self.item.price              

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price     # This is a method (A function) made to calculate the discounted price based on the quantity of items in the cart. It multiples the quantity with the discounted price of the product

    def get_amount_saved(self):                             #This method calculates how much the person saves
        return self.get_total_item_price() - self.get_total_discount_item_price()   # The total price minus the discounted price gives us how much you would save

    def get_final_amount(self):                             # This is a function made to get the final price, this is made so that we don't have to keep repeating the "inf there is a discounted price" logic as in line 49 order_summary html
        if self.item.discount_price:                        # If the discounted price exists
            return self.get_total_discount_item_price()     # Show the discounted price
        return self.get_total_item_price()                  # Esle show the original unaltered price


class Order(models.Model):                                  # For the purpose of connecting all the order items to the order. The order is our shopping cart.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)        # This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    reference_code = models.CharField(max_length=20, blank=True, null=True)                # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    items = models.ManyToManyField(OrderItem)               # The example used in the Django docs is of a Group, Person, and Membership relationship. A group can have many people as members, and a person can be part of many groups, so the Group model has a ManyToManyField that points to Person . ref: https://docs.djangoproject.com/en/3.2/topics/db/examples/many_to_many/  https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.ManyToManyField
    start_date = models.DateTimeField(auto_now_add=True)    # Moment the order was created. A date and time, represented in Python by a datetime.datetime instance. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#datetimefield
    ordered_date = models.DateTimeField()                   # A date and time, represented in Python by a datetime.datetime instance. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#datetimefield . Nothing has been added in the field since we intend to manually set the value the moment it is ordered
    ordered = models.BooleanField(default=False)            # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    billing_address = models.ForeignKey (
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)        # Because the Foreign Key is on the same model, we had to use "Related_name". The related_name attribute specifies the name of the reverse relation from the User model back to your model. If you don't specify a related_name, Django automatically creates one using the name of your model with the suffix _set, for instance User.map_set.all(). ref https://stackoverflow.com/questions/2642613/what-is-related-name-used-for
    shipping_address = models.ForeignKey (
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)        # Because the Foreign Key is on the same model, we had to use "Related_name". The related_name attribute specifies the name of the reverse relation from the User model back to your model. If you don't specify a related_name, Django automatically creates one using the name of your model with the suffix _set, for instance User.map_set.all(). ref https://stackoverflow.com/questions/2642613/what-is-related-name-used-for
    payment = models.ForeignKey (
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey (
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)     # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    received = models.BooleanField(default=False)            # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    refund_requested = models.BooleanField(default=False)    # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    refund_granted = models.BooleanField(default=False)      # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield

    # The process for our ecommerce site involves:
    # * adding an item to cart
    # * adding a billing address (possibilities of a failed checkout)
    # * paying (pre processing, processing, packaging, etc)
    # * item being delivered
    # * item received
    # * refunds

    # ForeignKey is A many-to-one relationship (in this case the billing address is one and the people who use it are many). Requires two positional arguments: the class to which the model is related and the on_delete option.
        # BillingAddress line 109 models.py and payment line 125, coupon is line 143
        # To create a recursive relationship – an object that has a many-to-one relationship with itself – use models.ForeignKey('self', on_delete=models.CASCADE).
        # REF https://docs.djangoproject.com/en/3.2/ref/models/fields/#foreignkey
        # you can use null=True and on_delete=models.SET_NULL to implement a simple kind of soft deletion.
        # ref https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django
        # null=True would tell the underlying database that this field is allowed to save  null.

        # blank=True is applicable in the Django forms layer, i.e. any user is allowed to keep empty this field in Django form or Admin page. blank value is stored in the database.
        # ref https://thetldr.tech/what-is-the-difference-between-blank-and-null-in-django/

    def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return self.user.username                           # returns the username as the string representation

    def get_total(self):                                    # This is a function made to get the total of all the items in the order
        total = 0                                           # total by default set to 0
        for order_item in self.items.all():                 # items is from the Order class above in models.py. For every order_item (randomly chosen name) in the items attribute in the Order class 
            total += order_item.get_final_amount()          # add total (which is = 0) to each order item getting the final amount from the OrderItem class, so you get the final price     (same as total = total + order_item.get_final_price)
        if self.coupon:                                     # If there is a coupon submitted from the user, then minus the amount of that coupon, from the total that we obtained from the previous step
            total -= self.coupon.amount                     # total = total - self.coupon.amount so the total has to be minused with the coupon's amount. "coupon" is definied some lines above as being connected ot the Coupon class below, which also has the "amount" attributed. This is the amount that the coupon is worth. This amount is minused with the total
        return total


class Address (models.Model):                                  # This is our billing address
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)               # This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    first_name = models.CharField(max_length=100)                                              # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    last_name = models.CharField(max_length=100)                                               # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    username = models.CharField(max_length=100)                                                # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))   
    street_address = models.CharField(max_length=100)                                          # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    apartment_address = models.CharField(max_length=100)                                       # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    country = CountryField(multiple=False)                                                     # From multi-choice ref https://github.com/SmileyChris/django-countries
    zip = models.CharField(max_length=100)                                                     # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)                     # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options)) Choices are A sequence consisting itself of iterables of exactly two items (e.g. [(A, B), (A, B) ...]) to use as choices for this field. If choices are given, they’re enforced by model validation and the default form widget will be a select box with these choices instead of the standard text field. (Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices)
    default = models.BooleanField(default=False)                                               # Everytime you tell to use an address as default, you will grab (Via other code) the address you created and set default to be true. A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield


    def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return self.user.username                           # returns the username as the string representation

    class Meta:                                             # Give your model metadata by using an inner class Meta ref https://docs.djangoproject.com/en/3.2/topics/db/models/#meta-options
            verbose_name_plural = 'Addresses'               # A human-readable name for the object, singular. ref https://docs.djangoproject.com/en/3.2/ref/models/options/#verbose-name Model metadata is “anything that’s not a field”, such as ordering options (ordering), database table name (db_table), or human-readable singular and plural names (verbose_name and verbose_name_plural). None are required, and adding class Meta to a model is completely optional.

    # We need to keep track of the stripe payments. Right now thus far we've not been doing that, so we create the below class

class Payment(models.Model):                                 # This is to keep track of stripe payments
    stripe_charge_id = models.CharField(max_length=50)       # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)   #  This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # ForeignKey is A many-to-one relationship (in this case the billing address is one and the people who use it are many). Requires two positional arguments: the class to which the model is related and the on_delete option.        # This is to associate the order with the user. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    # you can use null=True and on_delete=models.SET_NULL to implement a simple kind of soft deletion.
        # ref https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django
        # null=True would tell the underlying database that this field is allowed to save  null.

        # blank=True is applicable in the Django forms layer, i.e. any user is allowed to keep empty this field in Django form or Admin page. blank value is stored in the database.
        # ref https://thetldr.tech/what-is-the-difference-between-blank-and-null-in-django/
    amount = models.FloatField()        # A floating-point number represented in Python by a float instance. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.FloatField
    timestamp = models.DateTimeField(auto_now_add=True)     # A date and time, represented in Python by a datetime.datetime instance. Takes the same extra arguments as DateField. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#datetimefield

    def __str__(self):                                      # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return self.user.username                           # returns the username as the string representation

class Coupon(models.Model):         # This is for the coupon feature. A model is the single, definitive source of information about your data. It contains the essential fields and behaviors of the data you’re storing. Generally, each model maps to a single database table. ref https://docs.djangoproject.com/en/3.2/topics/db/models/ 
    code = models.CharField(max_length=15)           # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    amount = models.FloatField()        #  This is the mount of money worth for the coupon code. A floating-point number represented in Python by a float instance. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.FloatField

    def __str__(self):              # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return self.code   # returns the code variable as the string representation
        

class Refund(models.Model):                                  # This is our refund class
    order = models.ForeignKey(Order, on_delete=models.CASCADE)        # This is to associate the order with the Order class. Note: ForeignKey is a Django ORM (object relational mapping) field-to-column mapping for creating and working with relationships between tables in relational databases. Django has a powerful, built-in user authentication system that makes it quick and easy to add login, logout, and signup functionality to a website. The AUTH_USER_MODEL is a recommended approach for referencing a user in a models.py file (ref: https://learndjango.com/tutorials/django-best-practices-referencing-user-model). 
    # for the cascade feature, The on_delete method is used to tell Django what to do with model instances (examples, cases) that depend on the model instance you delete. (e.g. a ForeignKey relationship). The on_delete=models. CASCADE tells Django to cascade (pour, flood) the deleting effect i.e. continue deleting the dependent models as well. (Ref https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    reason = models.TextField()                                              # This is A string field, for small- to large-sized strings. (ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/) (syntax: ass CharField(max_length=None, **options))
    accepted = models.BooleanField(default=False)            # A true/false field. ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#booleanfield
    email = models.EmailField()                              # A CharField that checks that the value is a valid email address using EmailValidator. ref https://docs.djangoproject.com/en/3.2/ref/models/fields/#emailfield

    def __str__(self):              # in every model you should define the standard Python class method __str__() to return a human-readable string for each object. This string is used to represent individual records in the administration site (and anywhere else you need to refer to a model instance). Often this will return a title or name field from the model. (ref: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models)  
        return f"{self.pk}"         # this returns the primary key but it has to be in f strings because it's an ID not a string

#Ideally, every time a user model instance is created, a corresponding user profile instance must be created as well. This is usually done using signals. ref https://www.oreilly.com/library/view/django-design-patterns/9781788831345/b2ecd556-abe5-47a1-8276-4e18da9402f5.xhtml

# Signals are used to perform any action on modification of a model instance. The signals are utilities that help us to connect events with actions. We can develop a function that will run when a signal calls it. In other words, Signals are used to perform some action on modification/creation of a particular entry in Database. For example, One would want to create a profile instance, as soon as a new user instance is created in Database  ref https://www.geeksforgeeks.org/how-to-create-and-use-signals-in-django/

# ref https://docs.djangoproject.com/en/3.2/ref/signals/#post-save
def userprofile_receiver(sender, instance, created, *args, **kwargs):       # mostly as per format
    if created:                                                             # as per format. If that user is created then proceed with the next line
        userprofile = UserProfile.objects.create(user=instance)             # we use the post_save signal to create a user profile no sooner a user is created
    
post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL) # we specify the sender as the Auth user model. pre_save/post_save: This signal  works before/after the method save(). ref https://www.geeksforgeeks.org/how-to-create-and-use-signals-in-django/

# So what is happening is when the UserProfile model is saved, a signal is fired called userprofile_receiver which creates a useerprofile receiver instance with a foreign key pointing to the instance of the user. 
# receiver – The function who receives the signal and does something.
# sender – Sends the signal
# created — Checks whether the model is created or not
# instance — created model instance
# **kwargs –wildcard keyword arguments