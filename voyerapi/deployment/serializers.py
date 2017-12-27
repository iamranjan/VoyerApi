from rest_framework import serializers
from .models import CanvasContent
import json
from rest_framework import serializers


class ManageCardsSerializer(serializers.ModelSerializer):
    cards = serializers.JSONField()

    # username = serializers.TextField()
    class Meta:
        model = CanvasContent
        fields = ('username', 'cards', 'deployed', 'build_uuid', 'build_prog')

    def create(self, validated_data):
        print("ManageCardsSerializer:create:")
        print(validated_data)
        obj, created = CanvasContent.objects.update_or_create(username=validated_data['username'],
                                                              defaults={'cards': validated_data['cards']})
        obj.deployed = validated_data['deployed']
        obj.build_uuid = validated_data['build_uuid']
        obj.build_prog = validated_data['build_prog']
        obj.save()

        return obj

# class CardSerializer(s)
