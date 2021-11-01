from django import template
from core.models import Order

register = template.Library()           # Required. This is to register our template tag. To be a valid tag library, the module must contain a module-level variable named register that is a template.Library instance, in which all the tags and filters are registered. ref: https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout

@register.filter                        # Here register.filter() is used as a decorator. A decorator in Python is a function that takes another function as its argument, and returns yet another function. Decorators can be extremely useful as they allow the extension of an existing function, without any modification to the original function source code. Python decorators allow you to change the behavior of a function without modifying the function itself. ref https://stackoverflow.com/questions/12046883/python-decorator-can-someone-please-explain-this
def cart_item_count(user):              # This is our template tag to do the counting of items in the shopping cart
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)         #ref to the Order class in models.py, we are filtering by the user. The user should be equal to the user that is entered into this function. Their previously ordered orders are not taken into consideration
        if qs.exists():                 # If the query set exists
            return qs[0].items.count()             # Get the first available order in the qs (query set), and .count counts the number of items (Also from the models.py)
    return 0                            # If the user is not authenticated (line 10) then return 0