from identity.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from requests.auth import HTTPBasicAuth

class CreateUserTest(APITestCase):
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
        self.registerData = {'username': 'mike', 'first_name': 'Mike', 'last_name': 'Tyson',
                             'email': 'mike.tyson@email.com', 'password':'password'}
        self.loginData = {'username': 'mike', 'password': 'password'}
        print('SETUP COMPLETE')

    def test_can_create_user(self):
        response = self.client.post(reverse('register'), self.registerData)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_can_login_user(self):
    #     print(self.loginData)
    #     response = self.client.post(reverse('login'), self.loginData)
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
