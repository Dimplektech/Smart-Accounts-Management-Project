from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


app_name = 'accounts'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Transaction URLs
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('add-transaction/', views.add_transaction_view, name='add_transaction'),

    # Account URLs
    path('accounts/', views.account_list_view, name='account_list'),
    path('add-account/', views.add_account, name='add_account'),
    path('account/<int:account_id>/', views.account_detail_view, name='account_detail'),

    # Budget URLs
    path('budgets/', views.budget_list_view, name='budget_list'),
    path('add-budget/', views.add_budget_view, name='add_budget'),

    # Reports URLs
    path('reports/', views.reports_view, name='reports'),
]
