from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activation_link = reverse('verify_email', kwargs={'uid': uid, 'token': token})
    activation_url = f'{settings.FRONTEND_URL}{activation_link}'
    subject = 'Activate your account'
    message = f'Hi {user.username}, please click the link below to verify your email address: {activation_url}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
