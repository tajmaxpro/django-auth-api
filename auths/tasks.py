from celery import shared_task
import random, time
from django.core.cache import cache
from config import settings
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone


@shared_task
def generate_otp():
    return str(random.randint(100000, 999999))

def generate_and_store_otp(email):
    otp = generate_otp()
    curr_timestamp = int(time.time())
    cache_key = f"otp_{email}"
    cache.set(cache_key, {'otp': otp, 'timestamp': curr_timestamp})
    return otp

def send_otp_email(email, otp):
    subject = "OTP for your login"
    message = f"OTP for your login is: {otp}. This OTP is valid only for 2 minutes. So hurry to verify it out."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    