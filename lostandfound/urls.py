from django.conf.urls import include, url

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

    url(r'^cloak/', include('cloak.urls')),
]
