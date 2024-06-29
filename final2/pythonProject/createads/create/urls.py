from django.urls import path
from .views import (
    AdvertisementListView,
    AdvertisementCreateView,
    AddFundView,
    UserWalletView,
    UserTransactionListView,
    CategoryListView,
    SubmitProofView,
    ApproveSubmissionView,
    AddBalanceView,
    AdvertisementsByCategoryView,
    AdvertisementSubmissionsView
)

urlpatterns = [
    # Advertisement URLs
    path('advertisements/', AdvertisementListView.as_view(), name='advertisement-list'),
    path('advertisements/create/', AdvertisementCreateView.as_view(), name='advertisement-create'),
    path('advertisements/category/<int:category_id>/', AdvertisementsByCategoryView.as_view(), name='advertisements-by-category'),

    # Fund addition URL
    path('add-fund/', AddFundView.as_view(), name='add-fund'),

    # Wallet URLs
    path('wallet/', UserWalletView.as_view(), name='user-wallet'),

    # Transaction URLs
    path('transactions/', UserTransactionListView.as_view(), name='user-transaction-list'),
    path('transactions/<uuid:transaction_id>/approve/', ApproveSubmissionView.as_view(), name='approve-transaction'),

    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<pk>/', CategoryListView.as_view(), name='category-detail'),

    # Proof Submission and Approval URLs
    path('submit-proof/', SubmitProofView.as_view(), name='submit-proof'),

    # Add Balance URL
    path('add-balance/', AddBalanceView.as_view(), name='add-balance'),

    # View submissions for a specific advertisement
    path('advertisements/<uuid:advertisement_id>/submissions/', AdvertisementSubmissionsView.as_view(), name='advertisement-submissions'),
]
