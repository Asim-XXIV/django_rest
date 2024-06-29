from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
    user.generate_otp()
    subject = 'Your Verification Code'
    message = f'Your verification code is {user.otp}. It is valid for 10 minutes.'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [user.email])
