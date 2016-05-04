from django.conf.urls import include, url
from django.http import HttpResponseServerError
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token

from .items import views as items
from .views import home


urlpatterns = [
    url(r'^home$', home, name='home'),
    url(r'^items/admin-action/(?P<item_num>\d+)/$', items.adminaction, name='admin-action'),
    url(r'^$', items.checkin, name='index'),
    url(r'^items/checkin$', items.checkin, name='checkin'),
    url(r'^items/admin-itemlist$', items.admin_itemlist, name='admin-itemlist'),
    url(r'^items/itemlist$', items.itemlist, name='itemlist'),
    url(r'^items/autocomplete/?$', items.autocomplete, name='users-autocomplete'),
    url(r'^items/(?P<item_id>\d+)/$', items.printoff, name='printoff'),

    # CAS Authentication
    url(r'^accounts/login/$', 'arcutils.cas.views.login', name='login'),
    url(r'^accounts/logout/$', 'arcutils.cas.views.logout', name='logout'),
    url(r'^accounts/validate/$', 'arcutils.cas.views.validate', name='cas-validate'),
]


@requires_csrf_token
def server_error(request, template_name='500.html'):
    """Override default Django server_error view so context is passed.

    Otherwise, static files won't be loaded and default context vars
    won't be available (&c).

    If loading or rendering the template causes an error, a bare 500
    response will be returned.

    """
    try:
        template = loader.get_template(template_name)
        body, content_type = template.render(request=request), None
    except Exception:
        body, content_type = '<h1>Server Error (500)</h1>', 'text/html'
    return HttpResponseServerError(body, content_type=content_type)
