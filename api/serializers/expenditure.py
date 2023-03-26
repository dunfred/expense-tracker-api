from rest_framework import serializers
from apps.account.models import Expenditure

class UserExpenditureSerializer(serializers.ModelSerializer):
    estimatedAmount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, min_value=0.00)
    user  = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )
    class Meta:
        model = Expenditure
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

class UserExpenditureUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expenditure
        fields = ['id', 'category', 'nameOfItem', 'estimatedAmount']
        extra_kwargs = {
            'id': {'read_only': True},
            'category': {'read_only': True},
            'nameOfItem': {'read_only': True},
            'estimatedAmount': {'read_only': True},
        }

# SCHEMA
class UserExpenditureDeleteSchemaSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, read_only=True)