from .models import Category
from django.db.utils import OperationalError, ProgrammingError

# This is made as part of our categories obtainer to put on the navbar. get_context_data: This method is used to populate a dictionary to use as the template context. https://stackoverflow.com/questions/36950416/when-to-use-get-get-queryset-get-context-data-in-django
def get_context_data(request):              # This context processor was made so that this function could be made accessible to all our other templates of this website. A context processor has a simple interface: it’s a Python function that takes one argument, an HttpRequest object, and returns a dictionary that gets added to the template context. Each context processor must return a dictionary. ref https://www.youtube.com/watch?v=_eWLaL2g1bo
    try:
        cat = Category.objects.all()            # we select all the objects present in the Category model                                              
        return {'cat': cat}                     # ref https://www.youtube.com/watch?v=2MkULPXXXLk https://betterprogramming.pub/django-quick-tips-context-processors-da74f887f1fc https://www.youtube.com/watch?v=_eWLaL2g1bo

    except (OperationalError, ProgrammingError):
        return []  # No documents table yet