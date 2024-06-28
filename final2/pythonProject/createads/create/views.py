from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Advertisement, UserWallet, UserTransaction, Category
from .serializers import AdvertisementSerializer, UserWalletSerializer, UserTransactionSerializer, \
    CategorySerializer
from login.models import User


class AdvertisementListView(generics.ListCreateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Advertisement.objects.all()
        return Advertisement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            user_wallet = UserWallet.objects.get(user=self.request.user)
            ad_budget = serializer.validated_data['budget']
            if user_wallet.balance >= ad_budget:
                user_wallet.balance -= ad_budget
                user_wallet.save()
                serializer.save(user=self.request.user, remaining_budget=ad_budget)
                UserTransaction.objects.create(user=self.request.user, advertisement=serializer.instance,
                                               transaction_type='spend', amount=ad_budget, status='approved')
            else:
                raise serializers.ValidationError("Insufficient balance in wallet.")


class AddFundView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            advertisement_id = request.data.get('advertisement_id')
            amount = request.data.get('amount')
            advertisement = Advertisement.objects.get(id=advertisement_id)
            user_wallet = UserWallet.objects.get(user=request.user)
            if user_wallet.balance >= amount:
                user_wallet.balance -= amount
                user_wallet.save()
                advertisement.remaining_budget += amount
                advertisement.status = 'active'
                advertisement.save()
                UserTransaction.objects.create(user=request.user, advertisement=advertisement,
                                               transaction_type='spend', amount=amount, status='approved')
                return Response({"detail": "Funds added successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Insufficient balance in wallet."}, status=status.HTTP_400_BAD_REQUEST)


# Proof Submission and Approval Views

class SubmitProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            advertisement_id = request.data.get('advertisement_id')
            proof = request.data.get('proof')
            advertisement = Advertisement.objects.get(id=advertisement_id)
            if advertisement.remaining_budget >= advertisement.per_job:
                transaction = UserTransaction.objects.create(user=request.user, advertisement=advertisement,
                                                             transaction_type='earn', amount=advertisement.per_job,
                                                             status='pending')
                # Store the proof in the appropriate model or field
                # proof.save() or similar logic
                return Response({"detail": "Proof submitted successfully, pending approval."},
                                status=status.HTTP_200_OK)
            return Response({"detail": "Insufficient remaining budget."}, status=status.HTTP_400_BAD_REQUEST)


class ApproveSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        with transaction.atomic():
            transaction_id = request.data.get('transaction_id')
            transaction = UserTransaction.objects.get(id=transaction_id, advertisement__user=request.user,
                                                      status='pending')
            if transaction:
                transaction.status = 'approved'
                transaction.save()
                earner_wallet = UserWallet.objects.get(user=transaction.user)
                earner_wallet.balance += transaction.amount
                earner_wallet.save()
                advertisement = transaction.advertisement
                advertisement.remaining_budget -= transaction.amount
                advertisement.save()
                if advertisement.remaining_budget <= 0:
                    advertisement.status = 'inactive'
                    advertisement.save()
                return Response({"detail": "Submission approved."}, status=status.HTTP_200_OK)
            return Response({"detail": "Submission already approved or invalid."}, status=status.HTTP_400_BAD_REQUEST)


# Wallet, Transaction, and Category Views

class UserWalletView(generics.RetrieveAPIView):
    queryset = UserWallet.objects.all()
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserWallet.objects.get(user=self.request.user)


class UserTransactionListView(generics.ListAPIView):
    serializer_class = UserTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserTransaction.objects.all()
        return UserTransaction.objects.filter(user=self.request.user)


class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
