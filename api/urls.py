from django.urls import path
from api.views import account
# from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Auth
    path('auth/signup/', account.RegistrationView.as_view(), name='signup'),
    path('auth/login/', account.LoginView.as_view(), name='login'),
    path('auth/logout/', account.LogoutAPIView.as_view(), name='logout'),
    path('auth/refresh/', account.UserTokenRefreshView.as_view(), name='refresh'),
    path('auth/user/<str:userID>/profile/', account.UserProfileView.as_view(), name='user_profile'),
]

