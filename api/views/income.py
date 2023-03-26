from django.forms import ValidationError
from rest_framework import permissions
from rest_framework import generics, status
from apps.account.models import Income
from api.serializers.income import UserIncomeDeleteSchemaSerializer, UserIncomeSerializer, UserIncomeUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.response import Response

# INCOME
class IncomeListCreateView(generics.ListCreateAPIView):
    queryset = Income.objects.order_by('-created_at')
    serializer_class = UserIncomeSerializer
    permission_classes = (permissions.IsAuthenticated, )

    # return qs containing incomes of logged in user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    # list
    @extend_schema(
        responses    = {status.HTTP_200_OK: serializer_class},
        summary      = "Get user's income data",
        description  = "This endpoint returns the user's income",
        methods      = ['get'],
        operation_id = 'getUserIncome',
        tags         = ["income"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # post
    @extend_schema(
        request      =serializer_class,
        responses    ={status.HTTP_201_CREATED: serializer_class},
        summary      ="Add income data",
        description  ="This endpoint allows you to add an income.",
        methods      =['post'],
        operation_id ='addUserIncome',
        tags         =["income"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class IncomeRetrieveUpdateDeleteView(generics.GenericAPIView):
    queryset = Income.objects.order_by('-created_at')
    serializer_class = UserIncomeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    lookup_field = 'id'

    # return qs containing incomes of logged in user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    # get
    @extend_schema(
        parameters=[
            OpenApiParameter(name='incomeID', description='The incomeID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses    ={status.HTTP_200_OK: serializer_class},
        summary      ="Get income data by ID",
        methods=     ['get'],
        operation_id ='getIncomeByID',
        tags         =["income"]
    )
    def get(self, request, incomeID):
        try:
            qs = self.get_queryset()
            income = qs.get(pk=incomeID)
        except Income.DoesNotExist:
            income = None
            return Response({'message': 'Income not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            income = None
            return Response({'message': 'Invalid income ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(income)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # put
    @extend_schema(
        parameters=[
            OpenApiParameter(name='incomeID', description='The incomeID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses    ={status.HTTP_200_OK: UserIncomeUpdateSerializer},
        summary      ="Update income data by ID",
        methods=     ['put'],
        operation_id ='updateIncomeByID',
        tags         =["income"]
    )
    def put(self, request, incomeID):
        try:
            income = Income.objects.get(pk=incomeID)
        except Income.DoesNotExist:
            income = None
            return Response({'message': 'Income not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            income = None
            return Response({'message': 'Invalid income ID'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        try:
            ser = UserIncomeSerializer(income, data=data, partial=True)
            if ser.is_valid():
                ser.save()
                resp = {
                    'nameOfRevenue': ser.data['nameOfRevenue'],
                    'amount': ser.data['amount'],
                }
                return Response(resp, status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response({'message': 'Invalid income data'}, status=status.HTTP_400_BAD_REQUEST)

    # delete
    @extend_schema(
        parameters=[
            OpenApiParameter(name='incomeID', description='The incomeID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses    ={status.HTTP_200_OK: UserIncomeDeleteSchemaSerializer},
        summary      ="Delete income data by ID",
        methods=     ['delete'],
        operation_id ='deleteIncomeByID',
        tags         =["income"]
    )
    def delete(self, request, incomeID):
        try:
            income = Income.objects.get(pk=incomeID)
        except Income.DoesNotExist:
            income = None
            return Response({'message': 'Income not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            income = None
            return Response({'message': 'Invalid income ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            income.delete()
        except Exception:
            return Response({'message': 'Error deleting income!'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Income deleted successfully!'}, status=status.HTTP_200_OK)
        

