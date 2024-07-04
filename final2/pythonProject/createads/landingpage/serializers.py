from rest_framework import serializers
from .models import AdminAdvertisement


class AdminAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAdvertisement
        fields = [
            'id',
            'title',
            'details',
            'discounts',
            'offers',
            'referral_code',
            'guidelines',
            'links',
            # 'thumbnail',
            'is_running',
            'duration',
            'priority',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
