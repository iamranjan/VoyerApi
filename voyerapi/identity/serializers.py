from .models import User
from rest_framework import serializers
from lib.utils import validate_email as email_is_valid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')


class UserLogoutSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ()

class UserCheckSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ()


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('url', 'name')


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        """
        Create the object.
        :param validated_data: string
        """
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        """
        Validate if email is valid or there is an user using the email.
        :param value: string
        :return: string
        """

        if not email_is_valid(value):
            raise serializers.ValidationError('Please use a different email address provider.')

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use, please use a different email address.')

        return value
