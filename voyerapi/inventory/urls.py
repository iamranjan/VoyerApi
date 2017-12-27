from django.conf.urls import url
from .views import AllInventoryView, SubsetInventoryView
from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    url(_(r'^(?P<pk>[0-9a-f-]+)$'),
        AllInventoryView.as_view(), name='pk_inventory'),
    url(_(r'^(?P<pk>[0-9a-f-]+)/(?P<search_string>[0-9A-z-]+)$'),
        SubsetInventoryView.as_view(), name='subset_inventory'),
]
