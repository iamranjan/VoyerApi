from django.conf.urls import url
from .views import ManageCardsView
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(_(r'^cards$'), ManageCardsView.as_view(), name='cards'),
]
