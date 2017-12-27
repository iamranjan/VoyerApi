from rest_framework import serializers
import json
from rest_framework import serializers

from . models import CPAccessRule


class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPAccessRule
        fields = ("position", "source", "destination", "service", "action", "track")
