import pytest
from django.urls import reverse
from rest_framework import status
from apps.account.models import Expenditure
from api.serializers.expenditure import UserExpenditureSerializer

pytestmark = pytest.mark.django_db

def mock_method(*arg, **kwargs):
    raise Exception('Some exception')

class TestUserExpenditure:
    list_create_url       = reverse('list_create_expenditures')

    def test_expenditure_list_and_create_view(self, api_client, user):
        api_client.force_authenticate(user=user) # Authenticates the request

        # Create expenditure
        response1 = api_client.post(self.list_create_url, data={'category': 'transport', 'nameOfItem':'transport', 'estimatedAmount': 2000.0}, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.data['category'] ==  'transport'
        assert response1.data['nameOfItem'] ==  'transport'
        assert float(response1.data['estimatedAmount']) ==  float(2000.0)

        # Get expenditure list
        response2 = api_client.get(self.list_create_url)
        assert response2.status_code == status.HTTP_200_OK
        assert user.expenditures.count() == len(response2.data)

    def test_expenditure_retrieve_update_and_delete_successful_requests(self, api_client, user, user_expenditure):
        api_client.force_authenticate(user=user) # Authenticates the request
        get_update_delete_url = reverse('retrieve_get_update_delete_expenditure', args=[user_expenditure.id])

        # To test __str__ method of the Expenditure model
        print(user_expenditure)

        # Get expenditure
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(user_expenditure.id)
        assert response.data['category'] == user_expenditure.category
        assert response.data['nameOfItem'] == user_expenditure.nameOfItem
        assert float(response.data['estimatedAmount']) == float(user_expenditure.estimatedAmount)
        
        # Update expenditure
        response = api_client.put(get_update_delete_url, data={'category': 'bills', 'nameOfItem':'light bills', 'estimatedAmount': 9000.0}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['category'] == "bills"
        assert response.data['nameOfItem'] == "light bills"
        assert float(response.data['estimatedAmount']) == float(9000.0)

        # Delete expenditure
        response = api_client.delete(get_update_delete_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'message': 'Expenditure deleted successfully!'}

        # Attempt to get deleted expenditure should return 404
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_expenditure_retrieve_update_and_delete_unsucessful_requests(self, api_client, user):
        api_client.force_authenticate(user=user) # Authenticates the request
        get_update_delete_url = reverse('retrieve_get_update_delete_expenditure', args=['9999'])

        # Get expenditure
        response = api_client.get(get_update_delete_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid expenditure ID'
        
        # Update expenditure
        # Testing with an invalid expenditure ID
        response = api_client.put(get_update_delete_url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid expenditure ID'

        # Testing with a valid but non-existent expenditure ID
        a_valid_non_existent_expenditure_id = '76581097-8da1-45e5-bbba-fe7ee51f61b7'
        url = reverse('retrieve_get_update_delete_expenditure', args=[a_valid_non_existent_expenditure_id])
        response = api_client.put(url, data={'nameOfRevenue': 'Bonus', 'amount': 7000.0}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Expenditure not found'

        # Delete expenditure
        # Testing with an invalid expenditure ID
        response = api_client.delete(get_update_delete_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Invalid expenditure ID'

        # Testing with a valid but non-existent expenditure ID
        a_valid_non_existent_expenditure_id = '76581097-8da1-45e5-bbba-fe7ee51f61b7'
        url = reverse('retrieve_get_update_delete_expenditure', args=[a_valid_non_existent_expenditure_id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Expenditure not found'

    def test_expenditure_update_exception_raised_when_serializing(self, mocker, api_client, user, user_expenditure):
        api_client.force_authenticate(user=user) # Authenticates the request
        url = reverse('retrieve_get_update_delete_expenditure', args=[user_expenditure.id])
        
        # Checking if error during serializing is been handled
        with mocker.patch.object(UserExpenditureSerializer, 'is_valid', side_effect=mock_method):

            response = api_client.put(url, data={'category': 'bills', 'nameOfItem':'light bills', 'estimatedAmount': 9000.0}, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['message'] == 'Invalid expenditure data'
    
    def test_expenditure_delete_exception_raised_when_deleting(self, mocker, api_client, user, user_expenditure):
        api_client.force_authenticate(user=user) # Authenticates the request
        url = reverse('retrieve_get_update_delete_expenditure', args=[user_expenditure.id])
        
        # Checking if error during expenditure delete is been handled
        with mocker.patch.object(Expenditure, 'delete', side_effect=mock_method):
            response = api_client.delete(url)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['message'] == 'Error deleting expenditure!'
