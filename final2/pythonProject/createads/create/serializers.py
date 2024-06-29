from rest_framework import serializers
from .models import Advertisement, UserWallet, UserTransaction, Category
from django.contrib.auth.models import AbstractUser


class AdvertisementSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Advertisement
        fields = '__all__'
        read_only_fields = ['id', 'user', 'remaining_budget', 'status']

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
        else:
            category, created = Category.objects.get_or_create(name='default')
        validated_data['category'] = category
        validated_data['remaining_budget'] = validated_data['budget']
        return super().create(validated_data)


class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = '__all__'


class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ['user_id', 'email', 'username', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class AddBalanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
