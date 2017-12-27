from django.shortcuts import render
from rest_framework import mixins
from rest_framework import generics
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import InventorySerializer, SubsetInventorySerializer
from .models import Inventory
from django.db.models import Q
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict

#
# class InventoryView(generics.GenericAPIView):
#     pass


# Create your views here.
class AllInventoryView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Create, update and delete jobs

    """
    serializer_class = InventorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_objects(self, pk):
        try:
            return Inventory.objects.filter(job__uuid=pk)
        except Inventory.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        List all inventory objects for a given job
        :param request:
        :return:
        """
        inventory = self.get_objects(pk)
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)


class SubsetInventoryView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Search for subset of jobs

    """
    serializer_class = SubsetInventorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_objects(self, pk, search_string):
        try:
            query = (Q(name__icontains=search_string) | Q(body__services__0=search_string)
                     | Q(body__visibility__0=search_string))
            return Inventory.objects.filter(query, job__uuid=pk)
        except Inventory.DoesNotExist:
            raise Http404

    def get(self, request, pk, search_string):
        """
        Search for inventory objects according to search_string
        :param request:
        :param pk: job uuid
        :param search_string: pattern to search with
        :return:
        """
        print("INVENTORY:SUBSET:PK:{}".format(pk))
        print("INVENTORY:SUBSET:search_string:{}".format(search_string))
        inventory = self.get_objects(pk, search_string)
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)
