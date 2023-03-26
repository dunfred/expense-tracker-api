from django.forms import ValidationError
from rest_framework import permissions
from rest_framework import generics, status
from apps.account.models import Expenditure
from rest_framework.response import Response
from api.serializers.expenditure import UserExpenditureDeleteSchemaSerializer, UserExpenditureSerializer, UserExpenditureUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# EXPENDITURE
class ExpenditureListCreateView(generics.ListCreateAPIView):
    queryset = Expenditure.objects.order_by('-created_at')
    serializer_class = UserExpenditureSerializer
    permission_classes = (permissions.IsAuthenticated, )

    # return qs containing expenditures of logged in user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-created_at')

    # list
    @extend_schema(
        responses={status.HTTP_200_OK: UserExpenditureSerializer},
        summary="Get user's expenditure data",
        description="This endpoint returns the user's expenditure",
        methods=['get'],
        operation_id='getUserExpenditure',
        tags=["expense"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # post
    @extend_schema(
        request=UserExpenditureSerializer,
        responses={status.HTTP_201_CREATED: UserExpenditureSerializer},
        summary="Add expenditure data",
        description="This endpoint allows you to add an expenditure.",
        methods=['post'],
        operation_id='addUserExpenditure',
        tags=["expense"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ExpenditureRetrieveUpdateDeleteView(generics.GenericAPIView):
    queryset = Expenditure.objects.order_by('-created_at')
    serializer_class = UserExpenditureSerializer
    permission_classes = (permissions.IsAuthenticated, )
    lookup_field = 'id'

    # return qs containing expenditures of logged in user only
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    # get
    @extend_schema(
        responses={status.HTTP_200_OK: UserExpenditureSerializer},
        summary="Get expenditure data by ID",
        methods=['get'],
        operation_id='getExpenditureByID',
        tags=["expense"]
    )
    def get(self, request, expenditureID):
        try:
            qs = self.get_queryset()
            expenditure = qs.get(pk=expenditureID)
        except Expenditure.DoesNotExist:
            expenditure = None
            return Response({'message': 'Expenditure not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            expenditure = None
            return Response({'message': 'Invalid expenditure ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(expenditure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # put
    @extend_schema(
        responses={status.HTTP_200_OK: UserExpenditureUpdateSerializer},
        summary="Update expenditure data by ID",
        methods=['put'],
        operation_id='updateExpenditureByID',
        tags=["expense"]
    )
    def put(self, request, expenditureID):
        try:
            expenditure = Expenditure.objects.get(pk=expenditureID)
        except Expenditure.DoesNotExist:
            expenditure = None
            return Response({'message': 'Expenditure not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            expenditure = None
            return Response({'message': 'Invalid expenditure ID'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        try:
            ser = UserExpenditureSerializer(expenditure, data=data, partial=True)
            if ser.is_valid():
                ser.save()
                resp = {
                    'category': ser.data['category'],
                    'nameOfItem': ser.data['nameOfItem'],
                    'estimatedAmount': ser.data['estimatedAmount'],
                }
                return Response(resp, status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response({'message': 'Invalid expenditure data'}, status=status.HTTP_400_BAD_REQUEST)


    # delete
    @extend_schema(
        parameters=[
            OpenApiParameter(name='expenditureID', description='The expenditureID that needs to be fetched', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses={status.HTTP_200_OK: UserExpenditureDeleteSchemaSerializer},
        summary="Delete expenditure data by ID",
        methods=['delete'],
        operation_id='deleteExpenditureByID',
        tags=["expense"]
    )
    def delete(self, request, expenditureID):
        try:
            expenditure = Expenditure.objects.get(pk=expenditureID)
        except Expenditure.DoesNotExist:
            expenditure = None
            return Response({'message': 'Expenditure not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            expenditure = None
            return Response({'message': 'Invalid expenditure ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expenditure.delete()
        except Exception:
            return Response({'message': 'Error deleting expenditure!'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Expenditure deleted successfully!'}, status=status.HTTP_200_OK)
        

