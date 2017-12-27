from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from .serializers import ManageCardsSerializer
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import CanvasContent
from rest_framework.response import Response
import json


class ManageCardsView(CreateModelMixin, GenericAPIView, UpdateModelMixin):
    """
    Allows cards to be viewed or edited

    """
    serializer_class = ManageCardsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request:

        request.user.username - username corresponding to the authentication token used in the request.
        :return:
        """
        # print(dir(request))
        # print(request.user.username)
        print('DATA')
        print(request.data)
        print('HEADERS')
        # print(request.headers)
        request.data['username'] = request.user.username
        return self.create(request)
    def get(self, request):
        """

        :return:
        """
        try:
            obj = CanvasContent.objects.get(username=self.request.user.username)
            # object = objectsList.latest('date_created')

            return Response({
                'cards': obj.cards,
                'deployed': obj.deployed,
                'build_uuid': obj.build_uuid,
                'build_prog': obj.build_prog,
            })
        except CanvasContent.DoesNotExist:
            return Response({
                'cards': [],
                'deployed': 'false' ,
                'build_uuid': 'buildNotStarted',
                'build_prog': 0,
            })
