import pytest
from rest_framework import status
from django.urls import reverse
from api.serializers.account import RegisterUserSerializer, UserSerializer, UserUpdateSerializer
from api.views.account import UserProfileView
from apps.account.models import User
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

def mock_method():
    raise Exception('Some exception')

# AUTH VIEW TESTS
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

    def test_registration_view_username_not_in_lowercase(self, client):
        # invalid data
        data = {
            'email': 'testuser@test.com',
            'password': 'testpassword',
            'first_name': 'test',
            'last_name': 'user',
            'phone_number': '+2348123456789',
            'username': 'TESTuser'
        }
        response = client.post(self.registration_url, data=data, format='json')

        # assert response status code and data
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['validations']['username'] == 'Username must be in lowercase letters.'
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

        # check if response status code is 401
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

        # check if response status code is 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # check if the response data is correct
        assert 'detail' in response.data
        assert response.data['detail'] == 'Invalid username/password'

class TestUserTokenRefreshView:
    refresh_token_url = reverse('refresh')

    def test_refresh_token_success(self, api_client, refresh_token):
        data = {'refresh': refresh_token}
        response = api_client.post(self.refresh_token_url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_token_missing_field(self, api_client):
        data = {}
        response = api_client.post(self.refresh_token_url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'refresh' in response.data['validations']

    def test_refresh_token_failure(self, api_client):
        data = {'refresh': 'invalid'}
        response = api_client.post(self.refresh_token_url, data=data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['validations']['code'] == 'token_not_valid'

class TestLogoutAPIView:
    logout_url = reverse('logout')

    def test_logout_success(self, api_client, user, refresh_token):
        data = {'refresh_token': refresh_token}
        response = api_client.post(self.logout_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'message': 'User logged out successfully'}

    def test_logout_failure(self, api_client):
        data = {}
        response = api_client.post(self.logout_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'refresh_token' in response.data['validations']

    def test_invalid_refresh_token(self, api_client):
        data = {'refresh_token': 'invalid_token'}
        response = api_client.post(self.logout_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data

# USER VIEW TESTS
class TestUserProfileView:
    def test_get_user_success(self, api_client, user, access_token):
        url = reverse('user_profile', args=[user.id])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

        response = api_client.get(url, **headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserSerializer(user).data

    def test_get_user_no_authentication(self, api_client, user, access_token):
        url = reverse('user_profile', args=[user.id])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_get_user_not_found(self, api_client, access_token):
        url = reverse('user_profile', args=['9999-ddd-cccc-vvv-rrr-sssd-gg-ss'])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

        response = api_client.get(url, **headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_success(self, api_client, user, access_token):
        url = reverse('user_profile', args=[user.id])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        data = {'first_name': 'newfirst', 'last_name': 'newlast', 'username': 'newuser'}
        
        response = api_client.put(url, data=data, format='json', **headers)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'User details updated successfully!'

    def test_update_user_no_authentication(self, api_client, user):
        url = reverse('user_profile', args=[user.id])
        data = {'first_name': 'newfirst', 'last_name': 'newlast', 'username': 'newuser'}
        
        response = api_client.put(url, data=data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_update_user_not_found(self, api_client, access_token):
        url = reverse('user_profile', args=['9999-ddd-cccc-vvv-rrr-sssd-gg-ss'])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        data = {'first_name': 'newfirst', 'last_name': 'newlast', 'username': 'newuser'}

        response = api_client.put(url, data=data, format='json', **headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_invalid_data(self, api_client, user, access_token):
        url = reverse('user_profile', args=[user.id])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        data = {'invalid_key': 'invalid_value'}

        response = api_client.put(url, data=data, format='json', **headers)

        # Should still return 200 OK because the invalid fields are ignored by serializer
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'User details updated successfully!'

    def test_update_user_exception_raised_when_serializing(self, mocker, api_client, user, access_token):
        url = reverse('user_profile', args=[user.id])
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        data = {'first_name': 'newfirst', 'last_name': 'newlast', 'username': 'newuser'}
        
        with mocker.patch.object(UserSerializer, 'is_valid', side_effect=mock_method) as mock_my_function:

            response = api_client.put(url, data=data, format='json', **headers)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['detail'] == 'Invalid user data'


