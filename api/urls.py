from django.urls import path
from api.views import user, income, expenditure

urlpatterns = [

    # Auth
    path('auth/signup/',    user.RegistrationView.as_view(), name='signup'),
    path('auth/login/',     user.LoginView.as_view(), name='login'),
    path('auth/logout/',    user.LogoutAPIView.as_view(), name='logout'),
    path('auth/refresh/',   user.UserTokenRefreshView.as_view(), name='refresh'),
    path('auth/user/<str:userID>/profile/', user.UserProfileView.as_view(), name='user_profile'),

    # Income
    path('user/income/',                income.IncomeListCreateView.as_view(), name='list_create_incomes'),
    path('user/income/<str:incomeID>/', income.IncomeRetrieveUpdateDeleteView.as_view(), name='retrieve_get_update_delete_income'),

    # Expenditure
    path('user/expenditure/',                     expenditure.ExpenditureListCreateView.as_view(), name='list_create_expenditures'),
    path('user/expenditure/<str:expenditureID>/', expenditure.ExpenditureRetrieveUpdateDeleteView.as_view(), name='retrieve_get_update_delete_expenditure'),
]

