from django.core.mail import send_mail


def send_verification_email(user):
    user.generate_otp()
    subject = 'Your Verification Code'
    message = f'Your verification code is {user.otp}. It is valid for 10 minutes.'
    send_mail(subject, message, 'rimalasim24@gmail.com', [user.email])
