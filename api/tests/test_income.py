import pytest
from django.urls import reverse
from rest_framework import status
from apps.account.models import Income
from api.serializers.income import UserIncomeSerializer

pytestmark = pytest.mark.django_db

def mock_method(*arg, **kwargs):
    raise Exception('Some exception')

class TestUserIncome:
    list_create_url       = reverse('list_create_incomes')

    def test_income_list_and_create_view(self, api_client, user):
        api_client.force_authenticate(user=user) # Authenticates the request

        # Create income
        response1 = api_client.post(self.list_create_url, data={'nameOfRevenue': 'Salary', 'amount': 5000.0}, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.data['nameOfRevenue'] ==  'Salary'
        assert float(response1.data['amount']) ==  float(5000.0)

        # Get income list
        response2 = api_client.get(self.list_create_url)
        assert response2.status_code == status.HTTP_200_OK
        assert user.incomes.count() == len(response2.data)

    def test_income_retrieve_update_and_delete_successful_requests(self, api_client, user, user_income):
        api_client.force_authenticate(user=user) # Authenticates the request
        get_update_delete_url = reverse('retrieve_get_update_delete_income', args=[user_income.id])

        # Get income
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(user_income.id)
        assert response.data['nameOfRevenue'] == user_income.nameOfRevenue
        assert float(response.data['amount']) == float(user_income.amount)
        
        # Update income
        response = api_client.put(get_update_delete_url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nameOfRevenue'] == "Bonus"
        assert float(response.data['amount']) == float(7000.0)

        # Delete income
        response = api_client.delete(get_update_delete_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'message': 'Income deleted successfully!'}

        # Attempt to get deleted income should return 404
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_income_retrieve_update_and_delete_unsucessful_requests(self, api_client, user):
        api_client.force_authenticate(user=user) # Authenticates the request
        get_update_delete_url = reverse('retrieve_get_update_delete_income', args=['9999'])

        # Get income
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid income ID'
        
        # Update income
        # Testing with an invalid income ID
        response = api_client.put(get_update_delete_url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid income ID'

        # Testing with a valid but non-existent income ID
        a_valid_non_existent_income_id = '76581097-8da1-45e5-bbba-fe7ee51f61b7'
        url = reverse('retrieve_get_update_delete_income', args=[a_valid_non_existent_income_id])
        response = api_client.put(url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Income not found'

        # Delete income
        # Testing with an invalid income ID
        response = api_client.delete(get_update_delete_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid income ID'

        # Testing with a valid but non-existent income ID
        a_valid_non_existent_income_id = '76581097-8da1-45e5-bbba-fe7ee51f61b7'
        url = reverse('retrieve_get_update_delete_income', args=[a_valid_non_existent_income_id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Income not found'

    def test_income_update_exception_raised_when_serializing(self, mocker, api_client, user, user_income):
        api_client.force_authenticate(user=user) # Authenticates the request
        url = reverse('retrieve_get_update_delete_income', args=[user_income.id])
        
        # Checking if error during serializing is been handled
        with mocker.patch.object(UserIncomeSerializer, 'is_valid', side_effect=mock_method):

            response = api_client.put(url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['message'] == 'Invalid income data'
    
    def test_income_delete_exception_raised_when_deleting(self, mocker, api_client, user, user_income):
        api_client.force_authenticate(user=user) # Authenticates the request
        url = reverse('retrieve_get_update_delete_income', args=[user_income.id])
        
        # Checking if error during income delete is been handled
        with mocker.patch.object(Income, 'delete', side_effect=mock_method):
            response = api_client.delete(url)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['message'] == 'Error deleting income!'
