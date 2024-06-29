from datetime import timedelta, datetime
from django.utils.timezone import now
from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Advertisement, UserWallet, UserTransaction, Category
from .serializers import AdvertisementSerializer, UserWalletSerializer, UserTransactionSerializer, \
    CategorySerializer, AddBalanceSerializer


class AdvertisementListView(generics.ListAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdvertisementCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk  # Use pk which is a more generic way to get the primary key

        # Calculate budget or termination based on the limit choice
        limit = data.get('limit')
        if limit == 'jobs':
            data['terminate'] = (datetime.now().date() + timedelta(days=60)).isoformat()
            if 'budget' not in data:
                data['budget'] = float(data['per_job']) * 20  # Assuming a default number of 20 jobs if not provided
        elif limit == 'days':
            terminate = data.get('terminate')
            if terminate:
                terminate_date = datetime.strptime(terminate, '%Y-%m-%d').date()  # Convert string to datetime.date
                days = (terminate_date - datetime.now().date()).days
                data['budget'] = days * float(data['per_job'])
            else:
                return Response({"detail": "Termination date must be provided for days limit."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid limit choice."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertisementSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                user_wallet = UserWallet.objects.get(user=request.user)
                ad_budget = serializer.validated_data['budget']

                if user_wallet.balance >= ad_budget:
                    category_name = serializer.validated_data.pop('category_name', 'default')
                    category, created = Category.objects.get_or_create(name=category_name)

                    user_wallet.balance -= ad_budget
                    user_wallet.save()

                    advertisement = serializer.save(user=request.user, remaining_budget=ad_budget, category=category)
                    UserTransaction.objects.create(
                        user=request.user,
                        advertisement=advertisement,
                        transaction_type='spend',
                        amount=ad_budget,
                        status='approved'
                    )

                    response_data = {
                        "message": "Advertisement created successfully.",
                        "spend": ad_budget,
                        "remaining_balance": user_wallet.balance,
                        "ad_id": advertisement.id
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"detail": "Insufficient balance in wallet."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class AdvertisementListView(generics.ListAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmitProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            advertisement_id = request.data.get('advertisement_id')
            proof = request.data.get('proof')
            advertisement = Advertisement.objects.get(id=advertisement_id)
            if advertisement.status == 'active' and advertisement.remaining_budget >= advertisement.per_job:
                UserTransaction.objects.create(
                    user=request.user,
                    advertisement=advertisement,
                    transaction_type='earn',
                    amount=advertisement.per_job,
                    status='pending',
                    proof=proof  # Add proof field to UserTransaction model if necessary
                )
                return Response({"detail": "Proof submitted successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Advertisement is not active or insufficient budget."},
                            status=status.HTTP_400_BAD_REQUEST)


class SubmitProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            advertisement_id = request.data.get('advertisement_id')
            proof = request.data.get('proof')
            advertisement = Advertisement.objects.get(id=advertisement_id)
            if advertisement.status == 'active' and advertisement.remaining_budget >= advertisement.per_job:
                UserTransaction.objects.create(
                    user=request.user,
                    advertisement=advertisement,
                    transaction_type='earn',
                    amount=advertisement.per_job,
                    status='pending',
                    proof=proof  # Add proof field to UserTransaction model if necessary
                )
                return Response({"detail": "Proof submitted successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Advertisement is not active or insufficient budget."},
                            status=status.HTTP_400_BAD_REQUEST)


class ApproveSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, transaction_id):
        try:
            with transaction.atomic():
                user_transaction = UserTransaction.objects.get(
                    id=transaction_id,
                    advertisement__user=request.user,
                    status='pending',
                    transaction_type='earn'
                )

                user_transaction.status = 'approved'
                user_transaction.save()

                earner_wallet = UserWallet.objects.get(user=user_transaction.user)
                earner_wallet.balance += user_transaction.amount
                earner_wallet.save()

                advertisement = user_transaction.advertisement
                advertisement.remaining_budget -= user_transaction.amount
                advertisement.save()

                # Create a spend transaction for the advertiser
                UserTransaction.objects.create(
                    user=request.user,
                    advertisement=advertisement,
                    transaction_type='spend',
                    amount=user_transaction.amount,
                    status='approved'
                )

                if advertisement.remaining_budget <= 0:
                    advertisement.status = 'inactive'
                    advertisement.save()

                return Response({"detail": "Submission approved and spend transaction created."},
                                status=status.HTTP_200_OK)

        except UserTransaction.DoesNotExist:
            return Response({"detail": "Transaction not found or already approved."},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class AddBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddBalanceSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                amount = serializer.validated_data['amount']
                user_wallet = UserWallet.objects.get(user=request.user)
                user_wallet.balance += amount
                user_wallet.save()
                return Response({"detail": "Balance added successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvertisementsByCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, category_id):
        advertisements = Advertisement.objects.filter(category_id=category_id)
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisementSubmissionsView(generics.ListAPIView):
    serializer_class = UserTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        advertisement_id = self.kwargs['advertisement_id']
        return UserTransaction.objects.filter(
            advertisement_id=advertisement_id,
            advertisement__user=self.request.user,
            transaction_type='earn',
            status='pending'
        )
