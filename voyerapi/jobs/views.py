from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.views import APIView
from .serializers import JobSerializer, JobStatusSerializer, JobMetadataSerializer
from .models import Job, JobMetadata
from .tasks import manageJenkinsJob, deleteJenkinsJob
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from uuid import uuid4
from django.http import Http404, HttpResponse


# Create your views here.


class JobCreateView(CreateModelMixin, GenericAPIView):
    """
    Create, update and delete jobs

    """
    serializer_class = JobSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Create a new job

        request.user.username - username corresponding to the authentication token used in the request.
        :return:
        """
        # print('USERNAME:%s' % request.user.username)
        # print('DATA:%s' % request.data)
        uuid = uuid4()

        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer)

            serializer.save(username=request.user.username, uuid=uuid)
            manageJenkinsJob.delay(uuid)
            return Response({
                'status': 'STARTED',
                'uuid': uuid
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobDeleteView(CreateModelMixin, GenericAPIView):
    """
    delete jobs

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise Http404

    def delete(self, request, pk, ):
        """
        Delete a job with a given UUID
        :param request:
        :return:
        """
        obj = self.get_object(pk)
        print('GET:OBJ:%s' % obj)
        print('GET:OBJ:%s' % obj.tags.all())
        deleteJenkinsJob.delay(pk)
        serializer = JobStatusSerializer(obj)
        try:
            return Response(serializer.data)
        except:
            raise HttpResponse(satus=500)


class JobStatusView(APIView):
    """
    Create, update and cancel jobs

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Fetch running job status
        :return:
        """
        obj = self.get_object(pk)
        print('GET:OBJ:%s' % obj)
        print('GET:OBJ:%s' % obj.tags.all())
        # print('GET:DATA:%s' % request.data)
        serializer = JobStatusSerializer(obj)
        return Response(serializer.data)


class JobMetadataView(APIView):
    """
    Fetch metadata related to job completion

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            job = Job.objects.get(pk=pk)
            return JobMetadata.objects.get(job=job)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Fetch job metadata
        :return:
        """
        obj = self.get_object(pk)
        print('GET:META_OBJ:%s' % obj)
        print('GET:META_OBJ:S3:%s' % obj.s3)
        # print('GET:DATA:%s' % request.data)
        serializer = JobMetadataSerializer(obj)
        return Response(serializer.data)


class JobMetadataSubsetView(APIView):
    """
    Fetch subset of metadata associated with job

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            job = Job.objects.get(pk=pk)
            return JobMetadata.objects.get(job=job)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, pk, field, format=None):
        """
        Fetch meta data by subfield
        :return:
        """
        obj = self.get_object(pk)
        print('GET:META_OBJ:%s' % obj)
        print('GET:META_OBJ:FIELD:%s' % field)
        serializer = JobMetadataSerializer(obj)
        try:
            return Response(serializer.data[field])
        except:
            return HttpResponse("Failed to find field: {} in metadata".format(field))
