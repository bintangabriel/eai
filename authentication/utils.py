from django.core.mail import EmailMessage
import threading
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
import os
import string
import random

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        EmailThread(email).start()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "https://lumba-ai-testing.vercel.app/reset-password?token={}".format(reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="LumbaAI"),
        # message:
        email_plaintext_message,
        # from:
        "lumbaaidev@gmail.com",
        # to:
        [reset_password_token.user.email]
    )

def generate_image_name(image_name):
    file, ext = os.path.splitext(image_name)
    new_file_name = file + "_" + random_string() + ext
    return new_file_name

def random_string(length=4):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))