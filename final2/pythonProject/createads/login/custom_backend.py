from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(user_id=user_id)
        except get_user_model().DoesNotExist:
            return None
