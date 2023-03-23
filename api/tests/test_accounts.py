import pytest
from rest_framework import status
from django.urls import reverse
from apps.account.models import User
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

class TestRegistrationView:
    registration_url = reverse('signup')

    def test_registration_view_success(self, client):
        # valid data
        data = {
            'email': 'testuser@test.com',
            'password': 'testpassword',
            'first_name': 'test',
            'last_name': 'user',
            'phone_number': '+2348123456789',
            'username': 'testuser'
        }
        response = client.post(self.registration_url, data=data, format='json')

        # assert response status code and data
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == data['email']
        assert response.data['message'] == 'User created successfully'
        assert User.objects.count() == 1

    def test_registration_view_user_already_exists(self, client):
        # create a user with the same email
        mixer.blend(User, email='testuser@test.com')

        # data with existing email
        data = {
            'email': 'testuser@test.com',
            'password': 'testpassword',
            'first_name': 'test',
            'last_name': 'user',
            'phone_number': '+2348123456789',
            'username': 'testuser'
        }
        response = client.post(self.registration_url, data=data, format='json')
        # assert response status code and data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['validations']['email'] == 'User with this Email already exists.'
        assert User.objects.count() == 1

    def test_registration_view_invalid_data(self, client):
        # invalid data
        data = {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'testuser@test',
            'password': 'ps',
            'username': 'Test User',
            'phone_number': '1230'
        }
        response = client.post(self.registration_url, data=data, format='json')

        # assert response status code and data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username'     in response.data['validations']
        assert 'email'        in response.data['validations']
        assert 'phone_number' in response.data['validations']
        assert 'password'     in response.data['validations']
        
        assert User.objects.count() == 0

    def test_registration_view_missing_all_required_fields(self, client):
        # missing email
        data = {
        }
        response = client.post(self.registration_url, data=data, format='json')
        print(response.data)

        # assert response status code and data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username'   in response.data['validations']
        assert 'first_name' in response.data['validations']
        assert 'last_name'  in response.data['validations']
        assert 'email'      in response.data['validations']
        assert 'password'   in response.data['validations']
        assert User.objects.count() == 0

class TestLoginView:
    login_url = reverse('login')

    def test_login_success(self, client):
        # create a user object with valid credentials
        user = mixer.blend(User, email='testuser@gmail.com', is_active=True)
        user.set_password('testpass@334')
        user.save()

        # send login request with valid credentials
        response = client.post(self.login_url, {'email': 'testuser@gmail.com', 'password': 'testpass@334'}, format='json')

        # check if response status code is 200
        assert response.status_code == status.HTTP_200_OK

        # check if the response data is correct
        assert 'id' in response.data
        assert 'email' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_login_inactive_user(self, client):
        # create a user object with inactive status
        user = mixer.blend(User, email='testuser@gmail.com', is_active=False)
        user.set_password('testpass@334')
        user.save()
        # send login request with valid credentials but inactive user
        response = client.post(self.login_url, {'email': 'testuser@gmail.com', 'password': 'testpass@334'}, format='json')

        # check if response status code is 400
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data
        assert response.data['detail'] == 'Invalid username/password'

    def test_login_invalid_credentials(self, client):
        # create a user object with valid credentials
        user = mixer.blend(User, email='testuser@gmail.com', is_active=True)
        user.set_password('testpass')
        user.save()
        # send login request with invalid credentials
        response = client.post(self.login_url, {'email': 'testuserinvalid@gmail.com', 'password': 'wrongpass'}, format='json')

        # check if response status code is 400
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # check if the response data is correct
        assert 'detail' in response.data
        assert response.data['detail'] == 'Invalid username/password'


