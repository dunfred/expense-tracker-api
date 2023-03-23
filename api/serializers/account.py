from apps.account.models import User
from rest_framework import serializers
# from django.db.models import Sum, F, Value
from django.contrib.auth import user_logged_in
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.serializers import PasswordField, TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password as user_validate_password

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        exclude = [
            'is_superuser', 
            'is_staff',
            'is_active',
            'password',
            'user_permissions',
            'groups',
            'last_login',
            'date_joined',
        ]

class RegisterUserSerializer(serializers.ModelSerializer):
    """Seralizer for user registration."""
    password     = serializers.CharField(max_length=255, required=True, style={"input_type": "password"}, write_only=True)
    phone_number = PhoneNumberField(max_length=20, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
        ]

    # def validate(self, attrs):
    #     """Validation for password and phone number."""
    #     try:
    #         password_validation.validate_password(attrs["password"])
    #     except ValidationError as e:
    #         raise serializers.ValidationError({'password': str(e)})

    #     if User.objects.filter(phone_number=attrs["phone_number"]).exists():
    #         raise serializers.ValidationError({'phone_number': 'This phone number is already taken'})

    #     return attrs
    def validate_password(self, value):
        try:
            user_validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        password = validated_data.get('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
        ]

class LoginSerializer(TokenObtainPairSerializer):
    """Password login serializer for user"""
    user_serializer = UserSerializer

    default_error_messages = {'no_active_account': ('Invalid username/password')}

    def __init__(self, *args, **kwargs):
        """Overriding to change the error messages."""
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(
            error_messages={"blank": "Invalid username"}
        )
        self.fields['password'] = PasswordField(
            error_messages={"blank": "Invalid password"}
        )

    def validate(self, attrs):
        """Overriding to return custom response"""
        super().validate(attrs) # keep this to ensure the self.user attr is set

        if not self.user.is_active:
            raise serializers.ValidationError({'detail': 'Your account is not active.'})

        refresh = self.get_token(self.user)

        resp = {
            'id': self.user.id,
            'email': self.user.email,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }
        # Add extra responses here

        user_logged_in.send(sender=self.user.__class__, request=self.context['request'], user=self.user)
        return resp
    
class TokenSerializer(serializers.Serializer):
    """Token Serializer"""
    access_token  = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class LogoutSerializer(serializers.Serializer):
    """Logout Serializer"""
    refresh_token = serializers.CharField(required=True)

# Schemas

class UserLoginSchemaSerializer(serializers.Serializer):
    """User login schema"""
    id      = serializers.UUIDField(read_only=True)
    email   = serializers.EmailField(read_only=True)
    tokens  = serializers.DictField(
        read_only=True,
        child=TokenSerializer()
    )

class UserLogoutSchemaSerializer(serializers.Serializer):
    """User logout schema"""
    message = serializers.CharField(read_only=True)

class UserUpdateSchemaSerializer(serializers.Serializer):
    """User update schema"""
    message = serializers.CharField(read_only=True)

class UserRegisterSchemaSerializer(serializers.Serializer):
    """User Register schema"""
    id      = serializers.UUIDField(read_only=True)
    email   = serializers.EmailField(read_only=True)
    message = serializers.CharField(read_only=True)

class RefreshTokenSchemaSerializer(serializers.Serializer):
    """Refresh Token schema"""
    access_token  = serializers.CharField(read_only=True)
