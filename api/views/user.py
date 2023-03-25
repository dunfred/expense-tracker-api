from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from api.utils.renderers import LoginRenderer
from rest_framework_simplejwt.views import TokenRefreshView
from apps.account.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers.user import (
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
from rest_framework.serializers import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

'''
class UserViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterUserSerializer
    # Register a new user
    @extend_schema(
        request=RegisterUserSerializer,
        responses={status.HTTP_201_CREATED: UserRegisterSchemaSerializer},
        summary='Register User',
        description='This endpoint is used to create a user using a valid email and password',
        methods=['post'],
        operation_id='createUser'
    )
    @action(
        methods=['post'],
        url_path='auth/signup',
        url_name='register_user',
        detail=False,
    )
    def register_user(self, request):
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
'''

# AUTH
class RegistrationView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = RegisterUserSerializer
    permission_classes = (permissions.AllowAny, )

    @extend_schema(
        request      = RegisterUserSerializer,
        responses    = {status.HTTP_201_CREATED: UserRegisterSchemaSerializer},
        summary      = 'Register User',
        description  = 'This endpoint is used to create a user using a valid email and password',
        methods      = ['post'],
        operation_id = 'createUser',
        tags         = ["user"],
        examples=[
            OpenApiExample(
                'Example 1',
                value={
                    "id": "7D1C57A7-72A8-4BC3-A392-E809DE18F7E4",
                    "email": "john@email.com",
                    "message": "User created successfully"
                },
                status_codes=['201'],
                response_only=True,
            ),
        ],

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
    """
    Custom TokenObtainPairView that returns extra user information upon successful login.
    """
    serializer_class = LoginSerializer
    renderer_classes = [LoginRenderer]
    permission_classes = (permissions.AllowAny, )

    @extend_schema(
        request      = serializer_class,
        responses    = {
            status.HTTP_200_OK: OpenApiResponse(
                                        response=UserLoginSchemaSerializer,
                                        description='successful operation'
                ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                                        response=None,
                                        description='Invalid username/password'
                )
            },
        summary      = 'Login User',
        description  = 'This endpoint is used to login a user in.',
        methods      = ['post'],
        operation_id = 'loginUser',
        tags         = ["user"],
        examples=[
            OpenApiExample(
                'Example 1',
                value={
                    "data": {
                        "id": "7D1C57A7-72A8-4BC3-A392-E809DE18F7E4",
                        "email": "john@email.com",
                        "tokens": {
                        "access_token":  "......",
                        "refresh_token": "......"
                        }
                    }
                },
                status_codes=['200'],
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token = serializer.validated_data['access']
            refresh_token = serializer.validated_data['refresh']
            return Response(
                {
                    'id': user.id,
                    'email': user.email,
                    'tokens': {
                        'access': str(token),
                        'refresh': str(refresh_token)
                    }
                },
                status=status.HTTP_200_OK
            )
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserTokenRefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny, )

    @extend_schema(
        responses    = {status.HTTP_201_CREATED: RefreshTokenSchemaSerializer},
        summary      = 'Token Refresh',
        description  = 'This endpoint is used to request a new access token',
        methods      = ['post'],
        operation_id = 'tokenRefresh',
        tags         = ["user"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer

    @extend_schema(
        request     = serializer_class,
        responses   = {
            status.HTTP_200_OK: OpenApiResponse(
                                    response=None,
                                    description='User logged out successfully'
                                ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                                    response=None,
                                    description='Invalid refresh token'
                                )
        },
        summary     = 'Logs out current logged in user',
        description = 'This endpoint invalidates the refresh token and kills the user session.',
        methods     = ['post'],
        operation_id= 'logoutUser',
        tags        = ["user"],
        
    )
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(status=status.HTTP_200_OK)
            except:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)

# USER
class UserProfileView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @extend_schema(
        parameters=[
            OpenApiParameter(name='userID', description='The userID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses    = {status.HTTP_200_OK: serializer_class},
        summary      = 'Get user by user ID',
        methods      = ['get'],
        operation_id = 'getUser',
        tags         = ["user"]
    )
    def get(self, request, userID):
        try:
            user = User.objects.get(pk=userID)
        except:
            user = None
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(
        parameters=[
            OpenApiParameter(name='userID', description='The userID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        request      = UserUpdateSerializer,
        responses    = {status.HTTP_200_OK: UserUpdateSchemaSerializer},
        summary      = 'Update user by user ID',
        methods      = ['put'],
        operation_id = 'updateUser',
        tags         = ["user"]
    )
    def put(self, request, userID):
        try:
            user = User.objects.get(pk=userID)
        except:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        try:
            serializer = UserUpdateSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'User details updated successfully!'}, status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response({'detail': 'Invalid user data'}, status=status.HTTP_400_BAD_REQUEST)

