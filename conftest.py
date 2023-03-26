import uuid
import pytest
from apps.account.models import Expenditure, Income, User
from mixer.backend.django import mixer
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# Creating global reusable fixtures

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    user_obj = mixer.blend(User,
        email='nobody@nomail.com',
        phone_number='+233277528582',
    )
    user_obj.set_password('test_user')
    user_obj.save()
    return user_obj

@pytest.fixture
def user_income(user):
    user_income_obj = mixer.blend(Income,
        id=uuid.uuid4(),
        user=user
    )
    return user_income_obj

@pytest.fixture
def user_expenditure(user):
    user_expenditure_obj = mixer.blend(Expenditure,
        id=uuid.uuid4(),
        category="transport",
        nameOfItem="transport",
        user=user
    )
    return user_expenditure_obj

@pytest.fixture
def refresh_token(user):
    refresh_token = RefreshToken.for_user(user)
    return str(refresh_token)

@pytest.fixture
def access_token(user):
    token = AccessToken.for_user(user)
    return str(token)