from django.urls import path
from .views import (
    AdvertisementListView,
    AddFundView,
    UserWalletView,
    UserTransactionListView,
    CategoryListView,
    SubmitProofView,
    ApproveSubmissionView
)

urlpatterns = [
    # Advertisement, Wallet, Transactions, and Categories
    path('advertisements/', AdvertisementListView.as_view(), name='advertisements'),
    path('add-fund/', AddFundView.as_view(), name='add-fund'),
    path('wallet/', UserWalletView.as_view(), name='wallet'),
    path('transactions/', UserTransactionListView.as_view(), name='transactions'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/<pk>/', CategoryListView.as_view(), name='category-detail'),
    path('submit-proof/', SubmitProofView.as_view(), name='submit-proof'),
    path('approve-submission/', ApproveSubmissionView.as_view(), name='approve-submission'),
]
