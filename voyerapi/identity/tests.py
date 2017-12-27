from django.core.urlresolvers import reverse
from .models import User
from rest_framework import status
from rest_framework.test import APITestCase
from requests.auth import HTTPBasicAuth
from knox.models import AuthToken
from deployment.models import CanvasContent

class PostDataTest(APITestCase):
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
        self.client.login(username='test_user', password='test_user_password')
        self.token = AuthToken.objects.create(self.user)
        self.data = {"cards": [{"name": "card1", "properties": "lol"},
                               {"name": "card552", "properties": "other"},
                               {"name": "card3", "properties": "another one!"}],
                     "deployed": False,
                     "build_uuid": "-1",
                     "build_prog": "-1"
                     }

        print('POST DATA SETUP COMPLETE')

    def test_can_post_data(self):
        # response = self.client.post(reverse('cards'), self.data) # try 'cards'
        response = self.client.post(reverse('cards'), data=self.data, format='json',
                                    HTTP_AUTHORIZATION='Token %s' % self.token)
        print(response.data)
        print('****')
        print(CanvasContent.objects.get(username='test_user').cards)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CanvasContent.objects.get(username='test_user').cards, self.data['cards'])

        # def test_can_create_user(self):
        #     response = self.client.post(reverse('deployment/cards'), self.registerData) # try 'cards'
        #     # print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # def test_can_login_user(self):
        #     print(self.loginData)
        #     response = self.client.post(reverse('login'), self.loginData)
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
