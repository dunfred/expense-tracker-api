from rest_framework import serializers
from apps.account.models import Income

class UserIncomeSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    user  = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )
    class Meta:
        model = Income
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

class UserIncomeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Income
        fields = ['nameOfRevenue', 'amount']
        extra_kwargs = {
            'nameOfRevenue': {'read_only': True},
            'amount': {'read_only': True},
        }

# SCHEMA
class UserIncomeDeleteSchemaSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100, read_only=True)
