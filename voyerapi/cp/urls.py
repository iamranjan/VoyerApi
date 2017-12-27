from django.conf.urls import url
from .views import CPAccessRuleViewShow, CPAccessRuleViewDelete, CPAccessRuleViewUpdate
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(_(r'^rules/(?P<pk>[0-9a-f-]+)$'), CPAccessRuleViewShow.as_view(), name='rules-show'),
    url(_(r'^rules/(?P<pk>[0-9a-f-]+)/(?P<rule_number>[0-9]+)$'), CPAccessRuleViewDelete.as_view(), name='rules-delete'),
    url(_(r'^rules/(?P<pk>[0-9a-f-]+)/(?P<rule_number>[0-9]+)$'), CPAccessRuleViewUpdate.as_view(), name='rules-update')
]
