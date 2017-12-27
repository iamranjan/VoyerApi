from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from .views import UserRegisterView, UserLoginView, UserLogoutView, UserCheckView

urlpatterns = [
    url(_(r'^login/$'),
        UserLoginView.as_view(),
        name='login'),
    url(_(r'^logout/$'),
        UserLogoutView.as_view(),
        name='login'),
    url(_(r'^register/$'),
        UserRegisterView.as_view(),
        name='register'),
    url(_(r'^check/$'),
        UserCheckView.as_view(),
        name='check'),
]
