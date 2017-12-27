from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer, UserCheckSerializer
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework import status
from rest_framework.response import Response
from lib.utils import AtomicMixin
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.exceptions import AuthenticationFailed
import base64
from django.contrib.auth import authenticate

#
class SCAPIAuthentication(BasicAuthentication):

    def authenticate(self, request):

        # Get the username and password
        credentials = {}
        if request.META['HTTP_AUTHORIZATION']:
            auth_header = request.META['HTTP_AUTHORIZATION']
            encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
            credentials['username'] = decoded_credentials[0]
            credentials['password'] = password = decoded_credentials[1]
        elif request.data.get('username') and request.data.get('password'):
            credentials['username'] = request.data.get('username')
            credentials['password'] = request.data.get('password')
        else:
            raise AuthenticationFailed('No credentials provided.')
        user = authenticate(**credentials)
        if user is None:
            raise AuthenticationFailed('Invalid username/password.')

        if not user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        return user, None  # authentication successful

    def authenticate_header(self, request):
        return None

class UserLoginView(GenericAPIView):
    """
    User login resource.
    ---
    post:
        omit_serializer: true
            parameters_strategy:
                form: replace
        parameters:
            - username:
              type: string
            - password:
              type: string
    """
    serializer_class = UserLoginSerializer
    # authentication_classes = (BasicAuthentication,)
    authentication_classes = (SCAPIAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        User login resource.
        """
        print('LOGGING:')
        print(request)
        print(request.user)
        print(dir(request))
        token = AuthToken.objects.create(request.user)
        print("TOKEN:%s" % token)
        return Response({
            'user': self.get_serializer(request.user).data,
            'token': token
        })


class UserLogoutView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        User logout resource.
        """
        print('LOGGING:')
        print(request)
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

class UserCheckView(GenericAPIView):
    serializer_class = UserCheckSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        User check resource.
        """
        print('CHECKING:')
        print(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutAllView(GenericAPIView):
    '''
    Log the user out of all sessions
    I.E. deletes all scauth tokens for the user
    '''
    serializer_class = UserLogoutSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserRegisterView(AtomicMixin, CreateModelMixin, GenericAPIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = ()

    def post(self, request):
        """User registration view."""
        return self.create(request)

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def retrieve(self, request, pk=None):
#         if pk == 'i':
#             return response.Response(UserSerializer(request.user,
#                                                     context={'request': request}).data)
#         return super(UserViewSet, self).retrieve(request, pk)


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
