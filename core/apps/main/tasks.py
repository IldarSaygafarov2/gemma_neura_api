from core.project import celery_app

from django.core.mail import send_mail
from core.project import settings


@celery_app.task()
def send_contact_mail(name, email, message):
    return send_mail(
        subject="Сообщение из контактной формы",
        message=f"Имя: {name}\nПочта: {email}\nСообщение: {message}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
    )
