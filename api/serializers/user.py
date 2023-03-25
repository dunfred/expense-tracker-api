from apps.account.models import User
from rest_framework import serializers
from django.contrib.auth import user_logged_in
from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.serializers import PasswordField, TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password as user_validate_password
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
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

    def validate_password(self, value):
        try:
            user_validate_password(value)
        except ValidationError as exc:
            # Throw a serializer validation error with the password errors
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
    """Password login serializer for user."""
    email = serializers.EmailField(required=True)
    password = PasswordField(required=True)
    
    default_error_messages = {'no_active_account': ('Invalid username/password')}

    def validate(self, attrs):
        """Overriding to return custom response."""
        data = super().validate(attrs) # keep this to ensure the self.user attr is set

        user_logged_in.send(sender=self.user.__class__, request=self.context['request'], user=self.user)
        return data
    
class TokenSerializer(serializers.Serializer):
    """Token Serializer."""
    access_token  = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class LogoutSerializer(serializers.Serializer):
    """Logout Serializer."""
    refresh_token = serializers.CharField(required=True)


# API Response Schemas
class UserLoginSchemaSerializer(serializers.Serializer):
    """User login schema."""
    id      = serializers.UUIDField(read_only=True)
    email   = serializers.EmailField(read_only=True)
    tokens  = serializers.DictField(
        read_only=True,
        child=TokenSerializer()
    )

class UserLogoutSchemaSerializer(serializers.Serializer):
    """User logout schema."""
    message = serializers.CharField(read_only=True)

class UserUpdateSchemaSerializer(serializers.Serializer):
    """User update schema."""
    message = serializers.CharField(read_only=True)

class UserRegisterSchemaSerializer(serializers.Serializer):
    """User Register schema."""
    id      = serializers.UUIDField(read_only=True)
    email   = serializers.EmailField(read_only=True)
    message = serializers.CharField(read_only=True)

class RefreshTokenSchemaSerializer(serializers.Serializer):
    """Refresh Token schema."""
    access_token  = serializers.CharField(read_only=True)
