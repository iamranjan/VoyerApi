from django.shortcuts import render
from django.shortcuts import render
from rest_framework import mixins
from rest_framework import generics
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AccessRuleSerializer
# from .serializers import
from inventory.models import Inventory
from django.http import Http404
from .lib import checkpoint
from rest_framework.response import Response
import time

from rest_framework import status
from django.forms.models import model_to_dict


# Create your views here.

class CPAccessRuleViewShow(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Interact with access rules on the checkpoint firewall

    """
    serializer_class = None
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get(self, request, pk):
        """
        List all of the rules on the CP firewall for a given job
        :param request:
        :return:
        """
        checkpointManager = checkpoint.Checkpoint(pk)
        checkpointManager.connect()
        rules = checkpointManager.get_rules()
        checkpointManager.disconnect()

        return Response(
            {
                "rules": rules,
            }
        )

class CPAccessRuleViewDelete(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = None
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk, ruleNumber):
        """
        Delete a given rule from the job uuid
        :param request:
        request.data = {
            "rule-number": "1"
        }
        :param pk:
        :return:
        """
        time.sleep(2)
        Response({
            "OK"
        })

class CPAccessRuleViewUpdate(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = AccessRuleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def post(self, request, pk, ruleNumber):
        """
        Delete a given rule from the job uuid
        :param request:
        request.data = {
            "rule-number": "1"
        }
        :param pk:
        :return:
        """
        time.sleep(2)
        Response({
            "OK"
        })
