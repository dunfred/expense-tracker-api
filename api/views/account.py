# from django.conf import settings
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from api.utils.renderers import LoginRenderer
from rest_framework_simplejwt.views import TokenRefreshView
from apps.account.models import User
from drf_yasg.utils import swagger_auto_schema
# from api.serializers.company import CompanySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# from api.utils.helper_funcs import generate_user_otp, verify_user_otp_not_invalid
# from api.utils.renderers import AdminSponsorResponseRenderer, AdminStaffListResponseRenderer, AdminStaffResponseRenderer, CompanyResponseRenderer, LoginRenderer, TokenResponseRenderer, UserResponseRenderer, AdminSponsorListResponseRenderer
from api.serializers.account import (
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSchemaSerializer,
    RegisterUserSerializer,
    UserLoginSchemaSerializer,
    UserLogoutSchemaSerializer,
    UserRegisterSchemaSerializer,
    UserSerializer,
    UserUpdateSchemaSerializer,
    UserUpdateSerializer
)
# from api.permissions import AdminStaffOnly
from drf_yasg import openapi
# from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_ARRAY, TYPE_STRING
# from api.pagination import SponsorsCustomPagination, StaffCustomPagination
# from django.db.models import Q
from rest_framework.serializers import ValidationError

# AUTH
class RegistrationView(generics.CreateAPIView):
    """ This endpoint is used to create a user using a valid email and password """
    authentication_classes = []
    serializer_class = RegisterUserSerializer
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(
        request_body=serializer_class, responses={status.HTTP_201_CREATED: UserRegisterSchemaSerializer}
    )
    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)
        
        ser.is_valid(raise_exception= True)
        # create the user
        ser.save()

        data = {
            'id': ser.data['id'],
            'email': ser.data['email'],
            'message': 'User created successfully'
        }
        
        return Response(data, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    """ This endpoint is used to log a user in. """
    serializer_class = LoginSerializer
    renderer_classes = [LoginRenderer]
    authentication_classes = []
    permission_classes = (permissions.AllowAny, )
 
    @swagger_auto_schema(
        request_body=serializer_class, responses={status.HTTP_200_OK: UserLoginSchemaSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserTokenRefreshView(TokenRefreshView):
    """ This endpoint is used to refresh the access token. """
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: RefreshTokenSchemaSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutAPIView(APIView):
    """ This endpoint invalidates the refresh token and kills the user session. """
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=serializer_class, responses={status.HTTP_200_OK: UserLogoutSchemaSerializer}
    )
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message':'User logged out successfully'}, status=status.HTTP_200_OK)
            except:
                raise ValidationError({'detail':'Invalid refresh token'})
        else:
            raise ValidationError({'refresh_token':'This field is required'})

# USER
class UserProfileView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, userID):
        try:
            user = User.objects.get(pk=userID)
        except:
            user = None
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    
    @swagger_auto_schema(
        request_body=UserUpdateSerializer, responses={status.HTTP_200_OK: UserUpdateSchemaSerializer}
    )
    def put(self, request, userID):
        try:
            user = User.objects.get(pk=userID)
        except:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        try:
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'User details updated successfully!'}, status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response({'detail': 'Invalid user data'}, status=status.HTTP_400_BAD_REQUEST)
        

# INCOME

# EXPENDITURE