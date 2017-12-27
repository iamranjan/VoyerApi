from django.test import TestCase, Client
from identity.models import User
from knox.models import AuthToken
from .models import Job
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class StartJobTestCase(APITestCase):
    def setUp(self):
        self.testUsername = 'test_user'
        self.testPassword = 'test_user_password'
        self.email = "test_user@gmail.com"
        self.first_name = "test"
        self.last_name = "user"
        # create a test user
        self.user = User.objects.create_user(username=self.testUsername,
                                             password=self.testPassword,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)


    def testStartJob(self):
        client = APIClient()
        token = AuthToken.objects.create(self.user)
        data = {
            'job': 'example-job-project',
            'tags': [
                {"name": "debug"},
                {"name": "extra-output"}
            ]
        }
        # data = {
        #     'job': 'example-job-project',
        #     'tags': [
        #         "debug",
        #         "extra-output"
        #     ]
        # }
        response = client.post('/api/v1/jobs/start', data=data, format='json', HTTP_AUTHORIZATION="Token %s" % token)
        # print("DEBUG_OUTPUT:%s" % response.data)
        obj = Job.objects.get(username=self.user.username)
        # print("OBJ.username:%s" % obj.username)
        # print("OBJ.uuid:%s" % obj.uuid)
        # print("OBJ.job:%s" % obj.job)
        # print("OBJ.tags:%s" % obj.tags.all())
        # print("RESPONSE:data%s" % response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg='response http status should be 201 - CREATED')

    def testGetStatusFromNameJob(self):
        client = APIClient()
        token = AuthToken.objects.create(self.user)
        new_job_data = {
            'job': 'example-job-project',
            'tags': [
                {"name": "debug"},
                {"name": "extra-output"}
            ]
        }
        job_create_response = client.post('/api/v1/jobs/start', data=new_job_data, format='json',
                                          HTTP_AUTHORIZATION="Token %s" % token)
        job = Job.objects.get(uuid=job_create_response.data['uuid'])
        # print ("TEST:GET:JOB:%s" %job)
        # print("TEST:GET:JOB:UUID:%s" % job.uuid)
        uuid = job.uuid
        data = {
            'job': 'example-job-project',
        }
        url = '/api/v1/jobs/status/%s' % uuid
        response = client.get(url, HTTP_AUTHORIZATION="Token %s" % token)
        print("TEST:GET:JOB:RESPONSE:%s" % response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='response http status should be 200 - OK')

        # def testGetStatusFromUUIDJob(self):
        #         client = APIClient()
        #         token = AuthToken.objects.create(self.user)
        #         job = Job.objects.get(username='test_user')
        #         print("JOB:%s" % job)
        #         print("JOB:uuid%s" % job.uuid)
        #         data = {
        #             'uuid': job.uuid
        #         }
        #         response = client.get('/scauth/jobs/status', data=data, format='json', HTTP_AUTHORIZATION="Token %s" % token)
