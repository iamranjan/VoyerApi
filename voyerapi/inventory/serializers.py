from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'hostname', 'body')


class SubsetInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'hostname', 'body')
