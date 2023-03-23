import pytest
from apps.account.models import User
from mixer.backend.django import mixer
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

# @pytest.fixture
# def user():
#     user_obj = mixer.blend(User,
#         email='nobody@nomail.com',
#         phone_number='+233277528582',
#     )
#     user_obj.set_password('test_user')
#     user_obj.save()
#     return user_obj
