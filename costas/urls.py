# Note: Now that we have a working view as explained in the previous chapters. We want to access that view via a URL. Django has his own way for URL mapping and it's done by editing your project url.py file (myproject/url.py) When a user makes a request for a page on your web app, Django controller takes over to look for the corresponding view via the url.py file, and then return the HTML response or a 404 not found error, if not found. In url.py, the most important thing is the "urlpatterns" tuple. It’s where you define the mapping between URLs and views. ref: https://www.tutorialspoint.com/django/django_url_mapping.htmhttps://www.tutorialspoint.com/django/django_url_mapping.htm
# a mapping is composed of three elements − The pattern − A regexp matching the URL you want to be resolved and map. Everything that can work with the python 're' module is eligible for the pattern (useful when you want to pass parameters via url).
# The python path to the view − Same as when you are importing a module.
# ref: https://www.webforefront.com/django/namedjangourls.html

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),        
    path('accounts/', include('allauth.urls')),    # This tells Django to search for URL patterns in the file allauth/urls.py.
    path('', include('core.urls', namespace='core')),  # '' is the root directory (/). This tells Django to search for URL patterns in the file core/urls.py. The ability to use <namespace>:<name> to reference urls allows you to effectively access urls from multiple instances of the same Django app. ref: https://www.webforefront.com/django/namedjangourls.html
    path('paypal/', include('paypal.standard.ipn.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

