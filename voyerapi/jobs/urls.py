from django.conf.urls import url
from .views import JobCreateView,JobDeleteView, JobStatusView, JobMetadataView, JobMetadataSubsetView
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(_(r'^start$'), JobCreateView.as_view(), name='start'),
    url(_(r'^delete/(?P<pk>[0-9a-f-]+)$'), JobDeleteView.as_view(), name='delete'),
    url(_(r'^status/(?P<pk>[0-9a-f-]+)$'), JobStatusView.as_view(), name='status'),
    url(_(r'^meta/(?P<pk>[0-9a-f-]+)$'), JobMetadataView.as_view(), name='metadata'),
    url(_(r'^meta/(?P<pk>[0-9a-f-]+)/(?P<field>[A-z-0-9]+)$'), JobMetadataSubsetView.as_view(), name='metadata-subset'),
]