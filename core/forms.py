# This is a python file having the main structure of the form used in the project. It is a Django form
# ref https://docs.djangoproject.com/en/3.2/topics/forms/
# ref https://docs.djangoproject.com/en/3.2/topics/forms/


from django import forms
from django.http import request
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_OPTIONS = {
    ('S', 'Stripe'),
    ('P', 'PayPal')
}


class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=True)                                              # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    last_name = forms.CharField(required=True)                                               # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    username = forms.CharField(widget=forms.TextInput(attrs={             # On a real Web page, you probably don’t want every widget to look the same. You might want a larger input element for the comment, and you might want the ‘name’ widget to have some special CSS class. It is also possible to specify the ‘type’ attribute to take advantage of the new HTML5 input types. To do this, you use the Widget.attrs argument when creating the widget. In this case we manipulated the placeholder attribute. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Widget.attrs
        'placeholder': 'Enter your username'}))                                                # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/   
    shipping_address = forms.CharField(required=False)                           # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    shipping_address2 = forms.CharField(required=False)                        # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    shipping_country = CountryField(blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'}))  # we need to add "Required = False" incase we decide to use "use default shipping address"        # A Django application that provides country choices for use with forms, flag icons static files, and a country field for models. ref https://github.com/SmileyChris/django-countries       .formfield() is from the same repository under Custom forms heading     
# country select widget from https://github.com/SmileyChris/django-countries/ the attrs is A dictionary containing HTML attributes to be set on the rendered widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Widget.attrs
# This class was taken from the (now commented) class attribute in the boostrap format in the country element (line 103 forms.py)                                                                         
    shipping_zip = forms.CharField(required=False)                                                                         # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    
    first_name = forms.CharField(required=True)                                              # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    last_name = forms.CharField(required=True)                                               # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    username = forms.CharField(widget=forms.TextInput(attrs={             # On a real Web page, you probably don’t want every widget to look the same. You might want a larger input element for the comment, and you might want the ‘name’ widget to have some special CSS class. It is also possible to specify the ‘type’ attribute to take advantage of the new HTML5 input types. To do this, you use the Widget.attrs argument when creating the widget. In this case we manipulated the placeholder attribute. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Widget.attrs
        'placeholder': 'Enter your username'}))                                                # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/   
    billing_address = forms.CharField(required=False)                           # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    billing_address2 = forms.CharField(required=False)                        # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    billing_country = CountryField(blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'}))  # we need to add "Required = False" incase we decide to use "use default shipping address"        # A Django application that provides country choices for use with forms, flag icons static files, and a country field for models. ref https://github.com/SmileyChris/django-countries       .formfield() is from the same repository under Custom forms heading     
# country select widget from https://github.com/SmileyChris/django-countries/ the attrs is A dictionary containing HTML attributes to be set on the rendered widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Widget.attrs
# This class was taken from the (now commented) class attribute in the boostrap format in the country element (line 103 forms.py)                                                                         
    billing_zip = forms.CharField(required=False)    

    same_billing_address = forms.BooleanField(required=False)     # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    set_default_shipping = forms.BooleanField(required=False)     # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    use_default_shipping = forms.BooleanField(required=False)     # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    set_default_billing = forms.BooleanField(required=False)     # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    use_default_billing = forms.BooleanField(required=False)     # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_OPTIONS)             # These widgets make use of the HTML elements <select>, <input type="checkbox">, and <input type="radio">. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.RadioSelect


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={                       # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
        'class': 'form-control',                                                 # These lines are from order_snippet.html line 37                                 # On a real Web page, you probably don’t want every widget to look the same. You might want a larger input element for the comment, and you might want the ‘name’ widget to have some special CSS class. It is also possible to specify the ‘type’ attribute to take advantage of the new HTML5 input types. To do this, you use the Widget.attrs argument when creating the widget. In this case we manipulated the placeholder attribute. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Widget.attrs
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))                                                                         


class RefundForm(forms.Form):
    reference_code = forms.CharField()                             # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    message = forms.CharField(widget=forms.Textarea(attrs={        # A text area is provides a much larger area for data entry than a text field. Text areas are common for things such as entering comments or other large pieces of information. So how can we create a text area in Django. ref http://www.learningaboutelectronics.com/Articles/How-to-create-a-text-area-in-a-Django-form.php ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#django.forms.Textarea
        'rows': 4
    }))                               # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    email = forms.EmailField()                               # ref https://docs.djangoproject.com/en/3.2/ref/forms/fields/#emailfield


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)                   # A string field, for small- to large-sized strings. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    save = forms.BooleanField(required=False)                        # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
    use_default = forms.BooleanField(required=False)                 # A widget is Django’s representation of an HTML input element. The widget handles the rendering of the HTML, and the extraction of data from a GET/POST dictionary that corresponds to the widget. ref https://docs.djangoproject.com/en/3.2/ref/forms/widgets/ A true/false field. The default form widget for this field is CheckboxInput, or NullBooleanSelect if null=True. ref https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/